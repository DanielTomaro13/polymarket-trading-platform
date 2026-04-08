"""
Polymarket International (Crypto) API client.
Wraps the `py-clob-client` SDK for the blockchain-based CLOB.
Operates on Polygon network with USDC settlement.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class PolymarketInternationalClient:
    """
    Client for Polymarket International (crypto-based, non-US).

    Uses the py-clob-client SDK for authenticated trading and raw HTTP
    for the Gamma API (market metadata).
    """

    CLOB_BASE = "https://clob.polymarket.com"
    GAMMA_BASE = "https://gamma-api.polymarket.com"

    def __init__(self) -> None:
        self._http = httpx.AsyncClient(timeout=30.0)
        self._clob_client = None

        # Lazy-init the CLOB client if credentials available
        if settings.poly_intl_private_key:
            try:
                from py_clob_client.client import ClobClient

                self._clob_client = ClobClient(
                    self.CLOB_BASE,
                    key=settings.poly_intl_private_key,
                    chain_id=137,  # Polygon mainnet
                    signature_type=1,
                    funder=settings.poly_intl_funder_address or None,
                )
                # Derive API credentials
                self._clob_client.set_api_creds(
                    self._clob_client.create_or_derive_api_creds()
                )
                logger.info("Polymarket International CLOB client initialised (authenticated)")
            except ImportError:
                logger.warning("py-clob-client not installed, International trading unavailable")
            except Exception as e:
                logger.error("Failed to initialise CLOB client: %s", e)
        else:
            logger.info("No International credentials — public endpoints only")

    # ──────────────────────────────────────────
    # Gamma API — Market Metadata (Public)
    # ──────────────────────────────────────────

    async def list_events(
        self,
        limit: int = 50,
        offset: int = 0,
        active: bool = True,
        closed: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch events from the Gamma API."""
        params = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
        }
        resp = await self._http.get(f"{self.GAMMA_BASE}/events", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_event(self, event_id: str) -> dict[str, Any]:
        """Get a specific event by ID from the Gamma API."""
        resp = await self._http.get(f"{self.GAMMA_BASE}/events/{event_id}")
        resp.raise_for_status()
        return resp.json()

    async def list_markets(
        self,
        limit: int = 50,
        offset: int = 0,
        active: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch markets from the Gamma API."""
        params = {"limit": limit, "offset": offset, "active": str(active).lower()}
        resp = await self._http.get(f"{self.GAMMA_BASE}/markets", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_market(self, condition_id: str) -> dict[str, Any]:
        """Get a specific market by condition_id from the Gamma API."""
        resp = await self._http.get(f"{self.GAMMA_BASE}/markets/{condition_id}")
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # CLOB API — Public Market Data
    # ──────────────────────────────────────────

    async def get_midpoint(self, token_id: str) -> dict[str, Any]:
        """Get the midpoint price for a token."""
        resp = await self._http.get(
            f"{self.CLOB_BASE}/midpoint", params={"token_id": token_id}
        )
        resp.raise_for_status()
        return resp.json()

    async def get_price(self, token_id: str, side: str = "BUY") -> dict[str, Any]:
        """Get the current price for a token on a given side."""
        resp = await self._http.get(
            f"{self.CLOB_BASE}/price",
            params={"token_id": token_id, "side": side},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_order_book(self, token_id: str) -> dict[str, Any]:
        """Get the order book for a token."""
        resp = await self._http.get(
            f"{self.CLOB_BASE}/book", params={"token_id": token_id}
        )
        resp.raise_for_status()
        return resp.json()

    async def get_spread(self, token_id: str) -> dict[str, Any]:
        """Get the bid-ask spread for a token."""
        resp = await self._http.get(
            f"{self.CLOB_BASE}/spread", params={"token_id": token_id}
        )
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # CLOB API — Authenticated Trading
    # ──────────────────────────────────────────

    def _require_auth(self) -> None:
        if self._clob_client is None:
            raise RuntimeError("CLOB client not available — check private key config")

    def create_market_order(
        self,
        token_id: str,
        amount: float,
        side: str = "BUY",
    ) -> dict[str, Any]:
        """Create and submit a market order (FOK)."""
        self._require_auth()
        from py_clob_client.clob_types import MarketOrderArgs, OrderType
        from py_clob_client.order_builder.constants import BUY, SELL

        order_side = BUY if side.upper() == "BUY" else SELL
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=order_side,
            order_type=OrderType.FOK,
        )
        signed = self._clob_client.create_market_order(order_args)  # type: ignore
        return self._clob_client.post_order(signed, OrderType.FOK)  # type: ignore

    def create_limit_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: str = "BUY",
    ) -> dict[str, Any]:
        """Create and submit a limit order (GTC)."""
        self._require_auth()
        from py_clob_client.clob_types import OrderArgs, OrderType
        from py_clob_client.order_builder.constants import BUY, SELL

        order_side = BUY if side.upper() == "BUY" else SELL
        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=order_side,
        )
        signed = self._clob_client.create_order(order_args)  # type: ignore
        return self._clob_client.post_order(signed, OrderType.GTC)  # type: ignore

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        """Cancel an order by ID."""
        self._require_auth()
        return self._clob_client.cancel(order_id)  # type: ignore

    def cancel_all_orders(self) -> dict[str, Any]:
        """Cancel all open orders."""
        self._require_auth()
        return self._clob_client.cancel_all()  # type: ignore

    def get_open_orders(self) -> list[dict[str, Any]]:
        """Get all open orders."""
        self._require_auth()
        return self._clob_client.get_orders()  # type: ignore

    # ──────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http.aclose()
