"""
Risk management engine.
Enforces position limits, exposure caps, drawdown circuit breakers,
and provides a kill switch for emergency position flattening.

All risk checks run BEFORE an order is submitted to the exchange.
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RiskCheckResult:
    """Result of a risk check on a proposed trade."""

    allowed: bool
    reason: str | None = None
    warnings: list[str] | None = None

    @staticmethod
    def ok(warnings: list[str] | None = None) -> "RiskCheckResult":
        return RiskCheckResult(allowed=True, warnings=warnings)

    @staticmethod
    def reject(reason: str) -> "RiskCheckResult":
        return RiskCheckResult(allowed=False, reason=reason)


@dataclass
class PortfolioState:
    """Snapshot of current portfolio for risk evaluation."""

    cash_balance: float
    buying_power: float
    total_position_value: float
    positions: dict[str, "PositionInfo"]  # slug -> PositionInfo
    daily_pnl: float = 0.0


@dataclass
class PositionInfo:
    """Info about a single position for risk evaluation."""

    slug: str
    side: str  # "long" or "short"
    quantity: int
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealised_pnl: float


class RiskManager:
    """
    Pre-trade risk management engine.

    Checks:
    1. Max position size per market
    2. Max total portfolio exposure
    3. Daily loss circuit breaker
    4. Buying power reserve
    5. Concentration limit (no single market > X% of portfolio)
    6. Spread gate (reject in wide-spread markets)
    7. Liquidity gate (reject if insufficient book depth)
    """

    def __init__(self) -> None:
        self._max_position_size = settings.max_position_size
        self._max_total_exposure = settings.max_total_exposure
        self._max_daily_loss = settings.max_daily_loss
        self._buying_power_reserve = settings.buying_power_reserve_pct
        self._max_concentration = settings.max_concentration_pct
        self._max_spread = settings.max_spread_threshold
        self._min_liquidity = settings.min_liquidity_depth

        # Track daily P&L for circuit breaker
        self._daily_pnl: float = 0.0
        self._daily_pnl_date: date = datetime.now(timezone.utc).date()
        self._circuit_breaker_triggered = False

        logger.info(
            "RiskManager initialised: max_pos=%d, max_exposure=$%.0f, "
            "max_daily_loss=$%.0f, reserve=%.0f%%, concentration=%.0f%%",
            self._max_position_size,
            self._max_total_exposure,
            self._max_daily_loss,
            self._buying_power_reserve * 100,
            self._max_concentration * 100,
        )

    # ──────────────────────────────────────────
    # Pre-Trade Risk Check
    # ──────────────────────────────────────────

    def check_order(
        self,
        market_slug: str,
        side: str,
        quantity: int,
        price: float,
        portfolio: PortfolioState,
        market_spread: float | None = None,
        book_depth: int | None = None,
    ) -> RiskCheckResult:
        """
        Run all risk checks on a proposed order.
        Returns allowed=True if all checks pass, otherwise reason for rejection.
        """
        warnings: list[str] = []

        # Reset daily P&L if new day
        today = datetime.now(timezone.utc).date()
        if today != self._daily_pnl_date:
            self._daily_pnl = 0.0
            self._daily_pnl_date = today
            self._circuit_breaker_triggered = False

        # 1. Circuit breaker check
        if self._circuit_breaker_triggered:
            return RiskCheckResult.reject(
                f"Daily loss circuit breaker active (loss: ${abs(self._daily_pnl):.2f}). "
                "All trading halted until tomorrow."
            )

        # 2. Daily loss check
        if self._daily_pnl <= -self._max_daily_loss:
            self._circuit_breaker_triggered = True
            return RiskCheckResult.reject(
                f"Daily loss limit reached: ${abs(self._daily_pnl):.2f} >= ${self._max_daily_loss:.2f}"
            )

        # 3. Position size check
        existing_qty = 0
        if market_slug in portfolio.positions:
            existing_qty = portfolio.positions[market_slug].quantity

        new_total_qty = existing_qty + quantity
        if new_total_qty > self._max_position_size:
            return RiskCheckResult.reject(
                f"Position size {new_total_qty} exceeds max {self._max_position_size} "
                f"for {market_slug}"
            )

        # 4. Total exposure check
        order_cost = quantity * price
        new_exposure = portfolio.total_position_value + order_cost
        if new_exposure > self._max_total_exposure:
            return RiskCheckResult.reject(
                f"Total exposure ${new_exposure:.2f} would exceed max ${self._max_total_exposure:.2f}"
            )

        # 5. Buying power reserve check
        min_required_reserve = portfolio.cash_balance * self._buying_power_reserve
        remaining_bp = portfolio.buying_power - order_cost
        if remaining_bp < min_required_reserve:
            return RiskCheckResult.reject(
                f"Remaining buying power ${remaining_bp:.2f} below required reserve "
                f"${min_required_reserve:.2f} ({self._buying_power_reserve * 100:.0f}%)"
            )

        # 6. Concentration check
        total_portfolio = portfolio.total_position_value + portfolio.cash_balance
        if total_portfolio > 0:
            position_value = (existing_qty * price) + order_cost
            concentration = position_value / total_portfolio
            if concentration > self._max_concentration:
                return RiskCheckResult.reject(
                    f"Concentration {concentration * 100:.1f}% in {market_slug} exceeds "
                    f"max {self._max_concentration * 100:.0f}%"
                )
            elif concentration > self._max_concentration * 0.8:
                warnings.append(
                    f"Approaching concentration limit: {concentration * 100:.1f}% "
                    f"(max {self._max_concentration * 100:.0f}%)"
                )

        # 7. Spread gate
        if market_spread is not None and market_spread > self._max_spread:
            return RiskCheckResult.reject(
                f"Market spread {market_spread * 100:.1f}% exceeds max {self._max_spread * 100:.1f}%"
            )
        elif market_spread is not None and market_spread > self._max_spread * 0.7:
            warnings.append(
                f"Wide spread warning: {market_spread * 100:.1f}% "
                f"(threshold {self._max_spread * 100:.1f}%)"
            )

        # 8. Liquidity gate
        if book_depth is not None and book_depth < self._min_liquidity:
            return RiskCheckResult.reject(
                f"Book depth {book_depth} below minimum {self._min_liquidity} contracts"
            )

        return RiskCheckResult.ok(warnings if warnings else None)

    # ──────────────────────────────────────────
    # P&L Tracking
    # ──────────────────────────────────────────

    def record_fill(self, pnl_impact: float) -> None:
        """Record the P&L impact of a filled order for daily tracking."""
        today = datetime.now(timezone.utc).date()
        if today != self._daily_pnl_date:
            self._daily_pnl = 0.0
            self._daily_pnl_date = today
            self._circuit_breaker_triggered = False

        self._daily_pnl += pnl_impact

        if self._daily_pnl <= -self._max_daily_loss:
            self._circuit_breaker_triggered = True
            logger.critical(
                "CIRCUIT BREAKER TRIGGERED: Daily P&L $%.2f exceeded max loss $%.2f",
                self._daily_pnl,
                self._max_daily_loss,
            )

    # ──────────────────────────────────────────
    # Kill Switch
    # ──────────────────────────────────────────

    async def kill_switch(self, polymarket_client: Any) -> dict[str, Any]:
        """
        Emergency kill switch: cancel all orders and close all positions.
        Used when risk limits are breached or manual emergency.
        """
        logger.critical("KILL SWITCH ACTIVATED — cancelling all orders")
        results: dict[str, Any] = {"cancelled_orders": None, "closed_positions": []}

        try:
            cancel_result = await polymarket_client.cancel_all_orders()
            results["cancelled_orders"] = cancel_result
            logger.info("All orders cancelled: %s", cancel_result)
        except Exception:
            logger.exception("Failed to cancel all orders during kill switch")

        try:
            positions = await polymarket_client.get_positions()
            for pos in positions:
                slug = pos.get("marketSlug") or pos.get("market_slug", "")
                if slug:
                    try:
                        close_result = await polymarket_client.close_position(slug)
                        results["closed_positions"].append(
                            {"slug": slug, "result": close_result}
                        )
                        logger.info("Closed position: %s", slug)
                    except Exception:
                        logger.exception("Failed to close position: %s", slug)
        except Exception:
            logger.exception("Failed to fetch positions during kill switch")

        self._circuit_breaker_triggered = True
        return results

    # ──────────────────────────────────────────
    # Status
    # ──────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Get current risk manager status."""
        return {
            "circuit_breaker_triggered": self._circuit_breaker_triggered,
            "daily_pnl": round(self._daily_pnl, 2),
            "daily_pnl_date": self._daily_pnl_date.isoformat(),
            "max_daily_loss": self._max_daily_loss,
            "max_position_size": self._max_position_size,
            "max_total_exposure": self._max_total_exposure,
            "buying_power_reserve_pct": self._buying_power_reserve,
            "max_concentration_pct": self._max_concentration,
            "max_spread_threshold": self._max_spread,
            "min_liquidity_depth": self._min_liquidity,
        }
