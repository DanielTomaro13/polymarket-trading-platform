"""
AI Agent API routes.
Endpoints for market research, trade suggestions, agent configuration,
and MCP tool definitions for Claude integration.
"""

from typing import Any

from fastapi import APIRouter, Body, Query

from app.services.ai_agent import AgentConfig, AIResearchAgent

router = APIRouter(prefix="/agent", tags=["AI Agent"])

_agent: AIResearchAgent | None = None


def init_agent(agent: AIResearchAgent) -> None:
    global _agent
    _agent = agent


def _get_agent() -> AIResearchAgent:
    if _agent is None:
        raise RuntimeError("AIResearchAgent not initialised")
    return _agent


# ──────────────────────────────────────────
# Market Research
# ──────────────────────────────────────────


@router.post("/research")
async def research_market(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """
    AI-powered deep research on a market.

    Body:
    {
        "slug": "chiefs-super-bowl-lxi",
        "question": "Will the Chiefs win Super Bowl LXI?",
        "current_price": 0.24,
        "sentiment_data": {...},   // optional
        "price_history": [...],    // optional
        "arbitrage_data": {...}    // optional
    }
    """
    agent = _get_agent()
    research = await agent.research_market(
        slug=params["slug"],
        question=params.get("question", ""),
        current_price=params["current_price"],
        sentiment_data=params.get("sentiment_data"),
        price_history=params.get("price_history"),
        arbitrage_data=params.get("arbitrage_data"),
        volume=params.get("volume", 0),
        spread=params.get("spread", 0),
    )

    return {
        "slug": research.slug,
        "question": research.question,
        "timestamp": research.timestamp,
        "direction": research.direction,
        "confidence": research.confidence,
        "fair_value": research.fair_value_estimate,
        "current_price": research.current_price,
        "edge": research.edge,
        "reasoning": research.reasoning,
        "risk_factors": research.risk_factors,
        "sentiment": research.sentiment_summary,
        "kelly_fraction": research.kelly_size,
        "recommended_size": research.recommended_size,
        "max_loss": research.max_loss,
        "expected_value": research.expected_value,
    }


# ──────────────────────────────────────────
# Trade Suggestions
# ──────────────────────────────────────────


@router.post("/suggestions")
async def get_suggestions(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """
    Generate AI trade suggestions across multiple markets.

    Body:
    {
        "markets": [
            {"slug": "chiefs-...", "mid_price": 0.24, "volume_total": 2450000, "spread": 0.02},
            ...
        ]
    }
    """
    agent = _get_agent()
    suggestions = await agent.generate_suggestions(params.get("markets", []))

    return {
        "count": len(suggestions),
        "suggestions": [
            {
                "slug": s.slug,
                "action": s.action,
                "quantity": s.quantity,
                "price": s.price,
                "confidence": s.confidence,
                "reasoning": s.reasoning,
                "edge": s.edge_estimate,
                "risk_reward": s.risk_reward,
                "priority": s.priority,
                "tags": s.tags,
            }
            for s in suggestions
        ],
    }


# ──────────────────────────────────────────
# Agent Configuration
# ──────────────────────────────────────────


@router.get("/status")
async def get_status() -> dict[str, Any]:
    """Get current AI agent status."""
    return _get_agent().get_status()


@router.post("/mode")
async def set_mode(
    mode: str = Query(..., regex="^(manual|suggest|auto)$"),
) -> dict[str, Any]:
    """Set AI agent mode: manual, suggest, or auto."""
    agent = _get_agent()
    agent.set_mode(mode)
    return {"mode": mode, "status": agent.get_status()}


@router.post("/config")
async def update_config(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """Update agent configuration parameters."""
    agent = _get_agent()
    config = agent.config

    if "max_trades_per_day" in params:
        config.max_trades_per_day = int(params["max_trades_per_day"])
    if "max_single_trade" in params:
        config.max_single_trade = float(params["max_single_trade"])
    if "min_confidence" in params:
        config.min_confidence = float(params["min_confidence"])
    if "min_edge" in params:
        config.min_edge = float(params["min_edge"])
    if "kelly_fraction" in params:
        config.kelly_fraction = float(params["kelly_fraction"])
    if "require_sentiment_confirm" in params:
        config.require_sentiment_confirm = bool(params["require_sentiment_confirm"])

    return {"status": "updated", "config": agent.get_status()}


# ──────────────────────────────────────────
# MCP Integration
# ──────────────────────────────────────────


@router.get("/mcp/tools")
async def get_mcp_tools() -> list[dict[str, Any]]:
    """Get MCP tool definitions for Claude integration."""
    return _get_agent().get_mcp_tools()
