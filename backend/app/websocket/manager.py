"""
WebSocket connection manager for Polymarket US real-time streams.

Manages two persistent connections:
1. Private WS (wss://api.polymarket.us/v1/ws/private)
   - Order updates, position changes, balance changes
2. Market WS (wss://api.polymarket.us/v1/ws/markets)
   - Order book depth (MARKET_DATA) and BBO (MARKET_DATA_LITE)
"""

import asyncio
import base64
import json
import logging
import time
from typing import Any, Callable, Coroutine

import websockets

from app.core.config import settings

logger = logging.getLogger(__name__)

# Subscription types as documented
SUBSCRIPTION_TYPE_ORDER = "SUBSCRIPTION_TYPE_ORDER"
SUBSCRIPTION_TYPE_POSITION = "SUBSCRIPTION_TYPE_POSITION"
SUBSCRIPTION_TYPE_ACCOUNT_BALANCE = "SUBSCRIPTION_TYPE_ACCOUNT_BALANCE"
SUBSCRIPTION_TYPE_MARKET_DATA = "SUBSCRIPTION_TYPE_MARKET_DATA"
SUBSCRIPTION_TYPE_MARKET_DATA_LITE = "SUBSCRIPTION_TYPE_MARKET_DATA_LITE"

# Callback type for message handlers
MessageHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class WebSocketManager:
    """
    Manages persistent WebSocket connections to Polymarket US.

    Handles:
    - Connection lifecycle with auto-reconnect
    - Ed25519 authentication for WebSocket endpoints
    - Subscription management for market slugs
    - Message routing to registered handlers
    """

    def __init__(self) -> None:
        self._private_ws: Any = None
        self._market_ws: Any = None
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._subscribed_slugs: set[str] = set()
        self._running = False
        self._reconnect_delay = 1.0
        self._max_reconnect_delay = 30.0
        self._tasks: list[asyncio.Task[None]] = []

    # ──────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────

    def _build_ws_auth_params(self) -> dict[str, str]:
        """Build Ed25519 signed auth parameters for WebSocket connection."""
        if not settings.polymarket_key_id or not settings.polymarket_secret_key:
            raise RuntimeError("Polymarket API credentials required for WebSocket auth")

        from cryptography.hazmat.primitives.asymmetric import ed25519

        timestamp = str(int(time.time() * 1000))
        method = "GET"
        path = "/v1/ws"
        message = f"{timestamp}{method}{path}"

        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
            base64.b64decode(settings.polymarket_secret_key)[:32]
        )
        signature = base64.b64encode(private_key.sign(message.encode())).decode()

        return {
            "key_id": settings.polymarket_key_id,
            "timestamp": timestamp,
            "signature": signature,
        }

    # ──────────────────────────────────────────
    # Handler Registration
    # ──────────────────────────────────────────

    def on_message(self, subscription_type: str, handler: MessageHandler) -> None:
        """Register a handler for a specific subscription type."""
        if subscription_type not in self._handlers:
            self._handlers[subscription_type] = []
        self._handlers[subscription_type].append(handler)
        logger.debug("Registered handler for %s", subscription_type)

    async def _dispatch(self, subscription_type: str, data: dict[str, Any]) -> None:
        """Dispatch a message to all registered handlers for its type."""
        handlers = self._handlers.get(subscription_type, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception:
                logger.exception("Handler error for %s", subscription_type)

    # ──────────────────────────────────────────
    # Private WebSocket
    # ──────────────────────────────────────────

    async def _connect_private(self) -> None:
        """Connect to the private WebSocket and subscribe to account updates."""
        delay = self._reconnect_delay

        while self._running:
            try:
                auth = self._build_ws_auth_params()
                url = settings.polymarket_ws_private
                logger.info("Connecting to private WebSocket: %s", url)

                async with websockets.connect(url) as ws:
                    self._private_ws = ws
                    delay = self._reconnect_delay  # reset on success

                    # Authenticate
                    await ws.send(json.dumps({
                        "type": "auth",
                        "params": auth,
                    }))

                    # Subscribe to all private channels
                    for sub_type in [
                        SUBSCRIPTION_TYPE_ORDER,
                        SUBSCRIPTION_TYPE_POSITION,
                        SUBSCRIPTION_TYPE_ACCOUNT_BALANCE,
                    ]:
                        await ws.send(json.dumps({
                            "type": "subscribe",
                            "params": {"subscription_type": sub_type},
                        }))
                        logger.info("Subscribed to private: %s", sub_type)

                    # Message loop
                    async for raw_msg in ws:
                        msg = json.loads(raw_msg)
                        msg_type = msg.get("subscription_type", msg.get("type", ""))
                        await self._dispatch(msg_type, msg)

            except websockets.ConnectionClosed as e:
                logger.warning("Private WS closed: %s. Reconnecting in %.1fs...", e, delay)
            except Exception:
                logger.exception("Private WS error. Reconnecting in %.1fs...", delay)

            self._private_ws = None
            await asyncio.sleep(delay)
            delay = min(delay * 2, self._max_reconnect_delay)

    # ──────────────────────────────────────────
    # Market WebSocket
    # ──────────────────────────────────────────

    async def subscribe_market(self, slug: str, full_depth: bool = False) -> None:
        """Subscribe to market data for a specific slug."""
        self._subscribed_slugs.add(slug)
        sub_type = SUBSCRIPTION_TYPE_MARKET_DATA if full_depth else SUBSCRIPTION_TYPE_MARKET_DATA_LITE

        if self._market_ws:
            await self._market_ws.send(json.dumps({
                "type": "subscribe",
                "params": {
                    "subscription_type": sub_type,
                    "market_slug": slug,
                },
            }))
            logger.info("Subscribed to market %s: %s", sub_type, slug)

    async def unsubscribe_market(self, slug: str) -> None:
        """Unsubscribe from market data for a specific slug."""
        self._subscribed_slugs.discard(slug)
        if self._market_ws:
            await self._market_ws.send(json.dumps({
                "type": "unsubscribe",
                "params": {"market_slug": slug},
            }))

    async def _connect_market(self) -> None:
        """Connect to the market WebSocket and subscribe to market data."""
        delay = self._reconnect_delay

        while self._running:
            try:
                auth = self._build_ws_auth_params()
                url = settings.polymarket_ws_markets
                logger.info("Connecting to market WebSocket: %s", url)

                async with websockets.connect(url) as ws:
                    self._market_ws = ws
                    delay = self._reconnect_delay

                    # Authenticate
                    await ws.send(json.dumps({
                        "type": "auth",
                        "params": auth,
                    }))

                    # Re-subscribe to all previously tracked slugs
                    for slug in self._subscribed_slugs:
                        await ws.send(json.dumps({
                            "type": "subscribe",
                            "params": {
                                "subscription_type": SUBSCRIPTION_TYPE_MARKET_DATA_LITE,
                                "market_slug": slug,
                            },
                        }))
                        logger.info("Re-subscribed to market: %s", slug)

                    # Message loop
                    async for raw_msg in ws:
                        msg = json.loads(raw_msg)
                        msg_type = msg.get("subscription_type", msg.get("type", ""))
                        await self._dispatch(msg_type, msg)

            except websockets.ConnectionClosed as e:
                logger.warning("Market WS closed: %s. Reconnecting in %.1fs...", e, delay)
            except Exception:
                logger.exception("Market WS error. Reconnecting in %.1fs...", delay)

            self._market_ws = None
            await asyncio.sleep(delay)
            delay = min(delay * 2, self._max_reconnect_delay)

    # ──────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────

    async def start(self) -> None:
        """Start both WebSocket connections as background tasks."""
        if self._running:
            logger.warning("WebSocket manager already running")
            return

        if not settings.polymarket_key_id:
            logger.warning("No API credentials — WebSocket connections disabled")
            return

        self._running = True
        self._tasks = [
            asyncio.create_task(self._connect_private()),
            asyncio.create_task(self._connect_market()),
        ]
        logger.info("WebSocket manager started (2 connections)")

    async def stop(self) -> None:
        """Stop all WebSocket connections."""
        self._running = False

        if self._private_ws:
            await self._private_ws.close()
        if self._market_ws:
            await self._market_ws.close()

        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        logger.info("WebSocket manager stopped")

    @property
    def is_connected(self) -> bool:
        """Whether both WebSocket connections are active."""
        return (
            self._private_ws is not None
            and self._market_ws is not None
        )
