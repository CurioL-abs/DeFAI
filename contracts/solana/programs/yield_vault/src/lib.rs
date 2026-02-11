use anchor_lang::prelude::*;

pub mod constants;
pub mod error;
pub mod events;
pub mod instructions;
pub mod state;
pub mod utils;

use instructions::*;

declare_id!("VLT1111111111111111111111111111111111111111");

#[program]
pub mod yield_vault {
    use super::*;

    /// Step 1 of vault initialization: create the vault state PDA.
    pub fn create_vault(
        ctx: Context<CreateVault>,
        params: InitializeVaultParams,
    ) -> Result<()> {
        instructions::initialize::handle_create_vault(ctx, params)
    }

    /// Step 2 of vault initialization: create share mint and vault token account PDAs.
    pub fn init_vault_accounts(ctx: Context<InitVaultAccounts>) -> Result<()> {
        instructions::initialize::handle_init_vault_accounts(ctx)
    }

    /// Deposit underlying tokens into the vault and receive share tokens.
    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        instructions::deposit::handler(ctx, amount)
    }

    /// Burn share tokens and withdraw underlying tokens from the vault.
    pub fn withdraw(ctx: Context<Withdraw>, shares: u64) -> Result<()> {
        instructions::withdraw::handler(ctx, shares)
    }

    /// Update the vault's net asset value. Only callable by owner or authorized manager.
    /// Accrues management and performance fees automatically.
    pub fn update_nav(ctx: Context<UpdateNav>, new_total_assets: u64) -> Result<()> {
        instructions::update_nav::handler(ctx, new_total_assets)
    }

    /// Collect accrued fees by minting new share tokens to the treasury.
    /// Only callable by the vault owner.
    pub fn collect_fees(ctx: Context<CollectFees>) -> Result<()> {
        instructions::collect_fees::handler(ctx)
    }

    /// Pause the vault — disables deposits and withdrawals. Owner only.
    pub fn pause(ctx: Context<Pause>) -> Result<()> {
        instructions::admin::handle_pause(ctx)
    }

    /// Unpause the vault — re-enables deposits and withdrawals. Owner only.
    pub fn unpause(ctx: Context<Unpause>) -> Result<()> {
        instructions::admin::handle_unpause(ctx)
    }

    /// Update vault configuration parameters. Owner only.
    pub fn update_config(ctx: Context<UpdateConfig>, params: UpdateConfigParams) -> Result<()> {
        instructions::admin::handle_update_config(ctx, params)
    }

    /// Add an authorized manager to the vault. Owner only.
    pub fn add_manager(ctx: Context<AddManager>, manager: Pubkey) -> Result<()> {
        instructions::admin::handle_add_manager(ctx, manager)
    }

    /// Remove an authorized manager from the vault. Owner only.
    pub fn remove_manager(ctx: Context<RemoveManager>, manager: Pubkey) -> Result<()> {
        instructions::admin::handle_remove_manager(ctx, manager)
    }

    /// Close an empty vault and reclaim all rent. Owner only.
    pub fn close_vault(ctx: Context<CloseVault>) -> Result<()> {
        instructions::close::handler(ctx)
    }
}
