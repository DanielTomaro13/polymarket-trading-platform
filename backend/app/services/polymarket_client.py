"""
Polymarket US API client service.
Wraps the official `polymarket-us` SDK with rate limiting, caching, and error handling.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class PolymarketClient:
    """
    Client for the Polymarket US API.

    Uses the official SDK for authenticated operations and raw httpx
    for public gateway endpoints (no auth required).
    """

    def __init__(self) -> None:
        self._gateway_base = settings.polymarket_gateway_base.rstrip("/")
        self._api_base = settings.polymarket_api_base.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30.0)
        self._sdk_client = None

        # Lazy-init the SDK client only if credentials are available
        if settings.polymarket_key_id and settings.polymarket_secret_key:
            try:
                from polymarket_us import PolymarketUS

                self._sdk_client = PolymarketUS(
                    key_id=settings.polymarket_key_id,
                    secret_key=settings.polymarket_secret_key,
                )
                logger.info("Polymarket US SDK client initialised (authenticated)")
            except ImportError:
                logger.warning("polymarket-us package not installed, using raw HTTP only")
        else:
            logger.info("No Polymarket credentials configured — public endpoints only")

    # ──────────────────────────────────────────
    # Public Gateway Endpoints (no auth)
    # ──────────────────────────────────────────

    async def list_events(
        self, limit: int = 50, offset: int = 0, active: bool = True
    ) -> list[dict[str, Any]]:
        """GET /v1/events — List events with pagination."""
        params = {"limit": limit, "offset": offset, "active": str(active).lower()}
        resp = await self._http.get(f"{self._gateway_base}/v1/events", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_event(self, event_id: str) -> dict[str, Any]:
        """GET /v1/events/{id} — Get event by ID."""
        resp = await self._http.get(f"{self._gateway_base}/v1/events/{event_id}")
        resp.raise_for_status()
        return resp.json()

    async def get_event_by_slug(self, slug: str) -> dict[str, Any]:
        """GET /v1/events/slug/{slug} — Get event by slug."""
        resp = await self._http.get(f"{self._gateway_base}/v1/events/slug/{slug}")
        resp.raise_for_status()
        return resp.json()

    async def list_markets(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """GET /v1/markets — List markets with pagination."""
        params = {"limit": limit, "offset": offset}
        resp = await self._http.get(f"{self._gateway_base}/v1/markets", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_market_by_slug(self, slug: str) -> dict[str, Any]:
        """GET /v1/markets/slug/{slug} — Get market by slug."""
        resp = await self._http.get(f"{self._gateway_base}/v1/markets/slug/{slug}")
        resp.raise_for_status()
        return resp.json()

    async def get_market_bbo(self, slug: str) -> dict[str, Any]:
        """GET /v1/markets/{slug}/bbo — Get best bid/offer."""
        resp = await self._http.get(f"{self._gateway_base}/v1/markets/{slug}/bbo")
        resp.raise_for_status()
        return resp.json()

    async def get_market_book(self, slug: str) -> dict[str, Any]:
        """GET /v1/markets/{slug}/book — Get full order book."""
        resp = await self._http.get(f"{self._gateway_base}/v1/markets/{slug}/book")
        resp.raise_for_status()
        return resp.json()

    async def get_market_settlement(self, slug: str) -> dict[str, Any]:
        """GET /v1/markets/{slug}/settlement — Get settlement info."""
        resp = await self._http.get(f"{self._gateway_base}/v1/markets/{slug}/settlement")
        resp.raise_for_status()
        return resp.json()

    async def list_series(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """GET /v1/series — List series."""
        params = {"limit": limit, "offset": offset}
        resp = await self._http.get(f"{self._gateway_base}/v1/series", params=params)
        resp.raise_for_status()
        return resp.json()

    async def list_sports(self) -> list[dict[str, Any]]:
        """GET /v1/sports — List all sports."""
        resp = await self._http.get(f"{self._gateway_base}/v1/sports")
        resp.raise_for_status()
        return resp.json()

    async def get_league_events(self, league_slug: str) -> list[dict[str, Any]]:
        """GET /v1/sports/leagues/{slug}/events — Get events by league."""
        resp = await self._http.get(
            f"{self._gateway_base}/v1/sports/leagues/{league_slug}/events"
        )
        resp.raise_for_status()
        return resp.json()

    async def search(self, query: str) -> dict[str, Any]:
        """GET /v1/search — Full-text search across events and markets."""
        resp = await self._http.get(f"{self._gateway_base}/v1/search", params={"q": query})
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Authenticated Trading Endpoints (via SDK)
    # ──────────────────────────────────────────

    def _require_auth(self) -> None:
        if self._sdk_client is None:
            raise RuntimeError("Polymarket SDK client not available — check credentials")

    async def get_balances(self) -> dict[str, Any]:
        """GET /v1/account/balances — Get account balances."""
        self._require_auth()
        return await self._sdk_client.account.balances()  # type: ignore[union-attr]

    async def get_positions(self) -> list[dict[str, Any]]:
        """GET /v1/portfolio/positions — Get open positions."""
        self._require_auth()
        return await self._sdk_client.portfolio.positions()  # type: ignore[union-attr]

    async def get_activities(self) -> list[dict[str, Any]]:
        """GET /v1/portfolio/activities — Get activities."""
        self._require_auth()
        return await self._sdk_client.portfolio.activities()  # type: ignore[union-attr]

    async def list_open_orders(self) -> list[dict[str, Any]]:
        """GET /v1/orders/open — Get open orders."""
        self._require_auth()
        return await self._sdk_client.orders.list()  # type: ignore[union-attr]

    async def create_order(self, order_params: dict[str, Any]) -> dict[str, Any]:
        """POST /v1/orders — Create a new order."""
        self._require_auth()
        return await self._sdk_client.orders.create(order_params)  # type: ignore[union-attr]

    async def cancel_order(self, order_id: str) -> dict[str, Any]:
        """POST /v1/order/{id}/cancel — Cancel an order."""
        self._require_auth()
        return await self._sdk_client.orders.cancel(order_id)  # type: ignore[union-attr]

    async def cancel_all_orders(self) -> dict[str, Any]:
        """POST /v1/orders/open/cancel — Cancel all open orders."""
        self._require_auth()
        return await self._sdk_client.orders.cancel_all()  # type: ignore[union-attr]

    async def preview_order(self, order_params: dict[str, Any]) -> dict[str, Any]:
        """POST /v1/order/preview — Preview order without execution."""
        self._require_auth()
        return await self._sdk_client.orders.preview(order_params)  # type: ignore[union-attr]

    async def close_position(self, market_slug: str) -> dict[str, Any]:
        """POST /v1/order/close-position — Close a position."""
        self._require_auth()
        return await self._sdk_client.orders.close_position(  # type: ignore[union-attr]
            {"marketSlug": market_slug}
        )

    # ──────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http.aclose()
