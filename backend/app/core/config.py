"""
Application configuration.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Polymarket Platform"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/polymarket"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Polymarket US API
    polymarket_key_id: str = ""
    polymarket_secret_key: str = ""
    polymarket_api_base: str = "https://api.polymarket.us"
    polymarket_gateway_base: str = "https://gateway.polymarket.us"
    polymarket_ws_private: str = "wss://api.polymarket.us/v1/ws/private"
    polymarket_ws_markets: str = "wss://api.polymarket.us/v1/ws/markets"

    # Falcon API (Polymarket Analytics)
    falcon_api_token: str = ""
    falcon_api_base: str = "https://narrative.agent.heisenberg.so/v2"

    # Polymarket International (Crypto / Polygon)
    poly_intl_private_key: str = ""
    poly_intl_funder_address: str = ""

    # Kalshi API
    kalshi_api_key_id: str = ""
    kalshi_private_key_path: str = ""

    # Rate Limits (per 10 seconds unless noted)
    rate_limit_trading: int = 440
    rate_limit_query: int = 55
    rate_limit_global: int = 2000
    rate_limit_public_per_second: int = 20

    # Risk Management Defaults
    max_position_size: int = 1000  # max contracts per market
    max_total_exposure: float = 10000.0  # max portfolio value in USD
    max_daily_loss: float = 500.0  # daily drawdown circuit breaker
    buying_power_reserve_pct: float = 0.20  # keep 20% of buying power free
    max_concentration_pct: float = 0.25  # no single market > 25% of portfolio
    max_spread_threshold: float = 0.10  # reject orders in markets with spread > 10%
    min_liquidity_depth: int = 100  # reject if book depth < 100 contracts

    # Data Ingestion
    market_refresh_interval_seconds: int = 300  # 5 minutes
    series_refresh_interval_seconds: int = 1800  # 30 minutes

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
