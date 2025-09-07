use anchor_lang::prelude::*;

declare_id!("Demo111111111111111111111111111111111111111");

#[program]
pub mod yield_vault {
    use super::*;

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        let vault = &mut ctx.accounts.vault;
        vault.total_assets = vault.total_assets.checked_add(amount).unwrap();
        Ok(())
    }

    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        let vault = &mut ctx.accounts.vault;
        if vault.total_assets < amount {
            return Err(error!(ErrorCode::InsufficientFunds));
        }
        vault.total_assets = vault.total_assets.checked_sub(amount).unwrap();
        Ok(())
    }
}

#[account]
pub struct Vault {
    pub total_assets: u64,
}

#[derive(Accounts)]
pub struct Deposit<'info> {
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Not enough assets")]
    InsufficientFunds,
}
