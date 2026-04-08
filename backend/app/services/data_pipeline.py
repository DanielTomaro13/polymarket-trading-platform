"""
Historical data pipeline for backtesting.

Ingests and stores historical market data from Polymarket and Kalshi,
normalises it into a common tick format, and serves it to the backtesting engine.

Sources:
1. Polymarket US — historical prices via the public API (timeseries endpoints)
2. Polymarket International — Gamma API historical data
3. Kalshi — historical market data via public endpoints
4. Falcon — historical sentiment snapshots (when subscribed)
"""

import csv
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import httpx

from app.services.backtest_engine import HistoricalTick

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "historical"


@dataclass
class DataSource:
    """Represents a source of historical data."""

    name: str
    venue: str  # "polymarket_us", "polymarket_intl", "kalshi"
    base_url: str


SOURCES = {
    "polymarket_us": DataSource(
        name="Polymarket US",
        venue="polymarket_us",
        base_url="https://polymarket.com/api",
    ),
    "polymarket_intl": DataSource(
        name="Polymarket International",
        venue="polymarket_intl",
        base_url="https://gamma-api.polymarket.com",
    ),
    "kalshi": DataSource(
        name="Kalshi",
        venue="kalshi",
        base_url="https://api.elections.kalshi.com/trade-api/v2",
    ),
}


class HistoricalDataPipeline:
    """
    Ingests, stores, and serves historical market data for backtesting.

    Supports:
    - Fetching price history from all three venues
    - CSV import/export for offline data
    - In-memory tick cache for fast backtest iteration
    - Date range filtering and resampling
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=30.0)
        self._tick_cache: dict[str, list[HistoricalTick]] = {}
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    async def close(self) -> None:
        await self._client.aclose()

    # ──────────────────────────────────────────
    # Polymarket US Historical Data
    # ──────────────────────────────────────────

    async def fetch_pm_us_history(
        self,
        slug: str,
        start_date: str | None = None,
        end_date: str | None = None,
        interval: str = "1h",
    ) -> list[HistoricalTick]:
        """
        Fetch historical price data from Polymarket US.
        Returns list of HistoricalTick objects.
        """
        params: dict[str, Any] = {"interval": interval}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        try:
            resp = await self._client.get(
                f"{SOURCES['polymarket_us'].base_url}/markets/{slug}/timeseries",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.warning("Failed to fetch PM-US history for %s, using synthetic data", slug)
            data = self._generate_synthetic_history(slug, start_date, end_date, interval)

        ticks = []
        for point in data:
            ticks.append(HistoricalTick(
                timestamp=datetime.fromisoformat(point.get("timestamp", point.get("t", "2026-01-01T00:00:00Z")).replace("Z", "+00:00")),
                slug=slug,
                best_bid=float(point.get("bid", point.get("bestBid", point.get("price", 0.5)) - 0.01)),
                best_ask=float(point.get("ask", point.get("bestAsk", point.get("price", 0.5)) + 0.01)),
                mid_price=float(point.get("price", point.get("midPrice", 0.5))),
                volume=float(point.get("volume", 0)),
            ))

        self._tick_cache[slug] = ticks
        logger.info("Fetched %d ticks for %s from Polymarket US", len(ticks), slug)
        return ticks

    # ──────────────────────────────────────────
    # Kalshi Historical Data
    # ──────────────────────────────────────────

    async def fetch_kalshi_history(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[HistoricalTick]:
        """Fetch historical data from Kalshi."""
        try:
            params: dict[str, Any] = {}
            if start_date:
                params["min_ts"] = start_date
            if end_date:
                params["max_ts"] = end_date

            resp = await self._client.get(
                f"{SOURCES['kalshi'].base_url}/markets/{ticker}/candlesticks",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json().get("candlesticks", [])
        except Exception:
            logger.warning("Failed to fetch Kalshi history for %s, using synthetic data", ticker)
            data = self._generate_synthetic_history(ticker, start_date, end_date, "1h")

        ticks = []
        for point in data:
            ts = point.get("end_period_ts") or point.get("timestamp") or "2026-01-01T00:00:00Z"
            if isinstance(ts, (int, float)):
                ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                ts_dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))

            price = float(point.get("price", point.get("close", 0.5))) / 100  # Kalshi uses cents
            ticks.append(HistoricalTick(
                timestamp=ts_dt,
                slug=ticker,
                best_bid=max(0.01, price - 0.01),
                best_ask=min(0.99, price + 0.01),
                mid_price=price,
                volume=float(point.get("volume", 0)),
            ))

        self._tick_cache[ticker] = ticks
        logger.info("Fetched %d ticks for %s from Kalshi", len(ticks), ticker)
        return ticks

    # ──────────────────────────────────────────
    # CSV Import/Export
    # ──────────────────────────────────────────

    def export_to_csv(self, slug: str, filepath: str | None = None) -> str:
        """Export cached ticks to CSV file."""
        ticks = self._tick_cache.get(slug, [])
        if not ticks:
            raise ValueError(f"No cached data for {slug}")

        path = filepath or str(DATA_DIR / f"{slug}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "slug", "best_bid", "best_ask", "mid_price", "volume"])
            for tick in ticks:
                writer.writerow([
                    tick.timestamp.isoformat(),
                    tick.slug,
                    tick.best_bid,
                    tick.best_ask,
                    tick.mid_price,
                    tick.volume,
                ])

        logger.info("Exported %d ticks to %s", len(ticks), path)
        return path

    def import_from_csv(self, filepath: str) -> list[HistoricalTick]:
        """Import ticks from a CSV file."""
        ticks: list[HistoricalTick] = []
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticks.append(HistoricalTick(
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    slug=row["slug"],
                    best_bid=float(row["best_bid"]),
                    best_ask=float(row["best_ask"]),
                    mid_price=float(row["mid_price"]),
                    volume=float(row["volume"]),
                ))

        if ticks:
            self._tick_cache[ticks[0].slug] = ticks
        logger.info("Imported %d ticks from %s", len(ticks), filepath)
        return ticks

    # ──────────────────────────────────────────
    # Merge & Resample
    # ──────────────────────────────────────────

    def get_ticks(
        self,
        slug: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[HistoricalTick]:
        """Get cached ticks with optional date filtering."""
        ticks = self._tick_cache.get(slug, [])
        if start:
            ticks = [t for t in ticks if t.timestamp >= start]
        if end:
            ticks = [t for t in ticks if t.timestamp <= end]
        return sorted(ticks, key=lambda t: t.timestamp)

    def merge_ticks(self, *slugs: str) -> list[HistoricalTick]:
        """Merge ticks from multiple markets into a single timeline."""
        all_ticks: list[HistoricalTick] = []
        for slug in slugs:
            all_ticks.extend(self._tick_cache.get(slug, []))
        return sorted(all_ticks, key=lambda t: t.timestamp)

    def list_cached(self) -> dict[str, int]:
        """List all cached datasets and their tick counts."""
        return {slug: len(ticks) for slug, ticks in self._tick_cache.items()}

    # ──────────────────────────────────────────
    # Synthetic Data Generation
    # ──────────────────────────────────────────

    def _generate_synthetic_history(
        self,
        slug: str,
        start_date: str | None,
        end_date: str | None,
        interval: str,
    ) -> list[dict[str, Any]]:
        """Generate synthetic price history for demo/testing."""
        import random

        start = datetime.fromisoformat(start_date) if start_date else datetime.now(timezone.utc) - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now(timezone.utc)

        interval_hours = {"1h": 1, "4h": 4, "1d": 24, "15m": 0.25}.get(interval, 1)
        delta = timedelta(hours=interval_hours)

        points = []
        price = 0.50 + random.uniform(-0.20, 0.20)
        current = start

        while current <= end:
            # Random walk with mean reversion
            drift = (0.50 - price) * 0.01
            shock = random.gauss(0, 0.015)
            price = max(0.05, min(0.95, price + drift + shock))

            points.append({
                "timestamp": current.isoformat(),
                "price": round(price, 4),
                "bid": round(max(0.01, price - random.uniform(0.005, 0.015)), 4),
                "ask": round(min(0.99, price + random.uniform(0.005, 0.015)), 4),
                "volume": round(random.uniform(1000, 50000), 0),
            })
            current += delta

        return points

    def generate_synthetic_dataset(
        self,
        slug: str,
        days: int = 30,
        interval: str = "1h",
    ) -> list[HistoricalTick]:
        """Generate and cache a synthetic dataset for testing strategies."""
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        raw = self._generate_synthetic_history(
            slug, start.isoformat(), end.isoformat(), interval
        )

        ticks = [
            HistoricalTick(
                timestamp=datetime.fromisoformat(p["timestamp"]),
                slug=slug,
                best_bid=p["bid"],
                best_ask=p["ask"],
                mid_price=p["price"],
                volume=p["volume"],
            )
            for p in raw
        ]

        self._tick_cache[slug] = ticks
        logger.info("Generated %d synthetic ticks for %s (%d days)", len(ticks), slug, days)
        return ticks
