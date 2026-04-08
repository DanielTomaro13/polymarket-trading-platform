"""
Kalshi API client.
Supports both public market data and authenticated trading on the
CFTC-regulated Kalshi prediction market exchange.

Auth: RSA-PSS signature-based authentication.
Base URL: https://api.elections.kalshi.com/trade-api/v2
"""

import base64
import logging
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class KalshiClient:
    """
    Client for the Kalshi API (CFTC-regulated prediction market).

    Used primarily for cross-venue arbitrage with Polymarket US.
    Supports public market data and authenticated trading.
    """

    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self) -> None:
        self._http = httpx.AsyncClient(timeout=30.0)
        self._api_key_id = settings.kalshi_api_key_id
        self._private_key_path = settings.kalshi_private_key_path
        self._signer = None

        if self._api_key_id and self._private_key_path:
            try:
                self._init_signer()
                logger.info("Kalshi client initialised (authenticated)")
            except Exception as e:
                logger.error("Failed to initialise Kalshi auth: %s", e)
        else:
            logger.info("No Kalshi credentials — public endpoints only")

    def _init_signer(self) -> None:
        """Load RSA private key for request signing."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa

        with open(self._private_key_path, "rb") as f:
            self._private_key = serialization.load_pem_private_key(f.read(), password=None)
        self._signer = True

    def _build_auth_headers(self, method: str, path: str) -> dict[str, str]:
        """Build RSA-PSS signed authentication headers."""
        if not self._signer or not self._private_key:
            raise RuntimeError("Kalshi auth not configured")

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        timestamp_ms = str(int(time.time() * 1000))
        message = f"{timestamp_ms}{method.upper()}{path}"

        signature = self._private_key.sign(  # type: ignore
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        return {
            "KALSHI-ACCESS-KEY": self._api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode(),
            "Content-Type": "application/json",
        }

    # ──────────────────────────────────────────
    # Public Endpoints (No Auth)
    # ──────────────────────────────────────────

    async def list_events(
        self,
        limit: int = 50,
        cursor: str | None = None,
        status: str | None = None,
        series_ticker: str | None = None,
    ) -> dict[str, Any]:
        """GET /events — List events."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        if series_ticker:
            params["series_ticker"] = series_ticker

        resp = await self._http.get(f"{self.BASE_URL}/events", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_event(self, event_ticker: str) -> dict[str, Any]:
        """GET /events/{event_ticker} — Get event details."""
        resp = await self._http.get(f"{self.BASE_URL}/events/{event_ticker}")
        resp.raise_for_status()
        return resp.json()

    async def list_markets(
        self,
        limit: int = 50,
        cursor: str | None = None,
        event_ticker: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """GET /markets — List markets."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if event_ticker:
            params["event_ticker"] = event_ticker
        if status:
            params["status"] = status

        resp = await self._http.get(f"{self.BASE_URL}/markets", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_market(self, ticker: str) -> dict[str, Any]:
        """GET /markets/{ticker} — Get market details."""
        resp = await self._http.get(f"{self.BASE_URL}/markets/{ticker}")
        resp.raise_for_status()
        return resp.json()

    async def get_market_orderbook(self, ticker: str, depth: int = 10) -> dict[str, Any]:
        """GET /markets/{ticker}/orderbook — Get order book."""
        resp = await self._http.get(
            f"{self.BASE_URL}/markets/{ticker}/orderbook",
            params={"depth": depth},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_series(self, series_ticker: str) -> dict[str, Any]:
        """GET /series/{series_ticker} — Get series info."""
        resp = await self._http.get(f"{self.BASE_URL}/series/{series_ticker}")
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Authenticated Endpoints
    # ──────────────────────────────────────────

    def _require_auth(self) -> None:
        if not self._signer:
            raise RuntimeError("Kalshi authentication not configured")

    async def get_balance(self) -> dict[str, Any]:
        """GET /portfolio/balance — Get account balance."""
        self._require_auth()
        path = "/trade-api/v2/portfolio/balance"
        headers = self._build_auth_headers("GET", path)
        resp = await self._http.get(f"{self.BASE_URL}/portfolio/balance", headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def get_positions(
        self, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        """GET /portfolio/positions — Get open positions."""
        self._require_auth()
        path = "/trade-api/v2/portfolio/positions"
        headers = self._build_auth_headers("GET", path)
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = await self._http.get(
            f"{self.BASE_URL}/portfolio/positions", headers=headers, params=params
        )
        resp.raise_for_status()
        return resp.json()

    async def create_order(
        self,
        ticker: str,
        side: str,
        action: str,
        count: int,
        type: str = "limit",
        yes_price: int | None = None,
        no_price: int | None = None,
        expiration_ts: int | None = None,
    ) -> dict[str, Any]:
        """POST /portfolio/orders — Create a new order."""
        self._require_auth()
        path = "/trade-api/v2/portfolio/orders"
        headers = self._build_auth_headers("POST", path)

        body: dict[str, Any] = {
            "ticker": ticker,
            "side": side,  # "yes" or "no"
            "action": action,  # "buy" or "sell"
            "count": count,
            "type": type,
        }
        if yes_price is not None:
            body["yes_price"] = yes_price
        if no_price is not None:
            body["no_price"] = no_price
        if expiration_ts is not None:
            body["expiration_ts"] = expiration_ts

        resp = await self._http.post(
            f"{self.BASE_URL}/portfolio/orders", headers=headers, json=body
        )
        resp.raise_for_status()
        return resp.json()

    async def cancel_order(self, order_id: str) -> dict[str, Any]:
        """DELETE /portfolio/orders/{order_id} — Cancel an order."""
        self._require_auth()
        path = f"/trade-api/v2/portfolio/orders/{order_id}"
        headers = self._build_auth_headers("DELETE", path)
        resp = await self._http.delete(
            f"{self.BASE_URL}/portfolio/orders/{order_id}", headers=headers
        )
        resp.raise_for_status()
        return resp.json()

    async def get_orders(
        self, ticker: str | None = None, status: str | None = None
    ) -> dict[str, Any]:
        """GET /portfolio/orders — Get orders."""
        self._require_auth()
        path = "/trade-api/v2/portfolio/orders"
        headers = self._build_auth_headers("GET", path)
        params: dict[str, Any] = {}
        if ticker:
            params["ticker"] = ticker
        if status:
            params["status"] = status
        resp = await self._http.get(
            f"{self.BASE_URL}/portfolio/orders", headers=headers, params=params
        )
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http.aclose()
