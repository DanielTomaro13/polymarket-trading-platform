# Polymarket Trading & Analytics Platform

A high-performance algorithmic trading platform and market intelligence dashboard built for prediction markets. 

This platform aggregates data and execution across **Polymarket US**, **Polymarket International**, and **Kalshi**, while integrating with **Falcon Analytics** for real-time sentiment intelligence and AI-driven trade suggestions.

---

## ⚡ Key Features

### 1. Multi-Venue Execution Core
- **Polymarket US**: REST execution and market data for CFTC-regulated fiat markets.
- **Polymarket International**: Gamma API metadata, py-clob-client order management, and L2 depth.
- **Kalshi**: Fully authenticated integration (RSA-PSS) for cross-venue arbitrage.
- **WebSocket Manager**: Maintains persistent, authenticated, auto-reconnecting `Ed25519` private and market streams.

### 2. Risk & Margin Engine
- **Pre-Trade Risk Management**: 8 mandatory checks before any order execution (Position limits, buying power, daily loss circuit breakers).
- **Emergency Kill Switch**: Panic-close all positions gracefully across venues.
- **Symmetric Fee Calculation**: Real-time modeling of Polymarket's `Taker_Rate × Quantity × Price × (1 - Price)` fee structure.
- **Mutually Exclusive Margin**: Models collateral return offsets for complete-set positions (e.g., buying every team in a tournament) to maximize capital efficiency.

### 3. Intelligence & Arbitrage
- **Cross-Venue Scanner**: Calculates fee-adjusted Net Gaps between Polymarket and Kalshi to highlight risk-free arbitrage.
- **Complete-Set Arbitrage**: Identifies situations where buying the entire field results in a guaranteed yield.
- **Falcon Sentiment Analysis**: Real-time divergence mapping (Price vs. Social Sentiment).

### 4. Algorithmic Backtesting Lab
- **Simulation Engine**: Historical tick ingestion with realistic slippage models.
- **Built-In Strategies**: Test and tune algorithms including *Momentum*, *Mean Reversion*, *Spread Capture*, and the *Kelly Criterion*.
- **Metrics**: Generates Sharpe Ratios, Maximum Drawdown, Win Rates, and Equity Curves.

### 5. AI Autonomous Agent (Claude MCP)
- **Market Research**: AI synthesizes live depth, arbitrage gaps, and Falcon social sentiment into a structured "Fair Value".
- **Trade Suggestion Engine**: Ranks opportunities based on `Edge × Confidence`.
- **MCP Integration**: Fully exposed tools that allow Claude (Model Context Protocol) to natively analyze and trade for you.

---

## 🏗 Architecture & Tech Stack

The workspace is structured into a separated Backend API and a Frontend Dashboard.

### Backend (`/backend`)
- **Framework**: FastAPI (Python 3.12+)
- **ORM & DB**: Async SQLAlchemy + PostgreSQL + TimescaleDB (for tick data).
- **Design Pattern**: Dependency-injected service clients managed by FastAPI Lifespans.

### Frontend (`/frontend`)
- **Framework**: Next.js 16 (App Router) + TypeScript.
- **Styling**: Vanilla CSS Modules featuring a premium dark-themed, glassmorphic design system.
- **State Management**: React Hooks + native fetch.

---

## 🚀 Quick Start

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment variables and add your API credentials:
```bash
cp .env.example .env
```
Ensure you generate and provide:
- Polymarket US / Intl API Keys + Passphrases + L1 Wallet Private Keys (for Ed25519 signing).
- Kalshi Private Key path.
- Falcon API Token.

### 3. Start Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation available at: `http://localhost:8000/docs`

### 4. Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://localhost:3000`

---

## 📂 Project Structure

```text
polymarket/
├── backend/                     # High-performance FastAPI trading core
│   ├── app/
│   │   ├── api/routes/          # 45+ endpoints (markets, trading, agent, backtest)
│   │   ├── core/                # Settings, auth logic, and DB connection
│   │   ├── models/              # SQLAlchemy models (Order, Position, Tick)
│   │   ├── services/            # Client wrappers (Polymarket, Kalshi, Falcon, AI Agent)
│   │   └── websocket/           # Async WS manager for depth & fills
│   ├── data/                    # Historical ticks and DB migrations
│   └── tests/
│
└── frontend/                    # Next.js Analytics & Trading Terminal
    └── app/
        ├── arbitrage/           # Scanning dashboard
        ├── backtest/            # Algorithmic strategy lab
        ├── learn/               # Educational documentation view
        ├── portfolio/           # Profit/Loss and margin utilization
        ├── sentiment/           # AI divergence mapping
        ├── trading/             # Live chart, L2 depth, and order ticket
        └── page.tsx             # Main Market Explorer
```

---

## 🛡 Disclaimer
This software connects directly to regulated and unregulated prediction markets that mandate strict geographic compliance. It is provided for educational and research purposes. Always verify API fees and test algorithms in sandbox environments prior to deploying real capital.
