"""
Fee calculator implementing the Polymarket US fee schedule.

Fee formula: Fee = Θ × C × p × (1 − p)
  - Taker Θ = 0.05
  - Maker Θ = -0.0125 (rebate)

All calculations use banker's rounding (round half to even).
"""

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

TAKER_THETA = Decimal("0.05")
MAKER_THETA = Decimal("-0.0125")
WEEKLY_TAKER_REBATE_PCT = Decimal("0.50")


@dataclass
class FeeEstimate:
    """Fee estimate for a trade."""

    contracts: int
    price: float
    taker_fee: float
    maker_rebate: float
    weekly_taker_rebate: float
    net_taker_cost: float  # taker_fee - weekly_taker_rebate


def calculate_fee(
    contracts: int,
    price: float,
    is_maker: bool = False,
) -> Decimal:
    """
    Calculate the fee for a trade using the Polymarket symmetric formula.

    Args:
        contracts: Number of contracts (C)
        price: Trade price in dollars (0.01 to 0.99) (p)
        is_maker: If True, returns maker rebate (negative = you receive money)

    Returns:
        Fee amount in USD, rounded to nearest cent using banker's rounding.
    """
    c = Decimal(str(contracts))
    p = Decimal(str(price))
    theta = MAKER_THETA if is_maker else TAKER_THETA

    fee = theta * c * p * (1 - p)

    # Banker's rounding to nearest cent
    return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def estimate_trade_fees(contracts: int, price: float) -> FeeEstimate:
    """
    Calculate complete fee breakdown for a trade.

    Returns taker fee, maker rebate (instant), and estimated weekly taker rebate.
    """
    taker_fee = calculate_fee(contracts, price, is_maker=False)
    maker_rebate = calculate_fee(contracts, price, is_maker=True)
    weekly_rebate = (taker_fee * WEEKLY_TAKER_REBATE_PCT).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_EVEN
    )

    return FeeEstimate(
        contracts=contracts,
        price=price,
        taker_fee=float(taker_fee),
        maker_rebate=float(maker_rebate),
        weekly_taker_rebate=float(weekly_rebate),
        net_taker_cost=float(taker_fee - weekly_rebate),
    )


def calculate_price_impact(
    order_book: dict,
    side: str,
    quantity: int,
) -> dict:
    """
    Calculate expected price impact for a given order size against the book.

    Args:
        order_book: Order book dict with 'bids' and 'asks' as lists of [price, size]
        side: 'buy' or 'sell'
        quantity: Number of contracts to fill

    Returns:
        Dict with avg_fill_price, worst_price, price_impact, and levels_consumed.
    """
    levels = order_book.get("asks" if side == "buy" else "bids", [])
    remaining = quantity
    total_cost = 0.0
    levels_consumed = 0

    for price, size in levels:
        if remaining <= 0:
            break

        fill_qty = min(remaining, int(size))
        total_cost += fill_qty * float(price)
        remaining -= fill_qty
        levels_consumed += 1

    if remaining > 0:
        return {
            "error": "Insufficient liquidity",
            "fillable": quantity - remaining,
            "remaining": remaining,
        }

    avg_fill_price = total_cost / quantity
    best_price = float(levels[0][0]) if levels else 0.0
    price_impact = abs(avg_fill_price - best_price)

    return {
        "avg_fill_price": round(avg_fill_price, 4),
        "best_price": best_price,
        "worst_price": float(levels[levels_consumed - 1][0]) if levels_consumed > 0 else 0.0,
        "price_impact": round(price_impact, 4),
        "levels_consumed": levels_consumed,
        "total_cost": round(total_cost, 2),
    }


def kelly_fraction(
    estimated_probability: float,
    market_price: float,
    fraction_of_kelly: float = 0.5,
) -> float:
    """
    Calculate optimal position size using the Kelly Criterion.

    Args:
        estimated_probability: Your estimated probability of YES winning (0-1)
        market_price: Current market price for YES contracts (0-1)
        fraction_of_kelly: Safety factor (0.5 = half-Kelly recommended)

    Returns:
        Fraction of bankroll to wager (0.0 if no edge).
    """
    if market_price <= 0 or market_price >= 1:
        return 0.0

    # For a binary contract: odds = (1 - price) / price
    odds = (1.0 - market_price) / market_price
    q = 1.0 - estimated_probability

    f = (estimated_probability * odds - q) / odds

    return max(0.0, f * fraction_of_kelly)
