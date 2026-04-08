"""
Market data API routes.
Provides REST endpoints for the frontend dashboard to consume market,
event, and series data from the cached Polymarket data.
"""

from typing import Any

from fastapi import APIRouter, Query

from app.services.polymarket_client import PolymarketClient

router = APIRouter(prefix="/markets", tags=["Markets"])

# Shared client instance (initialised on startup)
_client: PolymarketClient | None = None


def init_client(client: PolymarketClient) -> None:
    global _client
    _client = client


def _get_client() -> PolymarketClient:
    if _client is None:
        raise RuntimeError("PolymarketClient not initialised")
    return _client


@router.get("/events")
async def list_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    active: bool = Query(True),
) -> list[dict[str, Any]]:
    """List events with pagination and active filter."""
    return await _get_client().list_events(limit=limit, offset=offset, active=active)


@router.get("/events/{event_id}")
async def get_event(event_id: str) -> dict[str, Any]:
    """Get a specific event by ID."""
    return await _get_client().get_event(event_id)


@router.get("/events/slug/{slug}")
async def get_event_by_slug(slug: str) -> dict[str, Any]:
    """Get event by slug."""
    return await _get_client().get_event_by_slug(slug)


@router.get("/")
async def list_markets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    """List markets with pagination."""
    return await _get_client().list_markets(limit=limit, offset=offset)


@router.get("/slug/{slug}")
async def get_market_by_slug(slug: str) -> dict[str, Any]:
    """Get market by slug."""
    return await _get_client().get_market_by_slug(slug)


@router.get("/slug/{slug}/bbo")
async def get_market_bbo(slug: str) -> dict[str, Any]:
    """Get best bid/offer for a market."""
    return await _get_client().get_market_bbo(slug)


@router.get("/slug/{slug}/book")
async def get_market_book(slug: str) -> dict[str, Any]:
    """Get full order book for a market."""
    return await _get_client().get_market_book(slug)


@router.get("/slug/{slug}/settlement")
async def get_market_settlement(slug: str) -> dict[str, Any]:
    """Get settlement info for a market."""
    return await _get_client().get_market_settlement(slug)


@router.get("/series")
async def list_series(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    """List series."""
    return await _get_client().list_series(limit=limit, offset=offset)


@router.get("/sports")
async def list_sports() -> list[dict[str, Any]]:
    """List all sports."""
    return await _get_client().list_sports()


@router.get("/sports/leagues/{league_slug}/events")
async def get_league_events(league_slug: str) -> list[dict[str, Any]]:
    """Get events for a specific league."""
    return await _get_client().get_league_events(league_slug)


@router.get("/search")
async def search_markets(q: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Full-text search across events and markets."""
    return await _get_client().search(q)
