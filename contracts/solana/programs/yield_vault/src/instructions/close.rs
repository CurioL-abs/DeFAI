use anchor_lang::prelude::*;
use anchor_spl::token::{CloseAccount, Mint, Token, TokenAccount, self};

use crate::constants::*;
use crate::error::VaultError;
use crate::state::VaultState;

#[derive(Accounts)]
pub struct CloseVault<'info> {
    /// The vault owner closing the vault
    #[account(mut)]
    pub owner: Signer<'info>,

    /// The vault state — will be closed and rent returned to owner
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
        close = owner,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    /// The vault's token account — will be closed
    #[account(
        mut,
        seeds = [VAULT_TOKEN_SEED, vault.key().as_ref()],
        bump = vault.token_account_bump,
        token::mint = vault.mint,
        token::authority = vault,
    )]
    pub vault_token_account: Account<'info, TokenAccount>,

    /// The share mint — will be closed
    #[account(
        mut,
        seeds = [SHARE_MINT_SEED, vault.key().as_ref()],
        bump = vault.share_mint_bump,
        mint::authority = vault,
    )]
    pub share_mint: Account<'info, Mint>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<CloseVault>) -> Result<()> {
    let vault = &ctx.accounts.vault;

    // Vault must be completely empty
    require!(vault.total_shares == 0, VaultError::VaultNotEmpty);
    require!(vault.total_assets == 0, VaultError::VaultNotEmpty);
    require!(
        ctx.accounts.vault_token_account.amount == 0,
        VaultError::VaultNotEmpty
    );

    let mint_key = vault.mint;
    let owner_key = vault.owner;
    let vault_bump = vault.bump;
    let signer_seeds: &[&[&[u8]]] = &[&[
        VAULT_SEED,
        mint_key.as_ref(),
        owner_key.as_ref(),
        &[vault_bump],
    ]];

    // Close vault token account — return rent to owner
    token::close_account(CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        CloseAccount {
            account: ctx.accounts.vault_token_account.to_account_info(),
            destination: ctx.accounts.owner.to_account_info(),
            authority: ctx.accounts.vault.to_account_info(),
        },
        signer_seeds,
    ))?;

    // Close share mint — return rent to owner
    token::close_account(CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        CloseAccount {
            account: ctx.accounts.share_mint.to_account_info(),
            destination: ctx.accounts.owner.to_account_info(),
            authority: ctx.accounts.vault.to_account_info(),
        },
        signer_seeds,
    ))?;

    // Vault state account is closed via `close = owner` constraint

    Ok(())
}
