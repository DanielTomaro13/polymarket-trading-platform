"""
Trading API routes.
Authenticated endpoints for order management, portfolio, account,
risk management, and margin calculation.
"""

from typing import Any

from fastapi import APIRouter, Body, Path, Query

from app.services.fee_calculator import estimate_trade_fees
from app.services.margin_calculator import MarginCalculator
from app.services.polymarket_client import PolymarketClient
from app.services.risk_manager import PortfolioState, PositionInfo, RiskManager

router = APIRouter(prefix="/trading", tags=["Trading"])

_client: PolymarketClient | None = None
_risk_manager: RiskManager | None = None
_margin_calculator: MarginCalculator | None = None


def init_client(client: PolymarketClient) -> None:
    global _client
    _client = client


def init_risk_manager(rm: RiskManager) -> None:
    global _risk_manager
    _risk_manager = rm


def init_margin_calculator(mc: MarginCalculator) -> None:
    global _margin_calculator
    _margin_calculator = mc


def _get_client() -> PolymarketClient:
    if _client is None:
        raise RuntimeError("PolymarketClient not initialised")
    return _client


def _get_risk_manager() -> RiskManager:
    if _risk_manager is None:
        raise RuntimeError("RiskManager not initialised")
    return _risk_manager


def _get_margin_calculator() -> MarginCalculator:
    if _margin_calculator is None:
        raise RuntimeError("MarginCalculator not initialised")
    return _margin_calculator


# ──────────────────────────────────────────
# Account & Portfolio
# ──────────────────────────────────────────


@router.get("/account/balances")
async def get_balances() -> dict[str, Any]:
    """Get account balances and buying power."""
    return await _get_client().get_balances()


@router.get("/portfolio/positions")
async def get_positions() -> list[dict[str, Any]]:
    """Get all open positions."""
    return await _get_client().get_positions()


@router.get("/portfolio/activities")
async def get_activities() -> list[dict[str, Any]]:
    """Get portfolio activities."""
    return await _get_client().get_activities()


@router.get("/portfolio/margin")
async def get_portfolio_margin() -> dict[str, Any]:
    """
    Calculate portfolio-wide margin including ME collateral offsets.
    Returns total margin required, gross cost, and savings breakdown.
    """
    mc = _get_margin_calculator()
    positions = await _get_client().get_positions()

    # Transform API positions to margin calculator format
    margin_positions = []
    for pos in positions:
        margin_positions.append({
            "slug": pos.get("marketSlug", pos.get("market_slug", "")),
            "event_id": pos.get("eventId", pos.get("event_id", "")),
            "side": "yes" if pos.get("side", "").lower() in ("long", "yes", "buy") else "no",
            "quantity": pos.get("quantity", 0),
            "price": pos.get("avgEntryPrice", pos.get("avg_entry_price", 0)),
            "current_price": pos.get("currentPrice", pos.get("current_price", 0)),
        })

    summary = mc.portfolio_margin(margin_positions)
    return {
        "total_margin_required": summary.total_margin_required,
        "total_gross_cost": summary.total_gross_cost,
        "total_margin_savings": summary.total_margin_savings,
        "positions": summary.positions,
        "me_groups": summary.me_groups,
    }


# ──────────────────────────────────────────
# Orders
# ──────────────────────────────────────────


@router.get("/orders")
async def list_open_orders() -> list[dict[str, Any]]:
    """Get all open orders."""
    return await _get_client().list_open_orders()


@router.post("/orders")
async def create_order(order_params: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Create a new order with risk checks.

    Expected body:
    {
        "marketSlug": "chiefs-super-bowl",
        "intent": "ORDER_INTENT_BUY_LONG",
        "type": "ORDER_TYPE_LIMIT",
        "price": {"value": "0.55", "currency": "USD"},
        "quantity": 100,
        "tif": "TIME_IN_FORCE_GOOD_TILL_CANCEL"
    }
    """
    # Run risk check before submission
    rm = _get_risk_manager()
    slug = order_params.get("marketSlug", "")
    quantity = order_params.get("quantity", 0)
    price_obj = order_params.get("price", {})
    price = float(price_obj.get("value", 0)) if isinstance(price_obj, dict) else float(price_obj)
    intent = order_params.get("intent", "")
    side = "buy" if "BUY" in intent.upper() else "sell"

    # Build portfolio state for risk check
    try:
        balances = await _get_client().get_balances()
        positions = await _get_client().get_positions()

        portfolio = PortfolioState(
            cash_balance=float(balances.get("cashBalance", balances.get("cash_balance", 0))),
            buying_power=float(balances.get("buyingPower", balances.get("buying_power", 0))),
            total_position_value=sum(
                float(p.get("marketValue", p.get("market_value", 0))) for p in positions
            ),
            positions={
                p.get("marketSlug", p.get("market_slug", "")): PositionInfo(
                    slug=p.get("marketSlug", p.get("market_slug", "")),
                    side=p.get("side", "long"),
                    quantity=p.get("quantity", 0),
                    avg_entry_price=float(p.get("avgEntryPrice", p.get("avg_entry_price", 0))),
                    current_price=float(p.get("currentPrice", p.get("current_price", 0))),
                    market_value=float(p.get("marketValue", p.get("market_value", 0))),
                    unrealised_pnl=float(p.get("unrealisedPnl", p.get("unrealised_pnl", 0))),
                )
                for p in positions
            },
        )
    except Exception:
        # If we can't fetch portfolio state, allow with warning
        portfolio = PortfolioState(
            cash_balance=0,
            buying_power=0,
            total_position_value=0,
            positions={},
        )

    risk_check = rm.check_order(
        market_slug=slug,
        side=side,
        quantity=quantity,
        price=price,
        portfolio=portfolio,
    )

    if not risk_check.allowed:
        return {
            "status": "rejected",
            "reason": risk_check.reason,
            "risk_check": "failed",
        }

    # Risk check passed — submit order
    result = await _get_client().create_order(order_params)

    response: dict[str, Any] = {
        "status": "submitted",
        "order": result,
        "risk_check": "passed",
    }
    if risk_check.warnings:
        response["warnings"] = risk_check.warnings

    return response


@router.post("/orders/preview")
async def preview_order(order_params: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Preview an order without execution — returns fee estimate, margin, and risk check."""
    slug = order_params.get("marketSlug", "")
    quantity = order_params.get("quantity", 0)
    price_obj = order_params.get("price", {})
    price = float(price_obj.get("value", 0)) if isinstance(price_obj, dict) else float(price_obj)
    intent = order_params.get("intent", "")
    side = "buy_yes" if "BUY" in intent.upper() and "LONG" in intent.upper() else "buy_no"

    # Fee estimate
    fees = estimate_trade_fees(quantity, price)

    # Margin estimate
    mc = _get_margin_calculator()
    margin = mc.estimate_trade_margin(side=side, quantity=quantity, price=price)

    # Upstream preview (if available)
    try:
        api_preview = await _get_client().preview_order(order_params)
    except Exception:
        api_preview = None

    return {
        "fees": {
            "taker_fee": fees.taker_fee,
            "maker_rebate": fees.maker_rebate,
            "weekly_taker_rebate": fees.weekly_taker_rebate,
            "net_taker_cost": fees.net_taker_cost,
        },
        "margin": {
            "gross_cost": margin.gross_cost,
            "margin_required": margin.margin_required,
            "margin_savings": margin.margin_savings,
            "buying_power_impact": margin.buying_power_impact,
            "max_loss": margin.max_loss,
            "max_gain": margin.max_gain,
            "details": margin.details,
        },
        "api_preview": api_preview,
    }


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str = Path(...)) -> dict[str, Any]:
    """Cancel a specific order."""
    return await _get_client().cancel_order(order_id)


@router.post("/orders/cancel-all")
async def cancel_all_orders() -> dict[str, Any]:
    """Cancel all open orders."""
    return await _get_client().cancel_all_orders()


@router.post("/positions/{market_slug}/close")
async def close_position(market_slug: str = Path(...)) -> dict[str, Any]:
    """Close a position in a specific market."""
    return await _get_client().close_position(market_slug)


# ──────────────────────────────────────────
# Fee Calculator
# ──────────────────────────────────────────


@router.get("/fees/estimate")
async def estimate_fees(
    contracts: int = 100,
    price: float = 0.50,
) -> dict[str, Any]:
    """Estimate trading fees for a given order size and price."""
    result = estimate_trade_fees(contracts, price)
    return {
        "contracts": result.contracts,
        "price": result.price,
        "taker_fee": result.taker_fee,
        "maker_rebate": result.maker_rebate,
        "weekly_taker_rebate": result.weekly_taker_rebate,
        "net_taker_cost": result.net_taker_cost,
    }


# ──────────────────────────────────────────
# Risk Management
# ──────────────────────────────────────────


@router.get("/risk/status")
async def get_risk_status() -> dict[str, Any]:
    """Get current risk manager status (circuit breakers, limits, daily P&L)."""
    return _get_risk_manager().get_status()


@router.post("/risk/kill-switch")
async def activate_kill_switch() -> dict[str, Any]:
    """
    EMERGENCY: Cancel all orders and close all positions.
    This is irreversible and should only be used in emergencies.
    """
    rm = _get_risk_manager()
    result = await rm.kill_switch(_get_client())
    return {"status": "kill_switch_activated", "result": result}


# ──────────────────────────────────────────
# Margin Calculator
# ──────────────────────────────────────────


@router.get("/margin/estimate")
async def estimate_margin(
    side: str = Query("buy_yes", regex="^(buy_yes|buy_no|sell_yes|sell_no)$"),
    quantity: int = Query(100, ge=1),
    price: float = Query(0.50, ge=0.01, le=0.99),
    is_me: bool = Query(False),
) -> dict[str, Any]:
    """Estimate margin for a single trade."""
    mc = _get_margin_calculator()
    result = mc.estimate_trade_margin(
        side=side, quantity=quantity, price=price, is_me=is_me
    )
    return {
        "gross_cost": result.gross_cost,
        "margin_required": result.margin_required,
        "margin_savings": result.margin_savings,
        "buying_power_impact": result.buying_power_impact,
        "max_loss": result.max_loss,
        "max_gain": result.max_gain,
        "details": result.details,
    }
