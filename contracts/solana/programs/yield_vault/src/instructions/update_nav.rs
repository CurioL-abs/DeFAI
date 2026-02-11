use anchor_lang::prelude::*;

use crate::constants::*;
use crate::error::VaultError;
use crate::events::NavUpdated;
use crate::state::VaultState;
use crate::utils::{calculate_management_fee, calculate_performance_fee};

#[derive(Accounts)]
pub struct UpdateNav<'info> {
    /// The manager or owner updating the NAV
    pub authority: Signer<'info>,

    /// The vault state
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handler(ctx: Context<UpdateNav>, new_total_assets: u64) -> Result<()> {
    let vault = &mut ctx.accounts.vault;
    let authority_key = ctx.accounts.authority.key();

    // Only owner or authorized manager can update NAV
    require!(vault.is_authority(&authority_key), VaultError::Unauthorized);

    let clock = Clock::get()?;
    let old_total_assets = vault.total_assets;

    // Accrue management fees based on time elapsed
    let seconds_elapsed = clock
        .unix_timestamp
        .checked_sub(vault.last_fee_collection)
        .ok_or(VaultError::ArithmeticOverflow)?;

    let mgmt_fee = calculate_management_fee(
        vault.total_assets,
        vault.management_fee_bps,
        seconds_elapsed,
    )?;

    vault.accrued_management_fee = vault
        .accrued_management_fee
        .checked_add(mgmt_fee)
        .ok_or(VaultError::ArithmeticOverflow)?;

    // Calculate performance fee if NAV increased above high-water mark
    let (perf_fee, new_hwm) = calculate_performance_fee(
        new_total_assets,
        vault.high_water_mark,
        vault.performance_fee_bps,
        vault.total_shares,
    )?;

    if perf_fee > 0 {
        vault.accrued_management_fee = vault
            .accrued_management_fee
            .checked_add(perf_fee)
            .ok_or(VaultError::ArithmeticOverflow)?;
    }

    // Update state
    vault.total_assets = new_total_assets;
    vault.high_water_mark = new_hwm;
    vault.last_fee_collection = clock.unix_timestamp;

    emit!(NavUpdated {
        vault: vault.key(),
        old_total_assets,
        new_total_assets,
        manager: authority_key,
    });

    Ok(())
}
