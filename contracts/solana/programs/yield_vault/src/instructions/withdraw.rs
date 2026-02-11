use anchor_lang::prelude::*;
use anchor_spl::token::{self, Burn, Mint, Token, TokenAccount, Transfer};

use crate::constants::*;
use crate::error::VaultError;
use crate::events::Withdrawn;
use crate::state::VaultState;
use crate::utils::calculate_assets_to_return;

#[derive(Accounts)]
pub struct Withdraw<'info> {
    /// The user withdrawing tokens
    #[account(mut)]
    pub user: Signer<'info>,

    /// The vault state
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    /// The vault's token account (sends underlying tokens to user)
    #[account(
        mut,
        seeds = [VAULT_TOKEN_SEED, vault.key().as_ref()],
        bump = vault.token_account_bump,
        token::mint = vault.mint,
        token::authority = vault,
    )]
    pub vault_token_account: Account<'info, TokenAccount>,

    /// The share token mint (shares are burned on withdrawal)
    #[account(
        mut,
        seeds = [SHARE_MINT_SEED, vault.key().as_ref()],
        bump = vault.share_mint_bump,
        mint::authority = vault,
    )]
    pub share_mint: Account<'info, Mint>,

    /// The user's token account for the underlying asset (receives withdrawn tokens)
    #[account(
        mut,
        token::mint = vault.mint,
        token::authority = user,
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    /// The user's share token account (shares are burned from here)
    #[account(
        mut,
        token::mint = share_mint,
        token::authority = user,
    )]
    pub user_share_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<Withdraw>, shares: u64) -> Result<()> {
    let vault = &ctx.accounts.vault;

    // Validation
    require!(!vault.paused, VaultError::VaultPaused);
    require!(shares > 0, VaultError::InvalidAmount);
    require!(
        ctx.accounts.user_share_account.amount >= shares,
        VaultError::InsufficientShares
    );

    // Calculate assets to return
    let assets_to_return =
        calculate_assets_to_return(shares, vault.total_assets, vault.total_shares)?;
    require!(assets_to_return > 0, VaultError::InvalidAmount);

    // Check vault has enough liquid assets
    require!(
        ctx.accounts.vault_token_account.amount >= assets_to_return,
        VaultError::InsufficientAssets
    );

    // Burn user's share tokens (user signs as authority over their token account)
    token::burn(
        CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Burn {
                mint: ctx.accounts.share_mint.to_account_info(),
                from: ctx.accounts.user_share_account.to_account_info(),
                authority: ctx.accounts.user.to_account_info(),
            },
        ),
        shares,
    )?;

    // Transfer underlying tokens from vault to user (vault PDA signs)
    let mint_key = ctx.accounts.vault.mint;
    let owner_key = ctx.accounts.vault.owner;
    let vault_bump = ctx.accounts.vault.bump;
    let signer_seeds: &[&[&[u8]]] = &[&[
        VAULT_SEED,
        mint_key.as_ref(),
        owner_key.as_ref(),
        &[vault_bump],
    ]];

    token::transfer(
        CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault_token_account.to_account_info(),
                to: ctx.accounts.user_token_account.to_account_info(),
                authority: ctx.accounts.vault.to_account_info(),
            },
            signer_seeds,
        ),
        assets_to_return,
    )?;

    // Update vault state
    let vault = &mut ctx.accounts.vault;
    vault.total_assets = vault
        .total_assets
        .checked_sub(assets_to_return)
        .ok_or(VaultError::ArithmeticOverflow)?;
    vault.total_shares = vault
        .total_shares
        .checked_sub(shares)
        .ok_or(VaultError::ArithmeticOverflow)?;

    emit!(Withdrawn {
        vault: vault.key(),
        user: ctx.accounts.user.key(),
        shares_burned: shares,
        amount_returned: assets_to_return,
    });

    Ok(())
}
