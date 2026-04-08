"""
Portfolio margin calculator for Polymarket US.

Implements margin-aware position sizing for different event structures:

1. **Mutually Exclusive (ME)** events: Multiple outcomes where only one can win.
   - Buying multiple YES contracts in an ME event returns collateral
     because max loss on combined positions cannot exceed $1.00.
   - Example: NBA Championship — buying YES on Celtics ($0.30) and YES on Lakers ($0.20)
     costs only $0.50 total, not $0.50, because one must win.

2. **Directional** markets: Simple YES/NO binary contracts.
   - Standard margin = contracts × price (for YES)
   - Standard margin = contracts × (1 - price) (for NO)

3. **Complete Set** recognition: Buying all outcomes at < $1.00 total = guaranteed profit.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MarginEstimate:
    """Detailed margin estimate for a trade or portfolio."""

    gross_cost: float  # cost without margin benefits
    margin_required: float  # actual margin needed (after ME offsets)
    margin_savings: float  # savings from ME collateral return
    buying_power_impact: float  # net impact on buying power
    max_loss: float  # worst-case scenario loss
    max_gain: float  # best-case scenario gain
    details: str = ""


@dataclass
class PortfolioMarginSummary:
    """Full portfolio margin analysis."""

    total_margin_required: float
    total_gross_cost: float
    total_margin_savings: float
    positions: list[dict[str, Any]] = field(default_factory=list)
    me_groups: list[dict[str, Any]] = field(default_factory=list)


class MarginCalculator:
    """
    Portfolio margin calculator for Polymarket US.

    Supports:
    - Standard directional margin for binary contracts
    - Mutually Exclusive (ME) collateral return offsets
    - Complete set arbitrage profit calculation
    - Portfolio-wide margin summarisation
    """

    def __init__(self) -> None:
        # Track known mutually-exclusive groups by event_id
        self._me_groups: dict[str, list[str]] = {}  # event_id -> [market_slugs]

    def register_me_group(self, event_id: str, market_slugs: list[str]) -> None:
        """Register a mutually exclusive group of markets (e.g., NBA Championship outcomes)."""
        self._me_groups[event_id] = market_slugs
        logger.info("Registered ME group for event %s: %d markets", event_id, len(market_slugs))

    # ──────────────────────────────────────────
    # Single Trade Margin
    # ──────────────────────────────────────────

    def estimate_trade_margin(
        self,
        side: str,
        quantity: int,
        price: float,
        is_me: bool = False,
        existing_me_positions: list[dict[str, Any]] | None = None,
    ) -> MarginEstimate:
        """
        Estimate margin required for a single trade.

        Args:
            side: "buy_yes", "buy_no", "sell_yes", "sell_no"
            quantity: Number of contracts
            price: Trade price in dollars
            is_me: Whether this market is in a mutually exclusive group
            existing_me_positions: List of existing positions in the same ME group
                [{"slug": ..., "side": "yes"/"no", "quantity": int, "price": float}]

        Returns:
            MarginEstimate with gross cost, actual margin, savings, and scenarios.
        """
        if "yes" in side.lower():
            gross_cost = quantity * price
            max_loss = gross_cost
            max_gain = quantity * (1.0 - price)
        else:
            gross_cost = quantity * (1.0 - price)
            max_loss = gross_cost
            max_gain = quantity * price

        margin_savings = 0.0

        # ME collateral return calculation
        if is_me and existing_me_positions and "buy" in side.lower() and "yes" in side.lower():
            # When buying multiple YES contracts in an ME event,
            # your max loss is capped at the MOST EXPENSIVE position
            # because only one outcome can win
            existing_costs = [
                p["quantity"] * p["price"]
                for p in existing_me_positions
                if p.get("side") == "yes"
            ]

            if existing_costs:
                all_costs = existing_costs + [gross_cost]
                # Without ME: you'd need sum of all position costs
                naive_total = sum(all_costs)
                # With ME: max loss is the maximum single position cost
                # because all others will settle at $0
                me_total = max(all_costs)
                margin_savings = naive_total - me_total

        margin_required = max(0, gross_cost - margin_savings)
        buying_power_impact = margin_required

        return MarginEstimate(
            gross_cost=round(gross_cost, 4),
            margin_required=round(margin_required, 4),
            margin_savings=round(margin_savings, 4),
            buying_power_impact=round(buying_power_impact, 4),
            max_loss=round(max_loss, 4),
            max_gain=round(max_gain, 4),
            details=(
                f"ME savings: ${margin_savings:.2f}" if margin_savings > 0
                else "Standard directional margin"
            ),
        )

    # ──────────────────────────────────────────
    # Portfolio Margin Analysis
    # ──────────────────────────────────────────

    def portfolio_margin(
        self,
        positions: list[dict[str, Any]],
    ) -> PortfolioMarginSummary:
        """
        Calculate portfolio-wide margin with ME group offsets.

        Args:
            positions: List of all open positions, each with:
                {"slug": str, "event_id": str, "side": "yes"/"no",
                 "quantity": int, "price": float, "current_price": float}

        Returns:
            PortfolioMarginSummary with total margin, savings, and per-position breakdown.
        """
        total_gross = 0.0
        total_margin = 0.0
        total_savings = 0.0
        position_details: list[dict[str, Any]] = []
        me_group_details: list[dict[str, Any]] = []

        # Group positions by event_id for ME analysis
        event_positions: dict[str, list[dict[str, Any]]] = {}
        standalone_positions: list[dict[str, Any]] = []

        for pos in positions:
            event_id = pos.get("event_id", "")
            if event_id and event_id in self._me_groups:
                event_positions.setdefault(event_id, []).append(pos)
            else:
                standalone_positions.append(pos)

        # Process standalone (directional) positions
        for pos in standalone_positions:
            cost = pos["quantity"] * pos["price"] if pos["side"] == "yes" else pos["quantity"] * (1 - pos["price"])
            total_gross += cost
            total_margin += cost
            position_details.append({
                "slug": pos["slug"],
                "type": "directional",
                "gross_cost": round(cost, 4),
                "margin_required": round(cost, 4),
                "savings": 0.0,
            })

        # Process ME groups
        for event_id, group_positions in event_positions.items():
            yes_positions = [p for p in group_positions if p["side"] == "yes"]
            no_positions = [p for p in group_positions if p["side"] == "no"]

            yes_costs = [p["quantity"] * p["price"] for p in yes_positions]
            naive_total = sum(yes_costs)
            me_margin = max(yes_costs) if yes_costs else 0.0
            savings = naive_total - me_margin

            # Add standalone NO positions in this event
            for p in no_positions:
                cost = p["quantity"] * (1 - p["price"])
                me_margin += cost
                naive_total += cost

            total_gross += naive_total
            total_margin += me_margin
            total_savings += savings

            me_group_details.append({
                "event_id": event_id,
                "num_positions": len(group_positions),
                "gross_cost": round(naive_total, 4),
                "margin_required": round(me_margin, 4),
                "savings": round(savings, 4),
                "slugs": [p["slug"] for p in group_positions],
            })

        return PortfolioMarginSummary(
            total_margin_required=round(total_margin, 4),
            total_gross_cost=round(total_gross, 4),
            total_margin_savings=round(total_savings, 4),
            positions=position_details,
            me_groups=me_group_details,
        )

    # ──────────────────────────────────────────
    # Complete Set Analysis
    # ──────────────────────────────────────────

    def check_me_complete_set(
        self,
        event_id: str,
        outcome_prices: dict[str, float],
    ) -> dict[str, Any]:
        """
        Check if buying all outcomes in an ME group at current ask prices
        creates a guaranteed profit (complete set arbitrage).

        Args:
            event_id: The event identifier
            outcome_prices: Dict of {slug: ask_price} for all outcomes

        Returns:
            Analysis with total cost, profit, and recommendation.
        """
        total_cost = sum(outcome_prices.values())
        settlement_value = 1.00  # winner settles at $1.00
        profit = settlement_value - total_cost

        return {
            "event_id": event_id,
            "num_outcomes": len(outcome_prices),
            "total_cost": round(total_cost, 4),
            "settlement_value": settlement_value,
            "profit_per_set": round(profit, 4),
            "roi_pct": round((profit / total_cost) * 100, 2) if total_cost > 0 else 0,
            "is_profitable": profit > 0,
            "is_actionable": profit > 0.02,  # > 2 cents per contract set
            "outcomes": outcome_prices,
        }
