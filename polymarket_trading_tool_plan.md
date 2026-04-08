# Polymarket Trading Tool & Market Analysis Platform — Comprehensive Plan

> **Project:** Polymarket Trading & Analytics Platform
> **Date:** April 2026
> **Status:** Draft — Awaiting Approval

---

## 1. Executive Summary

This document outlines a comprehensive plan for building an integrated **Polymarket trading tool** and **market analysis platform**. The system will combine automated trading capabilities on Polymarket US (CFTC-regulated, fiat) with deep analytical intelligence sourced from every available API, SDK, data pipeline, and community tool in the ecosystem.

### Core Objectives

1. **Trade Execution Engine** — Programmatic order management (limit, market, IOC, FOK) via the official Polymarket US API with full portfolio/margin awareness
2. **Market Analysis Dashboard** — Real-time and historical analytics across markets, events, and series with institutional-grade visualisations
3. **Cross-Venue Arbitrage Scanner** — Automated detection of price discrepancies between Polymarket and Kalshi
4. **Sentiment & Signal Intelligence** — Social media sentiment scoring, narrative vs price divergence detection, and smart money tracking
5. **Strategy Backtesting Engine** — Historical data-driven strategy validation before deploying capital
6. **AI-Assisted Decision Making** — Claude MCP integration and autonomous agent capabilities for research and trade suggestions

---

## 2. Platform & Ecosystem Inventory

Every external resource this platform will leverage:

### 2.1 Official APIs

| API | Base URL | Auth | Purpose |
|---|---|---|---|
| **Polymarket US — Trading** | `https://api.polymarket.us` | API Key + Ed25519 Signature | Order placement, portfolio, account balances |
| **Polymarket US — Market Data** | `https://gateway.polymarket.us` | None (public) | Markets, events, series, sports, search, order books, BBO |
| **Polymarket US — Private WebSocket** | `wss://api.polymarket.us/v1/ws/private` | API Key + Ed25519 | Real-time orders, positions, balance updates |
| **Polymarket US — Market WebSocket** | `wss://api.polymarket.us/v1/ws/markets` | API Key + Ed25519 | Real-time order book depth, BBO streaming |
| **Falcon API (Polymarket Analytics)** | `https://narrative.agent.heisenberg.so/v2` | Bearer Token | Trader intelligence, cross-venue analysis, sentiment, leaderboard |

### 2.2 Official SDKs

| Package | Language | Install | Target |
|---|---|---|---|
| `polymarket-us` | Python | `pip install polymarket-us` | Polymarket US (fiat, CFTC) — **PRIMARY** |
| `polymarket-us` | TypeScript | `npm install polymarket-us` | Polymarket US (fiat, CFTC) — **PRIMARY** |
| `py-clob-client` | Python | `pip install py-clob-client` | Polymarket International (crypto) — **ACTIVE** |
| `@polymarket/clob-client` | TypeScript | `npm install @polymarket/clob-client` | Polymarket International (crypto) — **ACTIVE** |

### 2.3 Community Tools & Data Pipelines

| Tool | Purpose | Integration Point |
|---|---|---|
| **poly_data** (`warproxxx/poly_data`) | End-to-end historical trade data pipeline (markets.csv, trades.csv) | Backtesting engine, historical analysis |
| **polymarket-data-scraper** (`TenghanZhong`) | Multi-sport & crypto per-minute price snapshots, PostgreSQL storage | Sports market analysis, time-series DB |
| **polymarket-apis** (PyPI) | Unified Pydantic-validated wrapper for CLOB, Gamma, WebSocket, GraphQL | Data normalisation layer |
| **Oddpool** | Cross-venue aggregation, arbitrage detection, historical archives | Competitive intelligence, arbitrage validation |
| **Polymarket Subgraph** | On-chain indexing of trades, volume, users, liquidity | Deep on-chain analytics |

### 2.4 AI & MCP Servers

| Tool | Purpose |
|---|---|
| **Falcon MCP (Claude)** | Natural language queries against all Falcon data suites |
| **caiovicentino/polymarket-mcp-server** | 45-tool MCP server: discovery, trading, analysis, portfolio |
| **IQAIcom/mcp-polymarket** | Full-featured MCP: market data, pricing, order books, trading |
| **Polymarket/agents** | Official AI agent framework (Polymarket.py, Gamma.py, Chroma.py) |

### 2.5 Reference Trading Bots (Architecture Study)

| Bot | Key Learnings |
|---|---|
| **polymarket-trading-bot** (`discountry`) | Gasless transactions, WebSocket patterns, flash crash strategy |
| **BTC-15-Minute-Trading-Bot** (`aulekator`) | 7-phase algo pipeline, multi-source signals, Grafana/Prometheus monitoring |
| **polybot** (`ent0n29`) | Microservices (Kafka, ClickHouse, Grafana), strategy reverse-engineering |
| **polymarket-automated-mm** (`terrytrl100`) | Market making, reward-optimised pricing, intelligent cancellation |
| **poly-market-maker** (Official) | Official CLOB market maker, bands/AMM strategy |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND DASHBOARD                          │
│  (Next.js / React + D3.js / Recharts)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Market   │ │ Trading  │ │ Arbitrage│ │Sentiment │ │ Portfolio│ │
│  │ Explorer │ │ Terminal │ │ Scanner  │ │ Signals  │ │ Manager  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ REST + WebSocket
┌─────────────────────────────▼───────────────────────────────────────┐
│                        BACKEND API LAYER                            │
│  (Python / FastAPI)                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ │
│  │ Trading     │ │ Analytics   │ │ Arbitrage   │ │ Signal       │ │
│  │ Engine      │ │ Engine      │ │ Engine      │ │ Aggregator   │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬───────┘ │
│         │               │               │               │          │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼───────┐ │
│  │ Risk        │ │ Backtest    │ │ Data        │ │ AI / MCP     │ │
│  │ Manager     │ │ Engine      │ │ Ingestor    │ │ Interface    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ PostgreSQL   │ │ Redis        │ │ TimescaleDB  │               │
│  │ (positions,  │ │ (cache, WS   │ │ (OHLCV, time │               │
│  │  orders,     │ │  state,      │ │  series)     │               │
│  │  strategies) │ │  rate limits)│ │              │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│  │ Polymarket │ │ Falcon     │ │ Kalshi     │ │ News /     │      │
│  │ US API     │ │ API        │ │ (via       │ │ Social     │      │
│  │ + WS       │ │            │ │ Oddpool)   │ │ Feeds      │      │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.1 Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | Python 3.12+ / FastAPI | Native `polymarket-us` SDK, async WebSocket support, Falcon API integration |
| **Frontend** | Next.js 15 + React 19 | SSR for SEO, real-time WS rendering, component ecosystem |
| **Charting** | D3.js + Recharts + Lightweight Charts (TradingView) | Depth charts, candlestick-style probability charts, order book heatmaps |
| **Primary DB** | PostgreSQL 16 + TimescaleDB | Relational data + hypertables for time-series price/volume data |
| **Cache** | Redis 7 | WebSocket state, rate limit tracking, BBO cache, session management |
| **Task Queue** | Celery + Redis | Background data ingestion, scheduled analytics, alert delivery |
| **Monitoring** | Prometheus + Grafana | System health, API latency, trading engine metrics |
| **AI Layer** | Claude MCP + Falcon MCP Server | Natural language market queries, research assistance |

---

## 4. Module Design — Deep Dive

### 4.1 Data Ingestion & Market Cache

The data layer is the foundation. Every other module depends on clean, real-time, and historical data.

#### Real-Time Ingestion (WebSocket)

Two persistent WebSocket connections to Polymarket US:

| Connection | Endpoint | Subscriptions | Data Stored |
|---|---|---|---|
| **Private WS** | `wss://api.polymarket.us/v1/ws/private` | `SUBSCRIPTION_TYPE_ORDER`, `SUBSCRIPTION_TYPE_POSITION`, `SUBSCRIPTION_TYPE_ACCOUNT_BALANCE` | Local order state, position snapshots, balance cache |
| **Market WS** | `wss://api.polymarket.us/v1/ws/markets` | `SUBSCRIPTION_TYPE_MARKET_DATA` (full depth), `SUBSCRIPTION_TYPE_MARKET_DATA_LITE` (BBO only) | Order book snapshots, BBO ticks into TimescaleDB |

#### REST Polling (Supplementary)

| Endpoint | Frequency | Purpose |
|---|---|---|
| `GET /v1/events` | Every 5 minutes | Discover new events, update metadata cache |
| `GET /v1/markets` | Every 5 minutes | Discover new markets, update slugs/states |
| `GET /v1/series` | Every 30 minutes | Update series hierarchy |
| `GET /v1/sports/leagues/{slug}/events` | Every 5 minutes | Sports-specific event discovery |
| `GET /v1/search` | On-demand | User-initiated search |

#### Historical Data Pipeline

Leverage **poly_data** (`warproxxx/poly_data`) for deep historical coverage:

```python
# Orchestration: run on schedule (daily) or on-demand
# 1. Fetch market metadata -> markets.csv
# 2. Scrape order-filled events from Goldsky subgraph -> goldsky/orderFilled.csv
# 3. Process into structured trades -> processed/trades.csv
# 4. Load into TimescaleDB hypertables for backtesting
```

Additionally, adapt patterns from **polymarket-data-scraper** (`TenghanZhong`) for per-minute sports market snapshots with live score tracking.

#### Rate Limit Management

Implement a Redis-backed rate limiter respecting all documented limits:

| Endpoint Group | Limit | Strategy |
|---|---|---|
| Trading (place/cancel/modify) | 440 req / 10s each | Token bucket with burst allowance |
| Query (open orders, order by ID) | 55 req / 10s | Leaky bucket |
| Global (all combined) | 2,000 req / 10s | Global counter |
| Public (unauthenticated) | 20 req / s / IP | Per-IP counter |

Exponential backoff on `429` responses as per documentation.

---

### 4.2 Trading Engine

#### Order Management

Full implementation of all Polymarket US order types and TIF options:

| Feature | Implementation |
|---|---|
| **Limit Orders** | `ORDER_TYPE_LIMIT` with configurable price |
| **Market Orders** | Marketable limit at best available price |
| **Time-in-Force** | GTC, GTD, IOC, FOK — all four supported |
| **Order Preview** | `POST /v1/order/preview` before execution for fee/fill estimation |
| **Bulk Cancel** | `POST /v1/orders/open/cancel` for emergency position flattening |
| **Position Close** | `POST /v1/order/close-position` for clean exit |
| **Order Modify** | `POST /v1/order/{id}/modify` for price/size adjustments |

#### Smart Order Routing

1. Fetch full book via `GET /v1/markets/{slug}/book`
2. Calculate price impact for desired quantity
3. If impact > threshold: split into smaller IOC tranches
4. If spread > threshold: place limit order at mid-price
5. Apply fee estimation using: `Fee = 0.05 * C * p * (1-p)`

#### Fee Calculator

Implement the symmetric fee formula from the documentation:

```
Taker Fee = 0.05 x contracts x price x (1 - price)
Maker Rebate = -0.0125 x contracts x price x (1 - price)
Weekly Taker Rebate = 50% of taker fees (applied weekly)
```

All calculations use banker's rounding (round half to even).

#### Portfolio Margin Awareness

The engine must understand and exploit both margin optimisations:

1. **Mutually Exclusive Collateral Return** — Detect when short positions span the same mutually exclusive event (e.g., election candidates) and calculate true margin requirement (max of individual shorts, not sum)
2. **Directional Collateral Return** — Detect when lower-ranked longs offset higher-ranked shorts in directional events (spreads, totals, price levels) and reduce margin accordingly

---

### 4.3 Market Analysis Engine

#### Real-Time Analytics

| Metric | Source | Visualisation |
|---|---|---|
| **Market Price (probability)** | WS `MARKET_DATA_LITE` | Live line chart with historical overlay |
| **Order Book Depth** | WS `MARKET_DATA` | Depth chart (bids/asks stacked) |
| **BBO Spread** | WS `MARKET_DATA_LITE` | Spread time-series, heatmap by market |
| **Volume** | REST `/v1/markets` + historical | Bar chart with moving averages |
| **Market State** | REST `/v1/markets/{slug}` | Status badges (Open, Suspended, Halted, Expired) |
| **Live Sports Data** | REST sports endpoints | Score, period, game clock overlay on charts |

#### Probability Shift Detection

Monitor for significant price moves (configurable threshold, e.g., 5% move) and fire alerts via Discord/email.

#### Market Screening & Filtering

Configurable screener using combined REST + Falcon API data:

- Minimum volume filter
- Market state filter (open/closed)
- Sport / league / series filter
- Price range (probability band)
- Spread threshold
- Sentiment divergence (via Falcon)
- Cross-venue price gap (via Falcon)

---

### 4.4 Cross-Venue Arbitrage Scanner

#### Data Sources

| Venue | Data Source | Method |
|---|---|---|
| Polymarket US | Official API (real-time WS + REST) | Direct |
| Kalshi | Falcon API `/v2/cross/compare` | Via Falcon |
| Cross-venue validation | Oddpool | Supplementary |

#### Arbitrage Detection Logic

1. Query Falcon `/v2/cross/compare` with topic, venues `["polymarket", "kalshi"]`, metrics `["price_gap", "volume_ratio"]`
2. Filter for actionable gaps exceeding round-trip fee threshold
3. Estimate fees: PM fee using `0.05 * p * (1-p)` + approximate Kalshi fee
4. Alert on net-positive opportunities with volume/liquidity assessment

#### Same-Platform Arbitrage (Complete Set)

For mutually exclusive events with N outcomes, check if buying all outcomes at current ask prices costs less than $1.00 (guaranteed profit at settlement). Pattern documented in the **polybot** reference architecture.

---

### 4.5 Sentiment & Signal Intelligence

#### Falcon Sentiment Integration

Use `/v2/signals/sentiment` with configurable sources (`twitter`, `reddit`, `news`) and time windows (`1h`, `6h`, `24h`, `7d`).

Key response fields:
- `sentiment_score` (0.0–1.0)
- `price_sentiment_divergence` — **the most actionable signal**
- `mention_volume`, `narrative_trend`, `confidence`, `top_influencer`

#### Price-Sentiment Divergence Alerts

| Divergence | Interpretation | Suggested Action |
|---|---|---|
| `< -0.10` | Sentiment much more bearish than price | Consider SHORT |
| `-0.10 to +0.10` | Aligned | No signal |
| `> +0.10` | Sentiment much more bullish than price | Consider LONG |

#### Smart Money / Whale Tracking

Via Falcon `/v2/traders/stats` — query top F-Score wallets from the leaderboard, track their PnL, ROI, win rate, drawdown, and active positions for copy-trading signals.

---

### 4.6 Risk Management System

| Control | Implementation |
|---|---|
| **Max Position Size** | Per-market contract limit (configurable) |
| **Max Total Exposure** | Global portfolio value cap |
| **Max Loss Per Day** | Daily drawdown circuit breaker — cancel all orders + alert |
| **Buying Power Reserve** | Never deploy more than X% of buying power |
| **Concentration Limit** | No single market > Y% of portfolio value |
| **Spread Gate** | Reject orders in markets with spread > Z |
| **Liquidity Gate** | Reject orders where book depth < minimum contracts |
| **Kill Switch** | Emergency `POST /v1/orders/open/cancel` + close all positions |

#### Kelly Criterion Position Sizing

Optimal position sizing based on estimated edge and odds, using half-Kelly for safety.

---

### 4.7 Backtesting Engine

#### Data Sources

| Source | Coverage | Fields |
|---|---|---|
| **poly_data** pipeline | Full historical | timestamp, maker, taker, amounts, token IDs, tx hash |
| **polymarket-data-scraper** | Sports (MLB, NBA) | Per-minute bid/ask snapshots, live scores |
| **Falcon API** | Historical market data | Prices, volume, outcomes, metadata |
| **TimescaleDB** (own collection) | From deployment date | BBO ticks, depth snapshots, fills |

#### Built-In Strategies for Backtesting

| Strategy | Description |
|---|---|
| **Mean Reversion** | Fade sharp probability moves, exit at mean |
| **Momentum** | Follow sustained directional moves |
| **Sentiment Divergence** | Trade when price != sentiment (Falcon signal) |
| **Cross-Venue Arb** | Simulated dual-venue arbitrage execution |
| **Market Making** | Simulate bid/ask quoting with inventory management |
| **Flash Crash** | Buy extreme dips in high-liquidity markets |

---

### 4.8 AI Agent & MCP Integration

#### Claude MCP Server

Deploy both Falcon MCP (analytics) and Polymarket MCP (trading) servers for natural language interaction with the platform.

#### AI-Powered Features

| Feature | Implementation |
|---|---|
| **"What should I trade?"** | LLM analyses top markets by divergence, volume, sentiment |
| **Market Research Summaries** | RAG over news + Falcon sentiment — structured brief |
| **Trade Explanation** | Post-hoc analysis of why a trade was suggested |
| **Portfolio Review** | AI-generated commentary on current positions and risk |

Build on the official `Polymarket/agents` framework (Polymarket.py, Gamma.py, Chroma.py for ChromaDB vectorisation).

---

## 5. Dashboard UI — Key Views

| View | Key Features |
|---|---|
| **Market Explorer** | Searchable/filterable list; sort by volume, probability, spread, sentiment; quick-view cards with BBO, 24h change |
| **Trading Terminal** | TradingView-style probability chart; real-time order book depth; order entry panel; order preview with fees; open orders with modify/cancel |
| **Arbitrage Dashboard** | Cross-venue price gap table; net gap after fees; volume ratio; historical gap chart; one-click alert setup |
| **Sentiment & Signals** | Sentiment gauge per market; price vs sentiment divergence overlay; mention volume sparklines; top influencer feed |
| **Portfolio Manager** | Balance and buying power; open positions with live P&L; margin utilisation (ME + directional collateral returns); ROI, win rate, Sharpe, drawdown |
| **Whale Tracker** | F-Score leaderboard; wallet drill-down; copy-trading signal feed |
| **Backtesting Lab** | Strategy selector and parameter tuning; equity curve, drawdown chart, trade log; strategy comparison table |

---

## 6. Incentive Programme Optimisation

The platform should actively optimise for all four Polymarket incentive programmes:

| Programme | Strategy |
|---|---|
| **Volume Incentive** | Track trading volume; surface progress toward reward tiers |
| **Liquidity Incentive** | Place resting orders in thin markets; track reward accrual |
| **Fill Incentive** | Prioritise resting orders that are likely to fill |
| **Market Maker (if approved)** | Dedicated market making mode with spread management and reward tracking |

---

## 7. Deployment & Infrastructure

| Component | Hosting | Rationale |
|---|---|---|
| **Backend API** | DigitalOcean VM (US-East) | Low latency to `api.polymarket.us` |
| **PostgreSQL + TimescaleDB** | Same VM or managed DB | Co-located for speed |
| **Redis** | Same VM | Cache locality |
| **Frontend** | Vercel or same VM (Nginx) | CDN for static assets |
| **Monitoring** | Grafana Cloud or self-hosted | Prometheus metrics, alerting |
| **CI/CD** | GitHub Actions | Automated testing, deployment |

---

## 8. Phased Delivery Timeline

### Phase 1 — Foundation (Weeks 1–3)
- [ ] Project scaffolding (FastAPI backend, Next.js frontend, PostgreSQL, Redis)
- [ ] Polymarket US SDK integration (`polymarket-us` Python)
- [ ] Market data REST ingestion (events, markets, series, sports)
- [ ] WebSocket connections (market data + private)
- [ ] Data models + TimescaleDB hypertables for BBO/trade time-series
- [ ] Basic market explorer UI

### Phase 2 — Trading Engine (Weeks 4–6)
- [ ] Order management (create, cancel, modify, preview, close-position)
- [ ] Trading terminal UI (order book, order entry, positions)
- [ ] Fee calculator (symmetric formula + maker rebate)
- [ ] Portfolio margin calculator (ME + directional collateral return)
- [ ] Risk management controls (position limits, kill switch)
- [ ] Real-time sync via private WebSocket

### Phase 3 — Analytics & Intelligence (Weeks 7–9)
- [ ] Falcon API integration (all four data suites)
- [ ] Sentiment analysis view
- [ ] Cross-venue arbitrage scanner
- [ ] Whale tracker / F-Score leaderboard
- [ ] Probability shift alerts
- [ ] Market screener with combined filters

### Phase 4 — Backtesting & Strategy (Weeks 10–12)
- [ ] Historical data pipeline (poly_data integration + own collection)
- [ ] Backtesting engine with fee-accurate simulation
- [ ] Built-in strategy library
- [ ] Backtesting lab UI
- [ ] Strategy performance comparison tools

### Phase 5 — AI & Automation (Weeks 13–15)
- [ ] Claude MCP server deployment
- [ ] AI research agent (news vectorisation, structured market briefs)
- [ ] AI-assisted trade suggestions
- [ ] Autonomous trading mode (paper trading first, then live)
- [ ] Incentive programme tracking

### Phase 6 — Polish & Production (Weeks 16–18)
- [ ] Grafana/Prometheus monitoring stack
- [ ] Alerting (Discord/email)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation and deployment automation

---

## 9. Resolved Decisions

| Question | Decision |
|---|---|
| **Target Platform** | Both **Polymarket US** (fiat) AND **Polymarket International** (crypto) |
| **Hosting** | Deferred — local development only for now |
| **Database** | Fresh PostgreSQL + TimescaleDB instance |
| **AI Integration** | Full capability — manual research AND autonomous trading agent |
| **Kalshi** | Yes — direct Kalshi API integration for cross-venue arbitrage execution |
| **Falcon API** | Will subscribe later — build integration now, activate when ready |
| **Sports Coverage** | All sports (NFL, NBA, NHL, MLB, MLS, CBB, Tennis, Golf) |
| **Market Making** | No — will not apply for Market Maker Programme |

---

## 10. Success Metrics

| Metric | Target |
|---|---|
| **Data Freshness** | BBO updates within 100ms of WebSocket receipt |
| **Order Execution** | Order placed within 200ms of signal generation |
| **Arbitrage Detection** | Cross-venue gaps detected within 5 seconds |
| **Uptime** | 99.5%+ for data ingestion and trading engine |
| **Backtesting Speed** | 1 year of minute-level data in < 60 seconds |
| **Dashboard Load Time** | < 2 seconds for any view |

---

*This plan leverages every documented resource: the official Polymarket US REST API (15+ endpoints), both WebSocket streams, the Falcon Analytics API (4 data suites), both official SDKs, 5 community data pipelines and trading bots for architectural reference, 4 MCP servers, the official AI agents framework, and 5 analytics platforms for competitive intelligence.*
