use anchor_lang::prelude::*;

use crate::constants::MAX_MANAGERS;
use crate::error::VaultError;

#[account]
pub struct VaultState {
    /// Vault owner / admin — can change config, pause, manage managers
    pub owner: Pubkey,
    /// Underlying token mint (e.g. USDC, SOL, etc.)
    pub mint: Pubkey,
    // Note: share_mint and vault_token_account are derived via PDA seeds,
    // so we don't store them — saves 64 bytes for BPF stack compliance.

    /// Total assets under management (in vault + deployed to strategies)
    pub total_assets: u64,
    /// Total outstanding share tokens
    pub total_shares: u64,

    /// Maximum total deposits allowed (0 = unlimited)
    pub deposit_cap: u64,
    /// Minimum deposit amount per transaction
    pub min_deposit: u64,

    /// Annual management fee in basis points (e.g. 200 = 2%)
    pub management_fee_bps: u16,
    /// Performance fee in basis points on profits above high-water mark
    pub performance_fee_bps: u16,

    /// High-water mark for performance fee calculation (per-share basis)
    pub high_water_mark: u64,
    /// Last time fees were collected (unix timestamp)
    pub last_fee_collection: i64,
    /// Accumulated management fees not yet collected (in asset units)
    pub accrued_management_fee: u64,

    /// Authorized managers (agents) who can execute strategies and update NAV
    pub managers: [Pubkey; MAX_MANAGERS],
    /// Current number of active managers
    pub manager_count: u8,

    /// Whether the vault is paused (deposits/withdrawals disabled)
    pub paused: bool,

    /// PDA bump seeds
    pub bump: u8,
    pub share_mint_bump: u8,
    pub token_account_bump: u8,
}

impl VaultState {
    /// Account discriminator (8) + all fields
    /// 32 + 32 + 8 + 8 + 8 + 8 + 2 + 2 + 8 + 8 + 8 + (32*3) + 1 + 1 + 1 + 1 + 1 = 225
    pub const LEN: usize = 8 + 225;

    /// Check if a pubkey is an authorized manager
    pub fn is_manager(&self, key: &Pubkey) -> bool {
        for i in 0..self.manager_count as usize {
            if self.managers[i] == *key {
                return true;
            }
        }
        false
    }

    /// Check if a pubkey is the owner or an authorized manager
    pub fn is_authority(&self, key: &Pubkey) -> bool {
        self.owner == *key || self.is_manager(key)
    }

    /// Add a new manager to the vault
    pub fn add_manager(&mut self, key: Pubkey) -> Result<()> {
        require!(
            (self.manager_count as usize) < MAX_MANAGERS,
            VaultError::MaxManagersReached
        );
        require!(!self.is_manager(&key), VaultError::ManagerAlreadyExists);

        self.managers[self.manager_count as usize] = key;
        self.manager_count += 1;
        Ok(())
    }

    /// Remove a manager from the vault (swap-remove for gas efficiency)
    pub fn remove_manager(&mut self, key: Pubkey) -> Result<()> {
        let mut found = false;
        for i in 0..self.manager_count as usize {
            if self.managers[i] == key {
                // Swap with last element and decrement count
                let last_idx = (self.manager_count - 1) as usize;
                self.managers[i] = self.managers[last_idx];
                self.managers[last_idx] = Pubkey::default();
                self.manager_count -= 1;
                found = true;
                break;
            }
        }
        require!(found, VaultError::ManagerNotFound);
        Ok(())
    }
}
