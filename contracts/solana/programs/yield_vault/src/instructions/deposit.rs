use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, MintTo, Token, TokenAccount, Transfer};

use crate::constants::*;
use crate::error::VaultError;
use crate::events::Deposited;
use crate::state::VaultState;
use crate::utils::calculate_shares_to_mint;

#[derive(Accounts)]
pub struct Deposit<'info> {
    /// The user depositing tokens
    #[account(mut)]
    pub user: Signer<'info>,

    /// The vault state
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    /// The vault's token account (receives deposited tokens)
    #[account(
        mut,
        seeds = [VAULT_TOKEN_SEED, vault.key().as_ref()],
        bump = vault.token_account_bump,
        token::mint = vault.mint,
        token::authority = vault,
    )]
    pub vault_token_account: Account<'info, TokenAccount>,

    /// The share token mint (vault mints shares to depositor)
    #[account(
        mut,
        seeds = [SHARE_MINT_SEED, vault.key().as_ref()],
        bump = vault.share_mint_bump,
        mint::authority = vault,
    )]
    pub share_mint: Account<'info, Mint>,

    /// The user's token account for the underlying asset
    #[account(
        mut,
        token::mint = vault.mint,
        token::authority = user,
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    /// The user's token account for vault shares (receives minted shares)
    #[account(
        mut,
        token::mint = share_mint,
        token::authority = user,
    )]
    pub user_share_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<Deposit>, amount: u64) -> Result<()> {
    let vault = &ctx.accounts.vault;

    // Validation
    require!(!vault.paused, VaultError::VaultPaused);
    require!(amount > 0, VaultError::InvalidAmount);
    require!(amount >= vault.min_deposit, VaultError::BelowMinDeposit);

    if vault.deposit_cap > 0 {
        let new_total = vault
            .total_assets
            .checked_add(amount)
            .ok_or(VaultError::ArithmeticOverflow)?;
        require!(new_total <= vault.deposit_cap, VaultError::DepositCapExceeded);
    }

    // Calculate shares to mint
    let shares_to_mint =
        calculate_shares_to_mint(amount, vault.total_assets, vault.total_shares)?;
    require!(shares_to_mint > 0, VaultError::InvalidAmount);

    // Transfer underlying tokens from user to vault
    token::transfer(
        CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.user_token_account.to_account_info(),
                to: ctx.accounts.vault_token_account.to_account_info(),
                authority: ctx.accounts.user.to_account_info(),
            },
        ),
        amount,
    )?;

    // Mint share tokens to user (vault PDA signs as mint authority)
    let mint_key = ctx.accounts.vault.mint;
    let owner_key = ctx.accounts.vault.owner;
    let vault_bump = ctx.accounts.vault.bump;
    let signer_seeds: &[&[&[u8]]] = &[&[
        VAULT_SEED,
        mint_key.as_ref(),
        owner_key.as_ref(),
        &[vault_bump],
    ]];

    token::mint_to(
        CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            MintTo {
                mint: ctx.accounts.share_mint.to_account_info(),
                to: ctx.accounts.user_share_account.to_account_info(),
                authority: ctx.accounts.vault.to_account_info(),
            },
            signer_seeds,
        ),
        shares_to_mint,
    )?;

    // Update vault state
    let vault = &mut ctx.accounts.vault;
    vault.total_assets = vault
        .total_assets
        .checked_add(amount)
        .ok_or(VaultError::ArithmeticOverflow)?;
    vault.total_shares = vault
        .total_shares
        .checked_add(shares_to_mint)
        .ok_or(VaultError::ArithmeticOverflow)?;

    emit!(Deposited {
        vault: vault.key(),
        user: ctx.accounts.user.key(),
        amount,
        shares_minted: shares_to_mint,
    });

    Ok(())
}
