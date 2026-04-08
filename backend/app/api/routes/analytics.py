"""
Analytics API routes.
Surfaces Falcon API data: sentiment, cross-venue arbitrage, trader intelligence.
"""

from typing import Any

from fastapi import APIRouter, Query

from app.services.falcon_client import FalconClient

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_client: FalconClient | None = None


def init_client(client: FalconClient) -> None:
    global _client
    _client = client


def _get_client() -> FalconClient:
    if _client is None:
        raise RuntimeError("FalconClient not initialised")
    return _client


# ──────────────────────────────────────────
# Falcon Market Data
# ──────────────────────────────────────────


@router.get("/markets")
async def retrieve_markets(
    market_slug: str | None = None,
    min_volume: str | None = None,
    closed: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Retrieve market data from Falcon API with filtering."""
    return await _get_client().retrieve_markets(
        market_slug=market_slug,
        min_volume=min_volume,
        closed=closed,
        limit=limit,
        offset=offset,
    )


# ──────────────────────────────────────────
# Trader Intelligence
# ──────────────────────────────────────────


@router.get("/traders/{wallet}/stats")
async def get_trader_stats(
    wallet: str,
    timeframe: str = Query("30d", regex="^(7d|15d|30d|90d|all)$"),
) -> dict[str, Any]:
    """Get performance stats for a specific wallet address."""
    return await _get_client().get_trader_stats(
        wallet=wallet,
        metrics=["pnl", "roi", "win_rate", "drawdown"],
        timeframe=timeframe,
    )


# ──────────────────────────────────────────
# Cross-Venue Arbitrage
# ──────────────────────────────────────────


@router.get("/arbitrage/compare")
async def cross_venue_compare(
    topic: str = Query(..., min_length=1),
) -> dict[str, Any]:
    """Compare matched markets between Polymarket and Kalshi."""
    return await _get_client().cross_compare(
        topic=topic,
        venues=["polymarket", "kalshi"],
        metrics=["price_gap", "volume_ratio"],
    )


# ──────────────────────────────────────────
# Sentiment Analysis
# ──────────────────────────────────────────


@router.get("/sentiment/{market_slug}")
async def get_sentiment(
    market_slug: str,
    window: str = Query("24h", regex="^(1h|6h|24h|7d)$"),
) -> dict[str, Any]:
    """Get sentiment analysis for a specific market."""
    return await _get_client().get_sentiment(
        market_slug=market_slug,
        sources=["twitter", "reddit", "news"],
        window=window,
    )
