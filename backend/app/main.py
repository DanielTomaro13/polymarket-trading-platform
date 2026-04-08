"""
Main FastAPI application.
Mounts all route modules and manages service lifecycle.
Supports both Polymarket US and International, plus Kalshi.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, analytics, backtest, markets, trading
from app.core.config import settings
from app.services.falcon_client import FalconClient
from app.services.kalshi_client import KalshiClient
from app.services.margin_calculator import MarginCalculator
from app.services.polymarket_client import PolymarketClient
from app.services.polymarket_intl_client import PolymarketInternationalClient
from app.services.risk_manager import RiskManager
from app.services.data_pipeline import HistoricalDataPipeline
from app.services.ai_agent import AIResearchAgent
from app.websocket.manager import WebSocketManager

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

# Global service instances
polymarket_client: PolymarketClient | None = None
polymarket_intl_client: PolymarketInternationalClient | None = None
falcon_client: FalconClient | None = None
kalshi_client: KalshiClient | None = None
risk_manager: RiskManager | None = None
margin_calculator: MarginCalculator | None = None
ws_manager: WebSocketManager | None = None
data_pipeline: HistoricalDataPipeline | None = None
ai_agent: AIResearchAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Startup and shutdown lifecycle manager."""
    global polymarket_client, polymarket_intl_client, falcon_client
    global kalshi_client, risk_manager, margin_calculator, ws_manager, data_pipeline, ai_agent

    logger.info("Starting Polymarket Platform v%s", settings.app_version)

    # Initialise all service clients
    polymarket_client = PolymarketClient()
    polymarket_intl_client = PolymarketInternationalClient()
    falcon_client = FalconClient()
    kalshi_client = KalshiClient()
    risk_manager = RiskManager()
    margin_calculator = MarginCalculator()
    ws_manager = WebSocketManager()
    data_pipeline = HistoricalDataPipeline()
    ai_agent = AIResearchAgent()

    # Inject clients into route modules
    markets.init_client(polymarket_client)
    trading.init_client(polymarket_client)
    trading.init_risk_manager(risk_manager)
    trading.init_margin_calculator(margin_calculator)
    analytics.init_client(falcon_client)
    backtest.init_pipeline(data_pipeline)
    agent.init_agent(ai_agent)

    # Store additional clients on app state for route access
    app.state.polymarket_intl = polymarket_intl_client
    app.state.kalshi = kalshi_client
    app.state.ws_manager = ws_manager

    # Start WebSocket connections
    await ws_manager.start()

    logger.info(
        "All services initialised — PM-US: %s, PM-Intl: %s, Falcon: %s, Kalshi: %s",
        "auth" if settings.polymarket_key_id else "public",
        "auth" if settings.poly_intl_private_key else "public",
        "active" if settings.falcon_api_token else "inactive",
        "auth" if settings.kalshi_api_key_id else "public",
    )
    yield

    # Cleanup
    logger.info("Shutting down services...")
    if ws_manager:
        await ws_manager.stop()
    if polymarket_client:
        await polymarket_client.close()
    if polymarket_intl_client:
        await polymarket_intl_client.close()
    if falcon_client:
        await falcon_client.close()
    if kalshi_client:
        await kalshi_client.close()
    if data_pipeline:
        await data_pipeline.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Polymarket Trading Tool & Market Analysis Platform. "
        "Supports Polymarket US (fiat), Polymarket International (crypto), "
        "and Kalshi for cross-venue arbitrage. Powered by Falcon Analytics "
        "for sentiment, trader intelligence, and cross-market signals."
    ),
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(markets.router, prefix="/api")
app.include_router(trading.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(backtest.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "platforms": "polymarket-us,polymarket-intl,kalshi",
    }
