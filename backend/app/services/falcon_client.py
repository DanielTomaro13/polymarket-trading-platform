"""
Falcon API client for Polymarket Analytics.
Provides access to all four data suites:
  1. Historical & Real-Time Market Data
  2. Trader Intelligence & Analytics
  3. Cross-Market Analysis
  4. Web Intelligence & Sentiment
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class FalconClient:
    """
    Client for the Falcon API (Polymarket Analytics).
    All endpoints use POST with JSON body payloads.
    Base URL: https://narrative.agent.heisenberg.so/v2
    """

    def __init__(self) -> None:
        self._base_url = settings.falcon_api_base.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {settings.falcon_api_token}",
            "Content-Type": "application/json",
        }
        self._http = httpx.AsyncClient(timeout=30.0, headers=self._headers)

        if not settings.falcon_api_token:
            logger.warning("No Falcon API token configured — analytics endpoints unavailable")

    def _require_token(self) -> None:
        if not settings.falcon_api_token:
            raise RuntimeError("Falcon API token not configured")

    # ──────────────────────────────────────────
    # Suite 1: Historical & Real-Time Market Data
    # ──────────────────────────────────────────

    async def retrieve_markets(
        self,
        market_slug: str | None = None,
        min_volume: str | None = None,
        closed: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """POST /v2/markets/retrieve — Retrieve market data with flexible filtering."""
        self._require_token()

        params: dict[str, Any] = {}
        if market_slug:
            params["market_slug"] = market_slug
        if min_volume:
            params["min_volume"] = min_volume
        if closed:
            params["closed"] = closed

        body = {
            "agent_id": 574,
            "params": params,
            "pagination": {"limit": limit, "offset": offset},
            "formatter_config": {"format_type": "raw"},
        }

        resp = await self._http.post(f"{self._base_url}/markets/retrieve", json=body)
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Suite 2: Trader Intelligence & Analytics
    # ──────────────────────────────────────────

    async def get_trader_stats(
        self,
        wallet: str,
        metrics: list[str] | None = None,
        timeframe: str = "30d",
    ) -> dict[str, Any]:
        """POST /v2/traders/stats — Trader performance metrics."""
        self._require_token()

        if metrics is None:
            metrics = ["pnl", "roi", "win_rate", "drawdown"]

        body = {
            "wallet": wallet,
            "metrics": metrics,
            "timeframe": timeframe,
        }

        resp = await self._http.post(f"{self._base_url}/traders/stats", json=body)
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Suite 3: Cross-Market Analysis
    # ──────────────────────────────────────────

    async def cross_compare(
        self,
        topic: str,
        venues: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """POST /v2/cross/compare — Cross-venue market comparison."""
        self._require_token()

        if venues is None:
            venues = ["polymarket", "kalshi"]
        if metrics is None:
            metrics = ["price_gap", "volume_ratio"]

        body = {
            "topic": topic,
            "venues": venues,
            "metrics": metrics,
        }

        resp = await self._http.post(f"{self._base_url}/cross/compare", json=body)
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Suite 4: Web Intelligence & Sentiment
    # ──────────────────────────────────────────

    async def get_sentiment(
        self,
        market_slug: str,
        sources: list[str] | None = None,
        window: str = "24h",
    ) -> dict[str, Any]:
        """POST /v2/signals/sentiment — Sentiment analysis for a market."""
        self._require_token()

        if sources is None:
            sources = ["twitter", "reddit", "news"]

        body = {
            "market_slug": market_slug,
            "sources": sources,
            "window": window,
        }

        resp = await self._http.post(f"{self._base_url}/signals/sentiment", json=body)
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http.aclose()
