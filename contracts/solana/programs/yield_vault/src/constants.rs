/// PDA seed for vault state accounts
pub const VAULT_SEED: &[u8] = b"vault";

/// PDA seed for vault share mint
pub const SHARE_MINT_SEED: &[u8] = b"share_mint";

/// PDA seed for vault token account (holds underlying assets)
pub const VAULT_TOKEN_SEED: &[u8] = b"vault_token";

/// Maximum number of managers per vault
pub const MAX_MANAGERS: usize = 3;

/// Maximum fee in basis points (50%)
pub const MAX_FEE_BPS: u16 = 5_000;

/// Basis points denominator (100%)
pub const BPS_DENOMINATOR: u128 = 10_000;

/// Seconds in a year (365 days)
pub const SECONDS_PER_YEAR: u128 = 31_536_000;
