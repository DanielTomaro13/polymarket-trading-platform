"""
Backtesting API routes.
Endpoints for running backtests, managing historical data, and comparing strategies.
"""

from typing import Any

from fastapi import APIRouter, Body, Query

from app.services.backtest_engine import (
    BUILT_IN_STRATEGIES,
    BacktestEngine,
    get_strategy,
)
from app.services.data_pipeline import HistoricalDataPipeline

router = APIRouter(prefix="/backtest", tags=["Backtesting"])

_pipeline: HistoricalDataPipeline | None = None


def init_pipeline(pipeline: HistoricalDataPipeline) -> None:
    global _pipeline
    _pipeline = pipeline


def _get_pipeline() -> HistoricalDataPipeline:
    if _pipeline is None:
        raise RuntimeError("HistoricalDataPipeline not initialised")
    return _pipeline


# ──────────────────────────────────────────
# Strategy Info
# ──────────────────────────────────────────


@router.get("/strategies")
async def list_strategies() -> list[dict[str, str]]:
    """List all available built-in strategies."""
    return [
        {"id": key, "name": cls.name, "description": cls.description}
        for key, cls in BUILT_IN_STRATEGIES.items()
    ]


# ──────────────────────────────────────────
# Historical Data
# ──────────────────────────────────────────


@router.post("/data/fetch")
async def fetch_historical_data(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """
    Fetch historical data for a market.

    Body:
    {
        "slug": "chiefs-super-bowl-lxi",
        "venue": "polymarket_us" | "kalshi",
        "start_date": "2026-01-01",
        "end_date": "2026-04-07",
        "interval": "1h"
    }
    """
    pipeline = _get_pipeline()
    slug = params["slug"]
    venue = params.get("venue", "polymarket_us")
    start = params.get("start_date")
    end = params.get("end_date")
    interval = params.get("interval", "1h")

    if venue == "kalshi":
        ticks = await pipeline.fetch_kalshi_history(slug, start, end)
    else:
        ticks = await pipeline.fetch_pm_us_history(slug, start, end, interval)

    return {
        "slug": slug,
        "venue": venue,
        "tick_count": len(ticks),
        "start": ticks[0].timestamp.isoformat() if ticks else None,
        "end": ticks[-1].timestamp.isoformat() if ticks else None,
    }


@router.post("/data/generate")
async def generate_synthetic_data(
    slug: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    interval: str = Query("1h"),
) -> dict[str, Any]:
    """Generate synthetic data for testing strategies."""
    pipeline = _get_pipeline()
    ticks = pipeline.generate_synthetic_dataset(slug, days, interval)
    return {
        "slug": slug,
        "tick_count": len(ticks),
        "days": days,
        "interval": interval,
    }


@router.get("/data/cached")
async def list_cached_data() -> dict[str, int]:
    """List all cached datasets and their tick counts."""
    return _get_pipeline().list_cached()


# ──────────────────────────────────────────
# Run Backtest
# ──────────────────────────────────────────


@router.post("/run")
async def run_backtest(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """
    Run a backtest with a specified strategy and data.

    Body:
    {
        "strategy": "momentum",
        "strategy_params": {"entry_threshold": 0.03, "exit_loss": 0.05},
        "slug": "chiefs-super-bowl-lxi",
        "initial_capital": 10000,
        "slippage_bps": 5,
        "use_synthetic": true,
        "synthetic_days": 30
    }
    """
    pipeline = _get_pipeline()

    strategy_name = params["strategy"]
    strategy_params = params.get("strategy_params", {})
    slug = params["slug"]
    initial_capital = params.get("initial_capital", 10_000.0)
    slippage_bps = params.get("slippage_bps", 5.0)

    # Get or generate data
    if params.get("use_synthetic", False):
        days = params.get("synthetic_days", 30)
        ticks = pipeline.generate_synthetic_dataset(slug, days)
    else:
        ticks = pipeline.get_ticks(slug)
        if not ticks:
            ticks = await pipeline.fetch_pm_us_history(slug)

    if not ticks:
        return {"error": f"No data available for {slug}"}

    # Run backtest
    strategy = get_strategy(strategy_name, **strategy_params)
    engine = BacktestEngine(
        initial_capital=initial_capital,
        slippage_bps=slippage_bps,
    )
    result = engine.run(strategy, ticks)

    return {
        "strategy": result.strategy_name,
        "period": f"{result.start_date} → {result.end_date}",
        "initial_capital": result.initial_capital,
        "final_capital": result.final_capital,
        "total_return": result.total_return,
        "total_return_pct": result.total_return_pct,
        "total_trades": result.total_trades,
        "winning_trades": result.winning_trades,
        "losing_trades": result.losing_trades,
        "win_rate": result.win_rate,
        "max_drawdown": result.max_drawdown,
        "max_drawdown_pct": result.max_drawdown_pct,
        "sharpe_ratio": result.sharpe_ratio,
        "total_fees": result.total_fees,
        "avg_trade_pnl": result.avg_trade_pnl,
        "best_trade": result.best_trade,
        "worst_trade": result.worst_trade,
        "equity_curve": result.equity_curve[-100:],  # Last 100 points for UI
        "trades": result.trades[-50:],  # Last 50 trades
    }


# ──────────────────────────────────────────
# Strategy Comparison
# ──────────────────────────────────────────


@router.post("/compare")
async def compare_strategies(
    params: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """
    Compare multiple strategies against the same dataset.

    Body:
    {
        "strategies": ["momentum", "mean_reversion", "kelly_criterion"],
        "slug": "chiefs-super-bowl-lxi",
        "initial_capital": 10000,
        "use_synthetic": true,
        "synthetic_days": 90
    }
    """
    pipeline = _get_pipeline()
    strategy_names = params["strategies"]
    slug = params["slug"]
    capital = params.get("initial_capital", 10_000.0)

    # Generate or fetch data (once, shared across strategies)
    if params.get("use_synthetic", False):
        days = params.get("synthetic_days", 90)
        ticks = pipeline.generate_synthetic_dataset(slug, days)
    else:
        ticks = pipeline.get_ticks(slug)
        if not ticks:
            ticks = await pipeline.fetch_pm_us_history(slug)

    if not ticks:
        return {"error": f"No data available for {slug}"}

    results = []
    for name in strategy_names:
        try:
            strategy = get_strategy(name)
            engine = BacktestEngine(initial_capital=capital)
            result = engine.run(strategy, ticks)
            results.append({
                "strategy": result.strategy_name,
                "return_pct": result.total_return_pct,
                "sharpe": result.sharpe_ratio,
                "max_dd_pct": result.max_drawdown_pct,
                "win_rate": result.win_rate,
                "total_trades": result.total_trades,
                "final_capital": result.final_capital,
                "total_fees": result.total_fees,
            })
        except Exception as e:
            results.append({"strategy": name, "error": str(e)})

    # Rank by return
    results.sort(key=lambda r: r.get("return_pct", -999), reverse=True)

    return {
        "slug": slug,
        "tick_count": len(ticks),
        "initial_capital": capital,
        "results": results,
    }
