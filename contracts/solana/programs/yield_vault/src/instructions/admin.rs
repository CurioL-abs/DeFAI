use anchor_lang::prelude::*;

use crate::constants::*;
use crate::error::VaultError;
use crate::events::{
    ConfigUpdated, ManagerAdded, ManagerRemoved, VaultPausedEvent, VaultUnpausedEvent,
};
use crate::state::VaultState;

// ──────────────────────────────────────────
// Pause
// ──────────────────────────────────────────

#[derive(Accounts)]
pub struct Pause<'info> {
    pub owner: Signer<'info>,

    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handle_pause(ctx: Context<Pause>) -> Result<()> {
    ctx.accounts.vault.paused = true;
    emit!(VaultPausedEvent {
        vault: ctx.accounts.vault.key(),
    });
    Ok(())
}

// ──────────────────────────────────────────
// Unpause
// ──────────────────────────────────────────

#[derive(Accounts)]
pub struct Unpause<'info> {
    pub owner: Signer<'info>,

    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handle_unpause(ctx: Context<Unpause>) -> Result<()> {
    ctx.accounts.vault.paused = false;
    emit!(VaultUnpausedEvent {
        vault: ctx.accounts.vault.key(),
    });
    Ok(())
}

// ──────────────────────────────────────────
// Update Config
// ──────────────────────────────────────────

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct UpdateConfigParams {
    pub deposit_cap: u64,
    pub min_deposit: u64,
    pub management_fee_bps: u16,
    pub performance_fee_bps: u16,
}

#[derive(Accounts)]
pub struct UpdateConfig<'info> {
    pub owner: Signer<'info>,

    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handle_update_config(ctx: Context<UpdateConfig>, params: UpdateConfigParams) -> Result<()> {
    require!(
        params.management_fee_bps <= MAX_FEE_BPS,
        VaultError::InvalidFeeConfig
    );
    require!(
        params.performance_fee_bps <= MAX_FEE_BPS,
        VaultError::InvalidFeeConfig
    );

    let vault = &mut ctx.accounts.vault;
    vault.deposit_cap = params.deposit_cap;
    vault.min_deposit = params.min_deposit;
    vault.management_fee_bps = params.management_fee_bps;
    vault.performance_fee_bps = params.performance_fee_bps;

    emit!(ConfigUpdated {
        vault: vault.key(),
        deposit_cap: params.deposit_cap,
        min_deposit: params.min_deposit,
        management_fee_bps: params.management_fee_bps,
        performance_fee_bps: params.performance_fee_bps,
    });

    Ok(())
}

// ──────────────────────────────────────────
// Add Manager
// ──────────────────────────────────────────

#[derive(Accounts)]
pub struct AddManager<'info> {
    pub owner: Signer<'info>,

    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handle_add_manager(ctx: Context<AddManager>, manager: Pubkey) -> Result<()> {
    ctx.accounts.vault.add_manager(manager)?;

    emit!(ManagerAdded {
        vault: ctx.accounts.vault.key(),
        manager,
    });

    Ok(())
}

// ──────────────────────────────────────────
// Remove Manager
// ──────────────────────────────────────────

#[derive(Accounts)]
pub struct RemoveManager<'info> {
    pub owner: Signer<'info>,

    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,
}

pub fn handle_remove_manager(ctx: Context<RemoveManager>, manager: Pubkey) -> Result<()> {
    ctx.accounts.vault.remove_manager(manager)?;

    emit!(ManagerRemoved {
        vault: ctx.accounts.vault.key(),
        manager,
    });

    Ok(())
}
