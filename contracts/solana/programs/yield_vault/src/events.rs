use anchor_lang::prelude::*;

#[event]
pub struct VaultInitialized {
    pub vault: Pubkey,
    pub mint: Pubkey,
    pub owner: Pubkey,
    pub deposit_cap: u64,
    pub management_fee_bps: u16,
    pub performance_fee_bps: u16,
}

#[event]
pub struct Deposited {
    pub vault: Pubkey,
    pub user: Pubkey,
    pub amount: u64,
    pub shares_minted: u64,
}

#[event]
pub struct Withdrawn {
    pub vault: Pubkey,
    pub user: Pubkey,
    pub shares_burned: u64,
    pub amount_returned: u64,
}

#[event]
pub struct NavUpdated {
    pub vault: Pubkey,
    pub old_total_assets: u64,
    pub new_total_assets: u64,
    pub manager: Pubkey,
}

#[event]
pub struct FeesCollected {
    pub vault: Pubkey,
    pub fee_shares_minted: u64,
    pub fee_amount: u64,
}

#[event]
pub struct VaultPausedEvent {
    pub vault: Pubkey,
}

#[event]
pub struct VaultUnpausedEvent {
    pub vault: Pubkey,
}

#[event]
pub struct ManagerAdded {
    pub vault: Pubkey,
    pub manager: Pubkey,
}

#[event]
pub struct ManagerRemoved {
    pub vault: Pubkey,
    pub manager: Pubkey,
}

#[event]
pub struct ConfigUpdated {
    pub vault: Pubkey,
    pub deposit_cap: u64,
    pub min_deposit: u64,
    pub management_fee_bps: u16,
    pub performance_fee_bps: u16,
}
