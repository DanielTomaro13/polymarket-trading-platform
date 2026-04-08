"""
Cross-venue arbitrage engine.
Detects and evaluates price discrepancies between Polymarket US and Kalshi.

Leverages:
- Falcon API `/v2/cross/compare` for automated market matching
- Direct Kalshi API for real-time order book data
- Polymarket US API for real-time BBO data
- Fee-aware net profit calculation
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.falcon_client import FalconClient
from app.services.kalshi_client import KalshiClient
from app.services.polymarket_client import PolymarketClient

logger = logging.getLogger(__name__)


@dataclass
class ArbitrageOpportunity:
    """A detected cross-venue price discrepancy."""

    topic: str
    polymarket_slug: str
    kalshi_ticker: str
    polymarket_yes_price: float
    kalshi_yes_price: float
    gross_gap: float
    estimated_pm_fee: float
    estimated_kalshi_fee: float
    net_gap: float
    volume_ratio: float | None
    is_actionable: bool
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def direction(self) -> str:
        """Which venue is cheaper for YES."""
        if self.polymarket_yes_price < self.kalshi_yes_price:
            return "BUY PM / SELL KALSHI"
        return "BUY KALSHI / SELL PM"


class ArbitrageEngine:
    """
    Scans for and evaluates cross-venue arbitrage opportunities
    between Polymarket US and Kalshi.

    Two modes:
    1. Falcon-powered scan: Uses `/v2/cross/compare` for automated matching
    2. Direct scan: Compares known matched markets via both APIs
    """

    # Approximate Kalshi taker fee (cents per contract out of 100)
    KALSHI_FEE_PER_CONTRACT_CENTS = 7  # ~$0.07 per contract
    MIN_NET_GAP_THRESHOLD = 0.02  # minimum 2 cents net profit required

    def __init__(
        self,
        polymarket: PolymarketClient,
        kalshi: KalshiClient,
        falcon: FalconClient | None = None,
    ) -> None:
        self._pm = polymarket
        self._kalshi = kalshi
        self._falcon = falcon
        self._matched_markets: list[dict[str, str]] = []

    # ──────────────────────────────────────────
    # Falcon-Powered Scan
    # ──────────────────────────────────────────

    async def scan_via_falcon(self, topic: str) -> list[ArbitrageOpportunity]:
        """
        Use Falcon API to find and compare matched markets across venues.

        Args:
            topic: Search topic (e.g., "nba-finals-2026", "senate-control-2026")

        Returns:
            List of arbitrage opportunities with fee-adjusted net gaps.
        """
        if not self._falcon:
            logger.warning("Falcon client not available — cannot scan via Falcon")
            return []

        try:
            result = await self._falcon.cross_compare(
                topic=topic,
                venues=["polymarket", "kalshi"],
                metrics=["price_gap", "volume_ratio"],
            )
        except Exception:
            logger.exception("Falcon cross-compare failed for topic: %s", topic)
            return []

        opportunities: list[ArbitrageOpportunity] = []

        # Process the largest disagreement
        largest = result.get("largest_disagreement")
        if largest and largest.get("price_gap", 0) > 0:
            opp = self._evaluate_opportunity(
                topic=largest.get("topic", topic),
                pm_slug=topic,  # Falcon doesn't return the slug directly
                kalshi_ticker="",
                pm_yes=largest.get("polymarket_yes", 0),
                kalshi_yes=largest.get("kalshi_yes", 0),
                volume_ratio=largest.get("volume_ratio"),
            )
            if opp:
                opportunities.append(opp)

        return opportunities

    # ──────────────────────────────────────────
    # Direct Scan (Known Matched Markets)
    # ──────────────────────────────────────────

    def register_matched_market(
        self,
        pm_slug: str,
        kalshi_ticker: str,
        topic: str = "",
    ) -> None:
        """Register a known matched market pair for direct scanning."""
        self._matched_markets.append({
            "pm_slug": pm_slug,
            "kalshi_ticker": kalshi_ticker,
            "topic": topic or f"{pm_slug} <-> {kalshi_ticker}",
        })

    async def scan_direct(self) -> list[ArbitrageOpportunity]:
        """
        Scan all registered matched markets for price discrepancies
        using direct API calls to both venues.
        """
        opportunities: list[ArbitrageOpportunity] = []

        for match in self._matched_markets:
            try:
                # Fetch BBO from Polymarket
                pm_bbo = await self._pm.get_market_bbo(match["pm_slug"])
                pm_mid = (
                    float(pm_bbo.get("best_bid", 0)) + float(pm_bbo.get("best_ask", 0))
                ) / 2

                # Fetch orderbook from Kalshi
                kalshi_book = await self._kalshi.get_market_orderbook(
                    match["kalshi_ticker"], depth=1
                )
                kalshi_yes_bid = kalshi_book.get("yes", {}).get("bids", [{}])[0].get("price", 0)
                kalshi_yes_ask = kalshi_book.get("yes", {}).get("asks", [{}])[0].get("price", 0)
                kalshi_mid = (kalshi_yes_bid + kalshi_yes_ask) / 2 / 100  # Kalshi uses cents

                opp = self._evaluate_opportunity(
                    topic=match["topic"],
                    pm_slug=match["pm_slug"],
                    kalshi_ticker=match["kalshi_ticker"],
                    pm_yes=pm_mid,
                    kalshi_yes=kalshi_mid,
                    volume_ratio=None,
                )
                if opp:
                    opportunities.append(opp)

            except Exception:
                logger.exception(
                    "Failed to scan matched market: %s <-> %s",
                    match["pm_slug"],
                    match["kalshi_ticker"],
                )

        return opportunities

    # ──────────────────────────────────────────
    # Fee Calculation & Evaluation
    # ──────────────────────────────────────────

    def _estimate_pm_taker_fee(self, price: float) -> float:
        """Estimate Polymarket US taker fee per contract."""
        return 0.05 * price * (1 - price)

    def _estimate_kalshi_taker_fee(self) -> float:
        """Estimate Kalshi taker fee per contract (fixed ~$0.07)."""
        return self.KALSHI_FEE_PER_CONTRACT_CENTS / 100

    def _evaluate_opportunity(
        self,
        topic: str,
        pm_slug: str,
        kalshi_ticker: str,
        pm_yes: float,
        kalshi_yes: float,
        volume_ratio: float | None,
    ) -> ArbitrageOpportunity | None:
        """Evaluate a potential arbitrage opportunity with fee adjustment."""
        gross_gap = abs(pm_yes - kalshi_yes)

        if gross_gap < 0.005:  # less than half a cent, not worth evaluating
            return None

        # Estimate round-trip fees (buy on one venue, sell on another)
        pm_fee = self._estimate_pm_taker_fee(pm_yes)
        kalshi_fee = self._estimate_kalshi_taker_fee()
        total_fees = pm_fee + kalshi_fee
        net_gap = gross_gap - total_fees

        is_actionable = net_gap >= self.MIN_NET_GAP_THRESHOLD

        opp = ArbitrageOpportunity(
            topic=topic,
            polymarket_slug=pm_slug,
            kalshi_ticker=kalshi_ticker,
            polymarket_yes_price=pm_yes,
            kalshi_yes_price=kalshi_yes,
            gross_gap=round(gross_gap, 4),
            estimated_pm_fee=round(pm_fee, 4),
            estimated_kalshi_fee=round(kalshi_fee, 4),
            net_gap=round(net_gap, 4),
            volume_ratio=volume_ratio,
            is_actionable=is_actionable,
        )

        if is_actionable:
            logger.info(
                "ARBITRAGE FOUND: %s | PM=%.2f Kalshi=%.2f | gap=%.4f net=%.4f | %s",
                topic,
                pm_yes,
                kalshi_yes,
                gross_gap,
                net_gap,
                opp.direction,
            )

        return opp

    # ──────────────────────────────────────────
    # Same-Platform Complete Set Arbitrage
    # ──────────────────────────────────────────

    @staticmethod
    def check_complete_set_arb(
        outcome_ask_prices: list[float],
    ) -> dict[str, Any]:
        """
        Check for complete-set arbitrage on a single platform.

        For mutually exclusive markets with N outcomes, if buying all
        outcomes at their current ask costs less than $1.00, you have
        a guaranteed profit at settlement.

        Args:
            outcome_ask_prices: List of current ask prices for each outcome

        Returns:
            Dict with total_cost, profit_per_set, and is_actionable.
        """
        total_cost = sum(outcome_ask_prices)
        profit = 1.00 - total_cost

        return {
            "total_cost": round(total_cost, 4),
            "profit_per_set": round(profit, 4),
            "is_actionable": profit > 0.02,  # > 2 cents to be worth it
            "num_outcomes": len(outcome_ask_prices),
        }
