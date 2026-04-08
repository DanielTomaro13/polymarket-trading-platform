"""
AI Research & Trading Agent for Polymarket.

Provides:
1. Market research agent — analyses a market using Falcon sentiment,
   price history, arbitrage data, and generates a structured report
2. Trade suggestion engine — recommends trades with reasoning
3. Autonomous trading mode — executes suggestions with configurable
   aggression and risk limits

Designed to integrate with Claude via MCP tool bindings.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.fee_calculator import estimate_trade_fees

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Data Types
# ──────────────────────────────────────────


@dataclass
class MarketResearch:
    """Structured research report for a market."""

    slug: str
    question: str
    timestamp: str
    fair_value_estimate: float
    confidence: float
    current_price: float
    edge: float
    direction: str  # "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"
    reasoning: list[str]
    risk_factors: list[str]
    sentiment_summary: dict[str, Any]
    arbitrage_data: dict[str, Any] | None
    kelly_size: float
    recommended_size: int
    max_loss: float
    expected_value: float


@dataclass
class TradeSuggestion:
    """An AI-generated trade suggestion with reasoning."""

    slug: str
    action: str  # "buy_yes", "buy_no", "sell_yes", "sell_no", "hold"
    quantity: int
    price: float
    confidence: float
    reasoning: str
    edge_estimate: float
    risk_reward: float
    priority: int  # 1 = highest
    tags: list[str] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Configuration for the AI trading agent."""

    mode: str = "manual"  # "manual", "suggest", "auto"
    max_trades_per_day: int = 10
    max_single_trade: float = 500.0
    min_confidence: float = 0.7
    min_edge: float = 0.05
    kelly_fraction: float = 0.25  # quarter-Kelly for safety
    auto_execute: bool = False
    require_sentiment_confirm: bool = True


# ──────────────────────────────────────────
# AI Research Agent
# ──────────────────────────────────────────


class AIResearchAgent:
    """
    AI-powered market research and trade suggestion engine.

    Analyses markets using multiple data sources and generates
    structured research reports with actionable trade suggestions.

    This agent is designed to be used both:
    1. Directly via API endpoints
    2. As MCP tool bindings for Claude integration
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self._daily_trade_count = 0
        self._daily_trade_date: str = ""
        self._suggestion_history: list[TradeSuggestion] = []

    # ──────────────────────────────────────────
    # Market Research
    # ──────────────────────────────────────────

    async def research_market(
        self,
        slug: str,
        question: str,
        current_price: float,
        sentiment_data: dict[str, Any] | None = None,
        price_history: list[dict[str, Any]] | None = None,
        arbitrage_data: dict[str, Any] | None = None,
        volume: float = 0,
        spread: float = 0,
    ) -> MarketResearch:
        """
        Perform comprehensive research on a market.

        Combines:
        - Current pricing analysis
        - Sentiment data (if available from Falcon)
        - Price momentum
        - Arbitrage signals
        - Volume/liquidity analysis

        Returns a structured research report.
        """
        now = datetime.now(timezone.utc).isoformat()

        # 1. Sentiment-based fair value estimate
        sentiment_score = 0.0
        sentiment_confidence = 0.5
        sentiment_summary: dict[str, Any] = {}

        if sentiment_data:
            sentiment_score = float(sentiment_data.get("sentimentScore", 0))
            sentiment_confidence = float(sentiment_data.get("confidence", 0.5))
            sentiment_summary = {
                "score": sentiment_score,
                "confidence": sentiment_confidence,
                "narrative": sentiment_data.get("narrativeTrend", "neutral"),
                "mentions": sentiment_data.get("mentionVolume", 0),
                "divergence": sentiment_data.get("priceSentimentDivergence", 0),
            }

        # 2. Price momentum analysis
        momentum = 0.0
        if price_history and len(price_history) >= 5:
            recent = [p.get("price", p.get("mid_price", 0.5)) for p in price_history[-5:]]
            older = [p.get("price", p.get("mid_price", 0.5)) for p in price_history[-10:-5]] if len(price_history) >= 10 else recent
            avg_recent = sum(recent) / len(recent)
            avg_older = sum(older) / len(older)
            if avg_older > 0:
                momentum = (avg_recent - avg_older) / avg_older

        # 3. Estimate fair value
        # Weight: 40% current price, 30% sentiment-adjusted, 20% momentum-adjusted, 10% arb
        sentiment_implied = current_price + sentiment_score * 0.10
        momentum_implied = current_price * (1 + momentum * 0.5)
        arb_implied = current_price

        if arbitrage_data and arbitrage_data.get("kalshi_price"):
            arb_implied = (current_price + float(arbitrage_data["kalshi_price"])) / 2

        fair_value = (
            current_price * 0.40
            + sentiment_implied * 0.30
            + momentum_implied * 0.20
            + arb_implied * 0.10
        )
        fair_value = max(0.01, min(0.99, fair_value))

        # 4. Calculate edge
        edge = fair_value - current_price
        abs_edge = abs(edge)

        # 5. Determine direction
        if abs_edge > 0.15:
            direction = "STRONG BUY" if edge > 0 else "STRONG SELL"
        elif abs_edge > 0.08:
            direction = "BUY" if edge > 0 else "SELL"
        else:
            direction = "HOLD"

        # 6. Kelly sizing
        if fair_value > current_price and current_price > 0 and current_price < 1:
            odds = (1 - current_price) / current_price
            q = 1 - fair_value
            kelly_f = max(0, (fair_value * odds - q) / odds)
        elif fair_value < current_price and current_price > 0:
            kelly_f = max(0, (current_price - fair_value) / current_price)
        else:
            kelly_f = 0

        adjusted_kelly = kelly_f * self.config.kelly_fraction
        bet_amount = 10000 * adjusted_kelly  # Assume $10K portfolio
        recommended_size = max(0, min(int(bet_amount / current_price), 500))

        # 7. Expected value
        if edge > 0:
            ev = recommended_size * edge
        else:
            ev = recommended_size * edge  # negative EV for sell

        max_loss = recommended_size * current_price

        # 8. Build reasoning
        reasoning = []
        risk_factors = []

        if sentiment_data:
            if sentiment_score > 0.3:
                reasoning.append(f"Strong positive sentiment ({sentiment_score:.2f}) supports upside")
            elif sentiment_score < -0.3:
                reasoning.append(f"Negative sentiment ({sentiment_score:.2f}) suggests downside risk")

            div = sentiment_data.get("priceSentimentDivergence", 0)
            if abs(div) > 0.15:
                reasoning.append(f"Price-sentiment divergence of {div:.0%} — potential mispricing")

        if abs(momentum) > 0.03:
            if momentum > 0:
                reasoning.append(f"Positive price momentum ({momentum:.1%}) over recent period")
            else:
                reasoning.append(f"Negative momentum ({momentum:.1%}) — trend is against")
                risk_factors.append("Negative momentum may continue")

        if arbitrage_data:
            gap = arbitrage_data.get("net_gap", 0)
            if gap > 0.02:
                reasoning.append(f"Cross-venue arbitrage gap of {gap:.4f} detected")

        if spread > 0.03:
            risk_factors.append(f"Wide bid-ask spread ({spread:.1%}) — execution risk")

        if volume < 100000:
            risk_factors.append("Low volume — liquidity risk on large orders")

        if not reasoning:
            reasoning.append("Insufficient signal strength for high-conviction trade")

        confidence = min(0.95, sentiment_confidence * 0.4 + min(abs_edge * 5, 0.5) + 0.1)

        return MarketResearch(
            slug=slug,
            question=question,
            timestamp=now,
            fair_value_estimate=round(fair_value, 4),
            confidence=round(confidence, 2),
            current_price=round(current_price, 4),
            edge=round(edge, 4),
            direction=direction,
            reasoning=reasoning,
            risk_factors=risk_factors,
            sentiment_summary=sentiment_summary,
            arbitrage_data=arbitrage_data,
            kelly_size=round(kelly_f, 4),
            recommended_size=recommended_size,
            max_loss=round(max_loss, 2),
            expected_value=round(ev, 2),
        )

    # ──────────────────────────────────────────
    # Trade Suggestions
    # ──────────────────────────────────────────

    async def generate_suggestions(
        self,
        markets: list[dict[str, Any]],
    ) -> list[TradeSuggestion]:
        """
        Generate trade suggestions across multiple markets.
        Ranks by edge × confidence and applies risk filters.
        """
        suggestions: list[TradeSuggestion] = []

        for market in markets:
            slug = market.get("slug", "")
            question = market.get("question", "")
            price = float(market.get("mid_price", market.get("best_ask", 0.5)))

            research = await self.research_market(
                slug=slug,
                question=question,
                current_price=price,
                sentiment_data=market.get("sentiment"),
                volume=float(market.get("volume_total", 0)),
                spread=float(market.get("spread", 0)),
            )

            if research.direction == "HOLD":
                continue
            if research.confidence < self.config.min_confidence:
                continue
            if abs(research.edge) < self.config.min_edge:
                continue

            action = "buy_yes" if research.edge > 0 else "buy_no"
            risk_reward = abs(research.expected_value) / max(research.max_loss, 0.01)

            suggestion = TradeSuggestion(
                slug=slug,
                action=action,
                quantity=research.recommended_size,
                price=price,
                confidence=research.confidence,
                reasoning="; ".join(research.reasoning),
                edge_estimate=research.edge,
                risk_reward=round(risk_reward, 2),
                priority=1 if abs(research.edge) > 0.10 else 2 if abs(research.edge) > 0.05 else 3,
                tags=[research.direction],
            )
            suggestions.append(suggestion)

        # Sort by priority then edge
        suggestions.sort(key=lambda s: (s.priority, -abs(s.edge_estimate)))
        self._suggestion_history.extend(suggestions)
        return suggestions

    # ──────────────────────────────────────────
    # MCP Tool Definitions
    # ──────────────────────────────────────────

    def get_mcp_tools(self) -> list[dict[str, Any]]:
        """
        Return MCP-compatible tool definitions for Claude integration.

        These tools allow Claude to:
        1. Research any market
        2. Get trade suggestions
        3. Execute trades (if auto mode enabled)
        4. Check portfolio status
        """
        return [
            {
                "name": "research_market",
                "description": "Perform deep research on a prediction market. Returns fair value estimate, sentiment analysis, edge calculation, and trade sizing recommendation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "slug": {"type": "string", "description": "Market slug/identifier"},
                        "question": {"type": "string", "description": "The market question"},
                        "current_price": {"type": "number", "description": "Current YES price (0-1)"},
                    },
                    "required": ["slug", "current_price"],
                },
            },
            {
                "name": "get_trade_suggestions",
                "description": "Generate AI-powered trade suggestions across tracked markets. Returns ranked list of actionable opportunities.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "min_confidence": {"type": "number", "description": "Minimum confidence threshold (0-1)"},
                        "max_results": {"type": "integer", "description": "Maximum suggestions to return"},
                    },
                },
            },
            {
                "name": "execute_suggestion",
                "description": "Execute a trade suggestion. Only available in 'auto' mode.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "slug": {"type": "string"},
                        "action": {"type": "string", "enum": ["buy_yes", "buy_no"]},
                        "quantity": {"type": "integer"},
                        "price": {"type": "number"},
                    },
                    "required": ["slug", "action", "quantity", "price"],
                },
            },
            {
                "name": "get_agent_status",
                "description": "Get current AI agent status, mode, daily trade count, and suggestion history.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    # ──────────────────────────────────────────
    # Status
    # ──────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Get current agent status."""
        return {
            "mode": self.config.mode,
            "auto_execute": self.config.auto_execute,
            "daily_trades": self._daily_trade_count,
            "max_daily": self.config.max_trades_per_day,
            "min_confidence": self.config.min_confidence,
            "min_edge": self.config.min_edge,
            "kelly_fraction": self.config.kelly_fraction,
            "suggestion_history_count": len(self._suggestion_history),
        }

    def set_mode(self, mode: str) -> None:
        """Set agent mode: manual, suggest, auto."""
        if mode not in ("manual", "suggest", "auto"):
            raise ValueError(f"Invalid mode: {mode}")
        self.config.mode = mode
        self.config.auto_execute = mode == "auto"
        logger.info("AI Agent mode set to: %s", mode)
