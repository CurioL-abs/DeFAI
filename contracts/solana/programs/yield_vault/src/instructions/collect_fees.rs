use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, MintTo, Token, TokenAccount};

use crate::constants::*;
use crate::error::VaultError;
use crate::events::FeesCollected;
use crate::state::VaultState;
use crate::utils::fee_amount_to_shares;

#[derive(Accounts)]
pub struct CollectFees<'info> {
    /// The vault owner collecting fees
    pub owner: Signer<'info>,

    /// The vault state
    #[account(
        mut,
        seeds = [VAULT_SEED, vault.mint.as_ref(), vault.owner.as_ref()],
        bump = vault.bump,
        has_one = owner @ VaultError::Unauthorized,
    )]
    pub vault: Box<Account<'info, VaultState>>,

    /// The share token mint (fee shares are minted)
    #[account(
        mut,
        seeds = [SHARE_MINT_SEED, vault.key().as_ref()],
        bump = vault.share_mint_bump,
        mint::authority = vault,
    )]
    pub share_mint: Account<'info, Mint>,

    /// The treasury's share token account (receives fee shares)
    #[account(
        mut,
        token::mint = share_mint,
    )]
    pub treasury_share_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<CollectFees>) -> Result<()> {
    let vault = &ctx.accounts.vault;

    require!(vault.accrued_management_fee > 0, VaultError::NoFeesToCollect);

    let fee_amount = vault.accrued_management_fee;

    // Convert fee amount to shares (dilutive minting)
    let fee_shares = fee_amount_to_shares(fee_amount, vault.total_assets, vault.total_shares)?;

    if fee_shares > 0 {
        // Mint fee shares to treasury (vault PDA signs)
        let mint_key = vault.mint;
        let owner_key = vault.owner;
        let vault_bump = vault.bump;
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
                    to: ctx.accounts.treasury_share_account.to_account_info(),
                    authority: ctx.accounts.vault.to_account_info(),
                },
                signer_seeds,
            ),
            fee_shares,
        )?;
    }

    // Update vault state
    let vault = &mut ctx.accounts.vault;
    vault.total_shares = vault
        .total_shares
        .checked_add(fee_shares)
        .ok_or(VaultError::ArithmeticOverflow)?;
    vault.accrued_management_fee = 0;

    emit!(FeesCollected {
        vault: vault.key(),
        fee_shares_minted: fee_shares,
        fee_amount,
    });

    Ok(())
}
