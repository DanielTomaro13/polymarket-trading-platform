"""
SQLAlchemy ORM models for the Polymarket platform.
Covers market hierarchy (Series → Events → Markets), order book snapshots,
positions, orders, and trade history.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────


class MarketState(str, PyEnum):
    OPEN = "open"
    PRE_OPEN = "pre_open"
    SUSPENDED = "suspended"
    HALTED = "halted"
    EXPIRED = "expired"


class OrderSide(str, PyEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, PyEnum):
    LIMIT = "limit"
    MARKET = "market"


class OrderTIF(str, PyEnum):
    GTC = "good_till_cancel"
    GTD = "good_till_date"
    IOC = "immediate_or_cancel"
    FOK = "fill_or_kill"


class OrderStatus(str, PyEnum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"


class PositionSide(str, PyEnum):
    LONG = "long"
    SHORT = "short"


# ──────────────────────────────────────────────
# Market Hierarchy: Series → Events → Markets
# ──────────────────────────────────────────────


class Series(Base):
    """A broad grouping of related events (e.g., NFL 2025-26 Season)."""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    events: Mapped[list["Event"]] = relationship(back_populates="series")


class Event(Base):
    """A specific occurrence within a series (e.g., Chiefs vs Eagles — Feb 9, 2026)."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    series_id: Mapped[int | None] = mapped_column(ForeignKey("series.id"))
    name: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sport: Mapped[str | None] = mapped_column(String(100))
    league: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[str | None] = mapped_column(Text)  # live score, period, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    series: Mapped[Series | None] = relationship(back_populates="events")
    markets: Mapped[list["Market"]] = relationship(back_populates="event")


class Market(Base):
    """A tradable yes/no contract (e.g., Will the Chiefs win?)."""

    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"))
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    question: Mapped[str] = mapped_column(Text)
    market_type: Mapped[str | None] = mapped_column(String(100))  # moneyline, spread, total, prop
    state: Mapped[str] = mapped_column(String(50), default=MarketState.OPEN.value)

    # Current pricing (cached from WebSocket)
    best_bid: Mapped[float | None] = mapped_column(Float)
    best_ask: Mapped[float | None] = mapped_column(Float)
    mid_price: Mapped[float | None] = mapped_column(Float)
    spread: Mapped[float | None] = mapped_column(Float)
    last_price: Mapped[float | None] = mapped_column(Float)

    # Volume & liquidity
    volume_total: Mapped[float | None] = mapped_column(Float)
    bid_depth: Mapped[float | None] = mapped_column(Float)
    ask_depth: Mapped[float | None] = mapped_column(Float)

    # Settlement
    settlement_price: Mapped[float | None] = mapped_column(Float)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    event: Mapped[Event | None] = relationship(back_populates="markets")

    __table_args__ = (
        Index("ix_markets_state", "state"),
        Index("ix_markets_market_type", "market_type"),
    )


# ──────────────────────────────────────────────
# Time-Series: BBO Ticks (for TimescaleDB hypertable)
# ──────────────────────────────────────────────


class BBOTick(Base):
    """
    Best-bid-and-offer tick data.
    This table should be converted to a TimescaleDB hypertable
    on the `timestamp` column for efficient time-series queries.
    """

    __tablename__ = "bbo_ticks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    market_slug: Mapped[str] = mapped_column(String(500), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    best_bid: Mapped[float] = mapped_column(Float)
    best_ask: Mapped[float] = mapped_column(Float)
    mid_price: Mapped[float] = mapped_column(Float)
    spread: Mapped[float] = mapped_column(Float)
    bid_size: Mapped[float | None] = mapped_column(Float)
    ask_size: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (Index("ix_bbo_ticks_slug_time", "market_slug", "timestamp"),)


# ──────────────────────────────────────────────
# Trading: Orders & Positions
# ──────────────────────────────────────────────


class Order(Base):
    """Local record of an order placed on Polymarket US."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    market_slug: Mapped[str] = mapped_column(String(500), index=True)
    side: Mapped[str] = mapped_column(String(10))  # buy / sell
    order_type: Mapped[str] = mapped_column(String(20))  # limit / market
    tif: Mapped[str] = mapped_column(String(30))  # GTC, GTD, IOC, FOK
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_fill_price: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default=OrderStatus.PENDING.value)
    fee_paid: Mapped[float] = mapped_column(Float, default=0.0)
    rebate_received: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_orders_status", "status"),)


class Position(Base):
    """Current open position in a market."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    market_slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    side: Mapped[str] = mapped_column(String(10))  # long / short
    quantity: Mapped[int] = mapped_column(Integer)
    avg_entry_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float)
    unrealised_pnl: Mapped[float | None] = mapped_column(Float)
    realised_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    margin_locked: Mapped[float] = mapped_column(Float, default=0.0)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ──────────────────────────────────────────────
# Analytics: Arbitrage & Sentiment Snapshots
# ──────────────────────────────────────────────


class ArbitrageSnapshot(Base):
    """Record of a detected cross-venue price discrepancy."""

    __tablename__ = "arbitrage_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(500))
    polymarket_price: Mapped[float] = mapped_column(Float)
    kalshi_price: Mapped[float] = mapped_column(Float)
    price_gap: Mapped[float] = mapped_column(Float)
    net_gap_after_fees: Mapped[float] = mapped_column(Float)
    volume_ratio: Mapped[float | None] = mapped_column(Float)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SentimentSnapshot(Base):
    """Snapshot of Falcon sentiment analysis for a market."""

    __tablename__ = "sentiment_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    market_slug: Mapped[str] = mapped_column(String(500), index=True)
    sentiment_score: Mapped[float] = mapped_column(Float)
    mention_volume: Mapped[int] = mapped_column(Integer)
    price_sentiment_divergence: Mapped[float] = mapped_column(Float)
    narrative_trend: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)
    top_influencer: Mapped[str | None] = mapped_column(String(255))
    window: Mapped[str] = mapped_column(String(10))  # 1h, 6h, 24h, 7d
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_sentiment_slug_time", "market_slug", "captured_at"),)
