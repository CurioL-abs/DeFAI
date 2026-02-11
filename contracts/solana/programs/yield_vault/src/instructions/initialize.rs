use anchor_lang::prelude::*;
use anchor_spl::token::{Mint, Token, TokenAccount};

use crate::constants::*;
use crate::error::VaultError;
use crate::events::VaultInitialized;
use crate::state::VaultState;

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct InitializeVaultParams {
    pub deposit_cap: u64,
    pub min_deposit: u64,
    pub management_fee_bps: u16,
    pub performance_fee_bps: u16,
}

// ── Step 1: Create the vault state PDA only ──────────────────────────────────

#[derive(Accounts)]
pub struct CreateVault<'info> {
    /// The vault owner who is creating this vault
    #[account(mut)]
    pub owner: Signer<'info>,

    /// The underlying token mint this vault accepts
    pub mint: Box<Account<'info, Mint>>,

    /// The vault state account (PDA)
    #[account(
        init,
        payer = owner,
        space = VaultState::LEN,
        seeds = [VAULT_SEED, mint.key().as_ref(), owner.key().as_ref()],
        bump,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    pub system_program: Program<'info, System>,
}

pub fn handle_create_vault(
    ctx: Context<CreateVault>,
    params: InitializeVaultParams,
) -> Result<()> {
    require!(
        params.management_fee_bps <= MAX_FEE_BPS,
        VaultError::InvalidFeeConfig
    );
    require!(
        params.performance_fee_bps <= MAX_FEE_BPS,
        VaultError::InvalidFeeConfig
    );

    let vault = &mut ctx.accounts.vault;
    let clock = Clock::get()?;

    vault.owner = ctx.accounts.owner.key();
    vault.mint = ctx.accounts.mint.key();

    vault.total_assets = 0;
    vault.total_shares = 0;

    vault.deposit_cap = params.deposit_cap;
    vault.min_deposit = params.min_deposit;

    vault.management_fee_bps = params.management_fee_bps;
    vault.performance_fee_bps = params.performance_fee_bps;
    vault.high_water_mark = 0;
    vault.last_fee_collection = clock.unix_timestamp;
    vault.accrued_management_fee = 0;

    vault.managers = [Pubkey::default(); MAX_MANAGERS];
    vault.manager_count = 0;

    vault.paused = false;

    vault.bump = ctx.bumps.vault;
    // These will be set in init_vault_accounts
    vault.share_mint_bump = 0;
    vault.token_account_bump = 0;

    Ok(())
}

// ── Step 2: Create share mint and vault token account PDAs ───────────────────

#[derive(Accounts)]
pub struct InitVaultAccounts<'info> {
    /// The vault owner (must match vault.owner)
    #[account(mut)]
    pub owner: Signer<'info>,

    /// The underlying token mint (must match vault.mint)
    #[account(address = vault.mint)]
    pub mint: Box<Account<'info, Mint>>,

    /// The vault state — must already exist
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    /// The share token mint (PDA) — vault issues these to depositors
    #[account(
        init,
        payer = owner,
        seeds = [SHARE_MINT_SEED, vault.key().as_ref()],
        bump,
        mint::decimals = mint.decimals,
        mint::authority = vault,
    )]
    pub share_mint: Box<Account<'info, Mint>>,

    /// The vault's token account (PDA) — holds the underlying assets
    #[account(
        init,
        payer = owner,
        seeds = [VAULT_TOKEN_SEED, vault.key().as_ref()],
        bump,
        token::mint = mint,
        token::authority = vault,
    )]
    pub vault_token_account: Box<Account<'info, TokenAccount>>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

pub fn handle_init_vault_accounts(ctx: Context<InitVaultAccounts>) -> Result<()> {
    let vault = &mut ctx.accounts.vault;

    vault.share_mint_bump = ctx.bumps.share_mint;
    vault.token_account_bump = ctx.bumps.vault_token_account;

    emit!(VaultInitialized {
        vault: vault.key(),
        mint: ctx.accounts.mint.key(),
        owner: ctx.accounts.owner.key(),
        deposit_cap: vault.deposit_cap,
        management_fee_bps: vault.management_fee_bps,
        performance_fee_bps: vault.performance_fee_bps,
    });

    Ok(())
}
