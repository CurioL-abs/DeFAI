use anchor_lang::prelude::*;

#[error_code]
pub enum VaultError {
    #[msg("Vault is currently paused")]
    VaultPaused,

    #[msg("Deposit amount must be greater than zero")]
    InvalidAmount,

    #[msg("Deposit would exceed the vault's deposit cap")]
    DepositCapExceeded,

    #[msg("Deposit amount is below the minimum required")]
    BelowMinDeposit,

    #[msg("Insufficient shares for withdrawal")]
    InsufficientShares,

    #[msg("Arithmetic overflow or underflow")]
    ArithmeticOverflow,

    #[msg("Caller is not authorized for this operation")]
    Unauthorized,

    #[msg("Maximum number of managers reached")]
    MaxManagersReached,

    #[msg("Manager not found in the manager list")]
    ManagerNotFound,

    #[msg("Manager already exists in the manager list")]
    ManagerAlreadyExists,

    #[msg("Vault must be empty (zero shares and assets) to close")]
    VaultNotEmpty,

    #[msg("Fee basis points exceed the maximum allowed")]
    InvalidFeeConfig,

    #[msg("No accrued fees to collect")]
    NoFeesToCollect,

    #[msg("Insufficient assets in vault for withdrawal")]
    InsufficientAssets,
}
