use anchor_lang::prelude::*;

use crate::constants::{BPS_DENOMINATOR, SECONDS_PER_YEAR};
use crate::error::VaultError;

/// Calculate shares to mint for a given deposit amount.
///
/// First depositor gets 1:1 ratio. Subsequent depositors get proportional shares:
///   shares = (deposit_amount * total_shares) / total_assets
///
/// Uses u128 intermediates to prevent overflow on large values.
pub fn calculate_shares_to_mint(
    deposit_amount: u64,
    total_assets: u64,
    total_shares: u64,
) -> Result<u64> {
    if total_shares == 0 || total_assets == 0 {
        // First deposit: 1:1 ratio
        return Ok(deposit_amount);
    }

    let shares = (deposit_amount as u128)
        .checked_mul(total_shares as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_div(total_assets as u128)
        .ok_or(VaultError::ArithmeticOverflow)?;

    // Ensure result fits in u64
    u64::try_from(shares).map_err(|_| error!(VaultError::ArithmeticOverflow))
}

/// Calculate assets to return for a given number of shares burned.
///
///   assets = (shares_to_burn * total_assets) / total_shares
///
/// Uses u128 intermediates to prevent overflow.
pub fn calculate_assets_to_return(
    shares_to_burn: u64,
    total_assets: u64,
    total_shares: u64,
) -> Result<u64> {
    if total_shares == 0 {
        return Ok(0);
    }

    let assets = (shares_to_burn as u128)
        .checked_mul(total_assets as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_div(total_shares as u128)
        .ok_or(VaultError::ArithmeticOverflow)?;

    u64::try_from(assets).map_err(|_| error!(VaultError::ArithmeticOverflow))
}

/// Calculate time-weighted management fee.
///
///   fee = total_assets * management_fee_bps * seconds_elapsed / (BPS_DENOMINATOR * SECONDS_PER_YEAR)
///
/// This gives a pro-rata annual fee based on time elapsed since last collection.
pub fn calculate_management_fee(
    total_assets: u64,
    fee_bps: u16,
    seconds_elapsed: i64,
) -> Result<u64> {
    if fee_bps == 0 || seconds_elapsed <= 0 || total_assets == 0 {
        return Ok(0);
    }

    let fee = (total_assets as u128)
        .checked_mul(fee_bps as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_mul(seconds_elapsed as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_div(
            BPS_DENOMINATOR
                .checked_mul(SECONDS_PER_YEAR)
                .ok_or(VaultError::ArithmeticOverflow)?,
        )
        .ok_or(VaultError::ArithmeticOverflow)?;

    u64::try_from(fee).map_err(|_| error!(VaultError::ArithmeticOverflow))
}

/// Calculate performance fee on profits above the high-water mark.
///
/// Returns (fee_in_asset_units, new_high_water_mark).
///
/// Performance fee is only charged on the increase above the previous high-water mark,
/// measured as total_assets per share to be fair to all depositors.
pub fn calculate_performance_fee(
    total_assets: u64,
    high_water_mark: u64,
    fee_bps: u16,
    total_shares: u64,
) -> Result<(u64, u64)> {
    if fee_bps == 0 || total_shares == 0 || total_assets <= high_water_mark {
        return Ok((0, high_water_mark));
    }

    let profit = (total_assets as u128)
        .checked_sub(high_water_mark as u128)
        .ok_or(VaultError::ArithmeticOverflow)?;

    let fee = profit
        .checked_mul(fee_bps as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_div(BPS_DENOMINATOR)
        .ok_or(VaultError::ArithmeticOverflow)?;

    let fee_u64 = u64::try_from(fee).map_err(|_| error!(VaultError::ArithmeticOverflow))?;

    Ok((fee_u64, total_assets))
}

/// Convert a fee amount (in asset units) to the equivalent number of shares to mint.
///
///   fee_shares = (fee_amount * total_shares) / (total_assets - fee_amount)
///
/// This dilutes existing holders proportionally to the fee taken.
pub fn fee_amount_to_shares(
    fee_amount: u64,
    total_assets: u64,
    total_shares: u64,
) -> Result<u64> {
    if fee_amount == 0 || total_shares == 0 {
        return Ok(0);
    }

    let assets_after_fee = (total_assets as u128)
        .checked_sub(fee_amount as u128)
        .ok_or(VaultError::ArithmeticOverflow)?;

    if assets_after_fee == 0 {
        return Ok(0);
    }

    let shares = (fee_amount as u128)
        .checked_mul(total_shares as u128)
        .ok_or(VaultError::ArithmeticOverflow)?
        .checked_div(assets_after_fee)
        .ok_or(VaultError::ArithmeticOverflow)?;

    u64::try_from(shares).map_err(|_| error!(VaultError::ArithmeticOverflow))
}
