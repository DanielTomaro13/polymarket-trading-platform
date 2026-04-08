"""
Backtesting engine for Polymarket trading strategies.

Simulates strategy performance against historical market data with
fee-accurate execution, slippage modeling, and position tracking.

Supports:
- Multiple built-in strategies
- Custom strategy plugins via the Strategy base class
- Fee-accurate P&L calculation using the Polymarket fee formula
- Trade-by-trade execution log
- Portfolio equity curve generation
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.fee_calculator import calculate_fee

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Data Types
# ──────────────────────────────────────────


@dataclass
class HistoricalTick:
    """A single point-in-time market snapshot."""

    timestamp: datetime
    slug: str
    best_bid: float
    best_ask: float
    mid_price: float
    volume: float


@dataclass
class BacktestTrade:
    """A single trade executed during backtesting."""

    timestamp: datetime
    slug: str
    side: str  # "buy_yes", "buy_no", "sell_yes", "sell_no"
    price: float
    quantity: int
    fee: float
    slippage: float
    pnl: float = 0.0


@dataclass
class BacktestPosition:
    """A position held during backtesting."""

    slug: str
    side: str  # "yes" or "no"
    quantity: int
    avg_entry: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealised_pnl(self) -> float:
        if self.side == "yes":
            return self.quantity * (self.current_price - self.avg_entry)
        return self.quantity * (self.avg_entry - self.current_price)


@dataclass
class BacktestResult:
    """Complete result of a backtest run."""

    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    total_fees: float
    avg_trade_pnl: float
    best_trade: float
    worst_trade: float
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    trades: list[dict[str, Any]] = field(default_factory=list)


# ──────────────────────────────────────────
# Strategy Base Class
# ──────────────────────────────────────────


class Strategy(ABC):
    """Base class for all trading strategies."""

    name: str = "BaseStrategy"
    description: str = ""

    @abstractmethod
    def on_tick(
        self,
        tick: HistoricalTick,
        positions: dict[str, BacktestPosition],
        capital: float,
    ) -> list[dict[str, Any]]:
        """
        Called on each tick. Return a list of signals:
        [{"action": "buy_yes"|"buy_no"|"sell_yes"|"sell_no"|"close",
          "slug": str, "quantity": int, "price": float}]
        """
        ...

    def on_start(self, initial_capital: float) -> None:
        """Called when backtest starts."""
        pass

    def on_end(self, result: BacktestResult) -> None:
        """Called when backtest ends."""
        pass


# ──────────────────────────────────────────
# Built-in Strategies
# ──────────────────────────────────────────


class MomentumStrategy(Strategy):
    """
    Buy when price crosses above a threshold with positive momentum.
    Sell when price drops below exit threshold.
    """

    name = "Momentum"
    description = "Buy on upward price momentum, sell on reversal"

    def __init__(self, entry_threshold: float = 0.03, exit_loss: float = 0.05, lookback: int = 5):
        self.entry_threshold = entry_threshold
        self.exit_loss = exit_loss
        self.lookback = lookback
        self._price_history: dict[str, list[float]] = {}

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        slug = tick.slug

        if slug not in self._price_history:
            self._price_history[slug] = []
        self._price_history[slug].append(tick.mid_price)

        history = self._price_history[slug]
        if len(history) < self.lookback + 1:
            return signals

        momentum = (history[-1] - history[-self.lookback - 1]) / history[-self.lookback - 1]

        # Entry: positive momentum above threshold
        if slug not in positions and momentum > self.entry_threshold and capital > 50:
            qty = min(100, int(capital * 0.1 / tick.best_ask))
            if qty > 0:
                signals.append({"action": "buy_yes", "slug": slug, "quantity": qty, "price": tick.best_ask})

        # Exit: if position exists and price dropped
        if slug in positions:
            pos = positions[slug]
            if pos.side == "yes":
                loss_pct = (tick.mid_price - pos.avg_entry) / pos.avg_entry
                if loss_pct < -self.exit_loss:
                    signals.append({"action": "close", "slug": slug, "quantity": pos.quantity, "price": tick.best_bid})

        return signals


class MeanReversionStrategy(Strategy):
    """
    Buy when price deviates significantly below its moving average.
    Sell when it reverts to the mean.
    """

    name = "Mean Reversion"
    description = "Buy on dips below moving average, sell on reversion to mean"

    def __init__(self, window: int = 20, entry_std: float = 1.5, exit_std: float = 0.5):
        self.window = window
        self.entry_std = entry_std
        self.exit_std = exit_std
        self._price_history: dict[str, list[float]] = {}

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        slug = tick.slug

        if slug not in self._price_history:
            self._price_history[slug] = []
        self._price_history[slug].append(tick.mid_price)

        history = self._price_history[slug]
        if len(history) < self.window:
            return signals

        window_data = history[-self.window:]
        mean = sum(window_data) / len(window_data)
        variance = sum((x - mean) ** 2 for x in window_data) / len(window_data)
        std = variance ** 0.5

        if std == 0:
            return signals

        z_score = (tick.mid_price - mean) / std

        if slug not in positions and z_score < -self.entry_std and capital > 50:
            qty = min(100, int(capital * 0.1 / tick.best_ask))
            if qty > 0:
                signals.append({"action": "buy_yes", "slug": slug, "quantity": qty, "price": tick.best_ask})

        if slug in positions and z_score > -self.exit_std:
            pos = positions[slug]
            if pos.side == "yes":
                signals.append({"action": "close", "slug": slug, "quantity": pos.quantity, "price": tick.best_bid})

        return signals


class SentimentDivergenceStrategy(Strategy):
    """
    Buy when price is below sentiment-implied fair value.
    Requires sentiment data attached to ticks.
    """

    name = "Sentiment Divergence"
    description = "Buy when market price is below Falcon sentiment-implied value"

    def __init__(self, min_divergence: float = 0.10, min_confidence: float = 0.6):
        self.min_divergence = min_divergence
        self.min_confidence = min_confidence

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        # In production, sentiment would be joined to the tick
        # For backtesting, this is a placeholder
        return []


class SpreadCaptureStrategy(Strategy):
    """
    Market-making-lite: place passive limit orders to capture the bid-ask spread.
    """

    name = "Spread Capture"
    description = "Place passive limit orders inside the spread to capture maker rebates"

    def __init__(self, min_spread: float = 0.03, position_limit: int = 200):
        self.min_spread = min_spread
        self.position_limit = position_limit

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        spread = tick.best_ask - tick.best_bid

        if spread >= self.min_spread:
            mid = tick.mid_price
            current_qty = positions.get(tick.slug, BacktestPosition(tick.slug, "yes", 0, 0)).quantity

            if current_qty < self.position_limit and capital > 50:
                qty = min(25, int(capital * 0.05 / mid))
                if qty > 0:
                    signals.append({"action": "buy_yes", "slug": tick.slug, "quantity": qty, "price": tick.best_bid + 0.01})

        return signals


class ArbitrageStrategy(Strategy):
    """
    Cross-venue arbitrage: buy on cheaper venue, sell on expensive venue.
    Requires paired ticks from multiple venues.
    """

    name = "Cross-Venue Arbitrage"
    description = "Execute when fee-adjusted price gap exceeds threshold between PM and Kalshi"

    def __init__(self, min_net_gap: float = 0.02):
        self.min_net_gap = min_net_gap

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        # Requires multi-venue tick data — placeholder for backtest
        return []


class KellyCriterionStrategy(Strategy):
    """
    Size positions using the Kelly Criterion based on estimated edge.
    Uses a fractional Kelly (half-Kelly) for safety.
    """

    name = "Kelly Criterion"
    description = "Optimize position sizing using Kelly formula with edge estimation"

    def __init__(self, fraction: float = 0.5, edge_threshold: float = 0.05):
        self.fraction = fraction
        self.edge_threshold = edge_threshold
        self._price_history: dict[str, list[float]] = {}

    def on_tick(self, tick: HistoricalTick, positions: dict[str, BacktestPosition], capital: float) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        slug = tick.slug

        if slug not in self._price_history:
            self._price_history[slug] = []
        self._price_history[slug].append(tick.mid_price)

        history = self._price_history[slug]
        if len(history) < 30:
            return signals

        # Estimate probability using price trend
        recent_avg = sum(history[-10:]) / 10
        long_avg = sum(history[-30:]) / 30
        estimated_prob = min(0.95, max(0.05, recent_avg + (recent_avg - long_avg)))

        price = tick.best_ask
        if price <= 0 or price >= 1:
            return signals

        odds = (1.0 - price) / price
        q = 1.0 - estimated_prob
        kelly_f = (estimated_prob * odds - q) / odds

        if kelly_f > self.edge_threshold and slug not in positions:
            bet_fraction = kelly_f * self.fraction
            bet_amount = capital * bet_fraction
            qty = max(1, int(bet_amount / price))
            qty = min(qty, 200)
            signals.append({"action": "buy_yes", "slug": slug, "quantity": qty, "price": price})

        return signals


# ──────────────────────────────────────────
# Strategy Registry
# ──────────────────────────────────────────


BUILT_IN_STRATEGIES: dict[str, type[Strategy]] = {
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "sentiment_divergence": SentimentDivergenceStrategy,
    "spread_capture": SpreadCaptureStrategy,
    "arbitrage": ArbitrageStrategy,
    "kelly_criterion": KellyCriterionStrategy,
}


def get_strategy(name: str, **kwargs: Any) -> Strategy:
    """Get a strategy instance by name."""
    cls = BUILT_IN_STRATEGIES.get(name)
    if cls is None:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(BUILT_IN_STRATEGIES.keys())}")
    return cls(**kwargs)


# ──────────────────────────────────────────
# Backtesting Engine
# ──────────────────────────────────────────


class BacktestEngine:
    """
    Simulates strategy performance against historical market data.

    Features:
    - Fee-accurate execution using Polymarket's symmetric formula
    - Configurable slippage model
    - Position tracking with P&L
    - Equity curve generation
    - Trade-by-trade execution log
    """

    def __init__(
        self,
        initial_capital: float = 10_000.0,
        slippage_bps: float = 5.0,
    ) -> None:
        self.initial_capital = initial_capital
        self.slippage_bps = slippage_bps

    def run(
        self,
        strategy: Strategy,
        ticks: list[HistoricalTick],
    ) -> BacktestResult:
        """
        Run a backtest with the given strategy and historical data.

        Args:
            strategy: Strategy instance to test
            ticks: List of historical ticks, sorted by timestamp

        Returns:
            BacktestResult with full performance metrics.
        """
        capital = self.initial_capital
        positions: dict[str, BacktestPosition] = {}
        trades: list[BacktestTrade] = []
        equity_curve: list[dict[str, Any]] = []
        peak_equity = capital

        strategy.on_start(self.initial_capital)

        for tick in ticks:
            # Update position prices
            if tick.slug in positions:
                positions[tick.slug].current_price = tick.mid_price

            # Get signals from strategy
            signals = strategy.on_tick(tick, positions, capital)

            for signal in signals:
                trade = self._execute_signal(signal, tick, positions, capital)
                if trade:
                    trades.append(trade)
                    capital -= trade.price * trade.quantity + trade.fee + trade.slippage
                    if "close" in signal["action"] or "sell" in signal["action"]:
                        # Return proceeds
                        capital += trade.price * trade.quantity * 2 + trade.pnl

            # Calculate portfolio value
            portfolio_value = capital + sum(
                p.market_value for p in positions.values()
            )
            equity_curve.append({
                "timestamp": tick.timestamp.isoformat(),
                "equity": round(portfolio_value, 2),
                "capital": round(capital, 2),
                "positions_value": round(portfolio_value - capital, 2),
            })

            # Track drawdown
            if portfolio_value > peak_equity:
                peak_equity = portfolio_value

        # Calculate final metrics
        final_equity = capital + sum(p.market_value for p in positions.values())
        total_return = final_equity - self.initial_capital
        total_fees = sum(t.fee for t in trades)
        trade_pnls = [t.pnl for t in trades if t.pnl != 0]
        winning = [p for p in trade_pnls if p > 0]
        losing = [p for p in trade_pnls if p < 0]

        # Sharpe ratio approximation
        if trade_pnls and len(trade_pnls) > 1:
            avg_pnl = sum(trade_pnls) / len(trade_pnls)
            std_pnl = (sum((p - avg_pnl) ** 2 for p in trade_pnls) / (len(trade_pnls) - 1)) ** 0.5
            sharpe = (avg_pnl / std_pnl) * (252 ** 0.5) if std_pnl > 0 else 0
        else:
            sharpe = 0.0

        # Max drawdown
        max_dd = 0.0
        peak = self.initial_capital
        for point in equity_curve:
            eq = point["equity"]
            if eq > peak:
                peak = eq
            dd = peak - eq
            if dd > max_dd:
                max_dd = dd

        result = BacktestResult(
            strategy_name=strategy.name,
            start_date=ticks[0].timestamp.isoformat() if ticks else "",
            end_date=ticks[-1].timestamp.isoformat() if ticks else "",
            initial_capital=self.initial_capital,
            final_capital=round(final_equity, 2),
            total_return=round(total_return, 2),
            total_return_pct=round((total_return / self.initial_capital) * 100, 2),
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=round(len(winning) / len(trades) * 100, 1) if trades else 0,
            max_drawdown=round(max_dd, 2),
            max_drawdown_pct=round((max_dd / peak_equity) * 100, 2) if peak_equity > 0 else 0,
            sharpe_ratio=round(sharpe, 2),
            total_fees=round(total_fees, 2),
            avg_trade_pnl=round(sum(trade_pnls) / len(trade_pnls), 2) if trade_pnls else 0,
            best_trade=round(max(trade_pnls), 2) if trade_pnls else 0,
            worst_trade=round(min(trade_pnls), 2) if trade_pnls else 0,
            equity_curve=equity_curve,
            trades=[
                {
                    "timestamp": t.timestamp.isoformat(),
                    "slug": t.slug,
                    "side": t.side,
                    "price": t.price,
                    "quantity": t.quantity,
                    "fee": t.fee,
                    "pnl": t.pnl,
                }
                for t in trades
            ],
        )

        strategy.on_end(result)
        return result

    def _execute_signal(
        self,
        signal: dict[str, Any],
        tick: HistoricalTick,
        positions: dict[str, BacktestPosition],
        capital: float,
    ) -> BacktestTrade | None:
        """Execute a trade signal with fee and slippage."""
        action = signal["action"]
        slug = signal["slug"]
        qty = signal.get("quantity", 0)
        price = signal.get("price", tick.mid_price)

        if qty <= 0:
            return None

        # Apply slippage
        slippage = price * (self.slippage_bps / 10000)
        if "buy" in action:
            exec_price = price + slippage
        else:
            exec_price = price - slippage

        # Calculate fee
        fee = float(calculate_fee(qty, exec_price, is_maker=False))

        # Check sufficient capital
        cost = qty * exec_price + fee
        if "buy" in action and cost > capital:
            return None

        pnl = 0.0

        if action == "close" and slug in positions:
            pos = positions[slug]
            pnl = pos.unrealised_pnl - fee
            del positions[slug]
        elif "buy_yes" in action:
            if slug in positions:
                pos = positions[slug]
                total_cost = pos.avg_entry * pos.quantity + exec_price * qty
                total_qty = pos.quantity + qty
                pos.avg_entry = total_cost / total_qty
                pos.quantity = total_qty
            else:
                positions[slug] = BacktestPosition(
                    slug=slug, side="yes", quantity=qty, avg_entry=exec_price
                )
        elif "buy_no" in action:
            positions[slug] = BacktestPosition(
                slug=slug, side="no", quantity=qty, avg_entry=exec_price
            )

        return BacktestTrade(
            timestamp=tick.timestamp,
            slug=slug,
            side=action,
            price=round(exec_price, 4),
            quantity=qty,
            fee=round(fee, 4),
            slippage=round(slippage * qty, 4),
            pnl=round(pnl, 4),
        )
