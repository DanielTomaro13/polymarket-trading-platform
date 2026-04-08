# Polymarket US — Complete Developer & Platform Documentation

> **Source:** [docs.polymarket.us](https://docs.polymarket.us)
> **Last compiled:** April 2026

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [How Prediction Markets Work](#2-how-prediction-markets-work)
3. [Market Hierarchy: Series → Events → Markets](#3-market-hierarchy-series--events--markets)
4. [Glossary of Terms](#4-glossary-of-terms)
5. [Prices & the Order Book](#5-prices--the-order-book)
6. [Orders & Trading Mechanics](#6-orders--trading-mechanics)
7. [Collateral & Margin System](#7-collateral--margin-system)
8. [Portfolio Margin: Mutually Exclusive Collateral Return](#8-portfolio-margin-mutually-exclusive-collateral-return)
9. [Portfolio Margin: Directional Collateral Return](#9-portfolio-margin-directional-collateral-return)
10. [Fee Schedule & Rebates](#10-fee-schedule--rebates)
11. [Incentive Programs](#11-incentive-programs)
12. [API Architecture](#12-api-architecture)
13. [Authentication](#13-authentication)
14. [Rate Limits](#14-rate-limits)
15. [REST API Endpoint Reference](#15-rest-api-endpoint-reference)
16. [WebSocket Streaming](#16-websocket-streaming)
17. [SDKs (TypeScript & Python)](#17-sdks-typescript--python)
18. [Quickstart: End-to-End Walkthrough](#18-quickstart-end-to-end-walkthrough)
19. [Error Handling](#19-error-handling)

---

## 1. Platform Overview

Polymarket US is a CFTC-regulated exchange for trading event contracts on real-world outcomes. It is operated as a **Designated Contract Market (DCM)** and **Derivatives Clearing Organisation (DCO)** under US Commodity Futures Trading Commission oversight. All trading is conducted in US dollars (fiat), with full regulatory compliance.

### Polymarket International vs Polymarket US

| Aspect | Polymarket (International) | Polymarket US |
|---|---|---|
| **Basis** | Crypto / blockchain | Fiat / USD |
| **Regulation** | Unregulated | CFTC-regulated DCM + DCO |
| **Target users** | Global (non-US) | US residents |
| **Settlement** | On-chain | Centralised clearing (Polymarket Clearing) |

### Key Differentiators from Sportsbooks

Polymarket US is fundamentally different from a traditional sportsbook in several ways:

- **Peer-to-peer exchange:** You trade against other users via a central limit order book (CLOB). The platform never takes the other side of your trade and does not set prices.
- **Exit anytime:** Unlike a sportsbook where your bet is locked in, you can sell your contracts before the event resolves. If sentiment shifts and prices move in your favour, you can close out early and take profits.
- **Market-driven prices:** Odds come from real trades. As new information becomes available, traders adjust their orders and prices update in real time — like a financial market.
- **Regulated derivatives exchange:** Event contracts are regulated financial instruments under CFTC oversight.

### Current Market Coverage

Sports: NFL, NBA, NHL, MLB, MLS, College Basketball (CBB), Tennis, Golf, and more. Politics, culture, finance, and economics markets are planned.

---

## 2. How Prediction Markets Work

A prediction market is a venue where participants trade on the probability of future events. Prices reflect the crowd's aggregate belief about the likelihood of an outcome occurring.

### Contract Mechanics

Each market asks a clear **yes/no question** about something that might happen. Contracts are priced between **$0.00 and $1.00**.

- A contract priced at **$0.62** means the market assigns roughly a **62% probability** to the event occurring.
- Contracts settle at **$1.00** if the outcome happens, or **$0.00** if it does not.
- You can buy or sell at any point before settlement — you don't have to hold to the end.

### Worked Example

**Market:** *Will the Kansas City Chiefs win Super Bowl LX?*

| Scenario | You buy YES at | Outcome | Contract settles at | Your profit |
|---|---|---|---|---|
| Chiefs win | $0.55 | YES | $1.00 | +$0.45 per contract |
| Chiefs lose | $0.55 | NO | $0.00 | −$0.55 per contract |

Because prices are set entirely by real trades, they tend to track real-world probabilities closely.

---

## 3. Market Hierarchy: Series → Events → Markets

Every prediction on Polymarket US is structured around three levels.

### Series

A series is a broad grouping of related events — like a sports league or a season. Think of it as a folder that contains many games or occurrences.

**Examples:** NFL 2025-26 Season, NBA 2025-26 Season, March Madness 2026

### Events

An event is a specific occurrence within a series — usually a single game, match, or contest. Each event has a start time, participants, and one or more markets attached to it.

**Examples:** Chiefs vs Eagles — Feb 9, 2026; Lakers vs Celtics — Jan 15, 2026

### Markets (Instruments)

A market is the actual thing you trade. It's a single yes/no question about an event. Each market settles at $1.00 if the outcome happens and $0.00 if it doesn't.

One event can have **multiple markets**:

| Market Type | Question | Example |
|---|---|---|
| **Moneyline** | Who wins? | Will the Chiefs win? |
| **Spread** | Will they win by more than X points? | Chiefs -3.5 |
| **Total** | Will the combined score be over/under X? | Total points over 47.5 |
| **Prop** | Will a specific thing happen in the game? | Mahomes over 2.5 TDs |

### Visual Hierarchy

```
Series: NFL 2025-26 Season
  └── Event: Chiefs vs Eagles — Feb 9, 2026
        ├── Market: Will the Chiefs win? (moneyline)
        ├── Market: Chiefs -3.5 (spread)
        └── Market: Total points over 47.5 (total)
```

### Market Slugs

Every market has a **slug** — a URL-friendly identifier like `aec-nfl-kc-phi-2026-02-09`. This slug is used everywhere: placing orders, fetching order books, subscribing to WebSocket streams. You can find slugs by searching or browsing markets through the API.

### Live Sports Data

For sports events that are in progress, you receive real-time metadata like the current score, period, and whether the game has ended. This is useful for building applications that react to live game state.

---

## 4. Glossary of Terms

### Market Structure & Hierarchy

| Term | Definition |
|---|---|
| **Category** | Broadest classification level organising instruments by event type (e.g. Sports, Politics, Crypto, Culture). |
| **Series** | More specific classification within a category, such as a sports league or topic (e.g. NFL, NBA, US Presidential, Bitcoin). |
| **Event** | A specific occurrence with multiple possible outcomes. Each event consists of one or more instruments representing the complete set of tradable outcomes. |
| **Product** | The type of contract structure used to format instruments (e.g. Athletic Event Contract, Election Winner Contract, Total Score Contract). |
| **Instrument** | The tradable symbol representing a specific outcome for an event. Also called a market. |
| **Participant** | The possible outcomes in an instrument. The long participant represents the "Yes" outcome; positions on the opposing outcome are achieved by selling (shorting) the long participant. |
| **Market** | Same as an instrument. A tradable outcome with defined resolution criteria and sources. |
| **Contract** | An instance of an instrument. You trade contracts in quantities (e.g. buying 100 contracts). Each contract settles at $1.00 if the outcome occurs and $0.00 if it does not. |

### Trading Basics

| Term | Definition |
|---|---|
| **Long position** | Buying contracts of an instrument, trading on the outcome occurring. You pay the current price per contract and receive $1.00 per contract if the outcome happens. |
| **Short position** | Selling (shorting) contracts of an instrument, trading on the outcome not occurring. You receive the current price per contract but must cover potential losses if the outcome happens. |
| **Order** | A request to buy or sell contracts at a chosen price. |
| **Order book** | List of bids and asks showing available prices and size at each level. |
| **Bid** | Highest price buyers are willing to pay. |
| **Ask** | Lowest price sellers are willing to accept. |
| **BBO (Best Bid and Offer)** | The best bid and ask prices currently available in the order book — the tightest spread at the top of the book. |
| **Spread** | Gap between the bid and the ask. |
| **Size** | Number of contracts available to buy or sell at a given price. |
| **Liquidity** | How much size is available to trade at listed prices. |

### Order Execution

| Term | Definition |
|---|---|
| **Fill** | When your order completes, fully or partially. |
| **Partial fill** | When only part of your order fills. |
| **Execution price** | The price at which your order fills. |
| **Fill price** | Average price you receive when your order fills across multiple levels. |
| **Marketable limit order** | An order that fills at the best available price shown on your screen. |
| **Price impact** | How much your fill price changes because of limited liquidity. |
| **Slippage** | Difference between expected and actual execution price. |
| **Maker** | Trader who adds liquidity by placing an order on the book. |
| **Taker** | Trader who removes liquidity by filling an existing order. |

### Positions & Account

| Term | Definition |
|---|---|
| **Open position** | Contracts you currently hold. |
| **Closed position** | A position you no longer hold because you sold it or the market resolved. |
| **Position value** | Real-time dollar value of your open positions. |
| **Cash balance** | Funds in your account not tied to open positions. |
| **Buying power** | Cash available to open new positions after margin is applied. |
| **Instant buying power** | Part of your deposit that becomes available to trade immediately. |
| **Margin** | Funds locked to cover the maximum possible loss of a short position. Equal to $1.00 per contract shorted. |
| **Max gain** | The most you can earn on a position. |
| **Max loss** | The most you can lose on a position. |

### Market Lifecycle

| Term | Definition |
|---|---|
| **Clarification** | Extra context added to explain how rules should be understood. |
| **Resolution** | When Polymarket determines the final outcome of a market using the sources listed in the rules. |
| **Settlement** | Final payout of $1.00 for winning contracts and $0.00 for losing contracts. |

### Fees & Display

| Term | Definition |
|---|---|
| **Fees** | Trading or platform fees applied to executed orders. |
| **Odds display** | How prices are shown, such as price, percent chance, or American odds. |
| **Open order** | An order waiting on the book to be filled. |
| **Order status** | Whether an order is open, filled, or partially filled. |
| **History** | Section showing your past filled orders and closed positions. |

---

## 5. Prices & the Order Book

### Prices Are Probabilities

Every contract on Polymarket US is priced between $0 and $1. The price represents the market's collective belief about how likely an outcome is.

| Price | Interpretation |
|---|---|
| $0.25 | Roughly 25% chance |
| $0.50 | Coin flip — market is undecided |
| $0.75 | Likely outcome (75% chance) |

If you buy a YES contract at $0.55 and the outcome happens, it settles at $1.00 — you profit $0.45 per contract. If it doesn't happen, it settles at $0.00 and you lose your $0.55.

### The Order Book (CLOB)

Polymarket US runs a **central limit order book**. Prices aren't set by Polymarket — they come from traders placing buy and sell orders against each other.

| Side | Meaning |
|---|---|
| **Bids** | Buy orders — the prices traders are willing to pay |
| **Asks (offers)** | Sell orders — the prices traders are willing to accept |

- The **spread** is the gap between the best bid and the best ask. A tight spread means the market is liquid. A wide spread means fewer people are trading.
- The **BBO (best bid and offer)** is the tightest price on each side — the highest bid and the lowest ask. This is the price you'd trade at if you placed a market order right now.

### How Trades Happen

- **Market order:** Fills immediately at the best available price on the other side of the book. You're a **taker** — you're taking liquidity.
- **Limit order** at a specific price that doesn't fill immediately: sits on the book waiting. You're a **maker** — providing liquidity for others.
- If your limit order's price crosses the best available price on the other side, it fills immediately (like a market order). Otherwise, it rests on the book.

### Settlement

When a market resolves, every contract settles at either $1.00 (YES won) or $0.00 (NO won). The exchange handles this automatically — winning contracts are credited to your balance, losing contracts go to zero.

### Market States

| State | Meaning |
|---|---|
| **Open** | Accepting orders and actively trading |
| **Pre-open** | Market exists but trading hasn't started |
| **Suspended** | Trading temporarily paused |
| **Halted** | Trading has been stopped |
| **Expired** | Market has ended and settled |

---

## 6. Orders & Trading Mechanics

### The YES/NO Model

Every market has two sides: **YES** and **NO**. They always add up to $1.00. If YES is priced at $0.60, NO is priced at $0.40.

There's only **one instrument per market — the YES side**. To trade against an outcome, you **sell** YES (which is the same as buying NO).

| What you want to do | How you do it |
|---|---|
| Trade on the outcome **happening** | Buy YES |
| Trade on the outcome **not happening** | Sell YES (equivalent to buying NO) |
| Close a winning YES position | Sell YES |
| Close a losing NO position | Buy YES back |

When placing an order, the price always refers to the YES side. If you want to buy NO at $0.40, you're really selling YES at $0.60.

### Order Types

| Type | How it works |
|---|---|
| **Limit order** | You set a price. Sits on the book until filled or cancelled. |
| **Market order** | Fills immediately at best available price. Instant execution but you pay the spread. |

### Time-in-Force Options

| Option | Meaning |
|---|---|
| **Good till cancel (GTC)** | Stays open until it fills or you cancel it |
| **Good till date (GTD)** | Stays open until a specific time, then auto-cancels |
| **Immediate or cancel (IOC)** | Fills whatever is available right now, cancels the rest |
| **Fill or kill (FOK)** | Must fill completely or not at all — no partial fills |

### Order Lifecycle

1. **Pending** — the exchange has received your order
2. **Open** — resting on the book, waiting for a match
3. **Partially filled** — some of your order has matched, the rest is still open
4. **Filled** — entire order has matched
5. **Cancelled / Expired / Rejected** — order didn't fill

### Positions

Once your order fills, you have a **position** — the contracts you hold in a market.

- A **long position** means you own YES contracts — you profit if the outcome happens.
- A **short position** means you've sold YES contracts — you profit if the outcome doesn't happen.

Your **buying power** is the cash available to open new positions. When you buy contracts, buying power decreases. When you sell or a market settles in your favour, it increases.

### Closing a Position

You close a position by taking the opposite action:

- Long (bought YES) → sell YES to close
- Short (sold YES) → buy YES to close

You don't have to wait for settlement. If the price has moved in your favour, you can lock in a profit early.

---

## 7. Collateral & Margin System

Polymarket Exchange operates with **fully-collateralised contracts** — sufficient funds are locked to cover the maximum possible payout at the time the trade is executed. No additional funds are required afterward.

### How Collateral Works

**Buyers (Long Positions):**
- Pay the contract price
- No additional margin required
- Maximum loss = amount paid
- Maximum gain = $1.00 − price paid

**Sellers (Short Positions):**
- Receive the contract price as proceeds
- Post $1.00 margin per contract (full payout value)
- Fiat balance increases by sale proceeds
- Buying power decreases by (Payout Value − Sale Price)
- Maximum loss = $1.00 − sale price
- Maximum gain = sale price

### Trade Example at $0.40

| Participant | Cash Flow | Margin Required | Buying Power Change |
|---|---|---|---|
| Buyer | −$0.40 | $0 | −$0.40 |
| Seller | +$0.40 | $1.00 | −$0.60 |

At settlement, **Polymarket Clearing** holds the seller's $1.00 margin to guarantee payout.

### Maximum Gain and Loss

Once a trade is executed, max gain and loss are **fixed and do not change** regardless of subsequent price movements.

**For a contract trading at $0.40:**

| Position | Max Loss | Max Gain |
|---|---|---|
| Buy (Long) | $0.40 | $0.60 |
| Sell (Short) | $0.60 | $0.40 |

### Shorting Mechanics

Shorting lets you take the opposite side of a market by selling a YES contract without owning it. You receive the sale price immediately, and margin equal to the full payout value ($1.00 per contract) is locked.

**Cash flow by position type:**
- **Long YES:** Fiat balance decreases by the purchase cost; buying power decreases by the same amount.
- **Short YES:** Fiat balance increases by sale proceeds; buying power decreases by (Payout Value − Sale Price) due to the full $1.00 margin locked per contract.

If you attempt a trade that would cause your buying power to fall below zero, the trade fails automatically.

### P/L Summary Table

| Action | Outcome | P/L |
|---|---|---|
| Buy YES @ $0.60 | YES wins | +$0.40 |
| Buy YES @ $0.60 | YES loses | −$0.60 |
| Sell YES @ $0.60 | YES wins | −$0.40 |
| Sell YES @ $0.60 | YES loses | +$0.60 |

### Portfolio Value Calculation

**For long positions:**
Portfolio Value = Buying Power + (Quantity × Last Price)

**For short positions:**
Portfolio Value = Buying Power + (Quantity × [Payout Value − Last Price])

**Example:** You have $5 starting balance and sell 1 YES contract at $0.70:
- Fiat Balance: $5.70 (received $0.70 proceeds)
- Margin Requirement: $1.00 (locked)
- Buying Power: $4.70 ($5.70 − $1.00)
- Position value: 1 × ($1.00 − $0.70) = $0.30
- Portfolio Value: $4.70 + $0.30 = $5.00 ✓

### Settlement and Payout

At settlement, **Polymarket Clearing** releases funds automatically:
- Winners receive **$1.00 per contract**
- Losers receive **$0**
- No margin calls, reconciliations, or additional obligations

### Collateral Management

Collateral and margin are managed at the clearing level:
1. You submit a withdrawal (e.g. $100) via Aeropay.
2. The DCO reviews it.
3. The DCM denies the request if it would leave insufficient buying power to meet margin obligations.

The same logic applies to open orders — unmatched longs or shorts cannot remain if they would breach margin limits.

### Portfolio Margin

Polymarket Exchange applies **portfolio-level margining**, meaning margin requirements consider your entire set of open positions rather than treating each market in isolation. You can maintain many open positions across different markets, as long as the aggregate exposure does not exceed your available buying power.

---

## 8. Portfolio Margin: Mutually Exclusive Collateral Return

Mutually exclusive collateral return is a portfolio margin optimisation that reduces your margin requirement when you hold offsetting short positions in instruments from the same event where only one outcome can occur.

### What Are Mutually Exclusive Events?

Events where only one outcome can happen: elections (one winner), championships (one team wins the title), award winners (one nominee wins).

### How It Works

When you hold short positions across multiple instruments in the same mutually exclusive event, the exchange recognises that your maximum loss is capped because only one outcome can occur.

**Without Collateral Return:**
- Short 9,000 contracts of Candidate A
- Short 1,000 contracts of Candidate B (same election)
- Margin requirement: **10,000** (9,000 + 1,000)

**With Collateral Return:**
- Short 9,000 contracts of Candidate A
- Short 1,000 contracts of Candidate B (same election)
- Margin requirement: **9,000** (reduced by the 1,000 offsetting position)
- Freed buying power: **1,000**

### Why This Matters

Your worst-case scenario is having the larger short position lose. The smaller offsetting position guarantees you'll win that amount.

**Maximum loss calculation:**
- If Candidate A wins: You lose 9,000 but gain 1,000 = Net loss 8,000
- If Candidate B wins: You lose 1,000 but gain 9,000 = Net gain 8,000

Your true maximum loss is 8,000, not 10,000.

### Rules

- Freed-up buying power **can** be used in other markets (different events).
- Freed-up buying power **cannot** be used to increase positions in the same mutually exclusive event.
- Closing offsetting positions requires returning the freed collateral. If that capital is deployed elsewhere, the close order will be rejected.

---

## 9. Portfolio Margin: Directional Collateral Return

Directional collateral return is a portfolio margin optimisation that reduces your margin requirement when you hold offsetting positions in instruments from the same directional event.

### What Are Directional Events?

Events with multiple instruments at ordered strike levels where outcomes are logically linked. If a higher threshold is true, all lower thresholds must also be true.

**Examples:**
- **Point spreads:** Win by more than 3.5? 6.5? 10.5?
- **Totals:** Score exceed 40.5? 47.5? 50.5?
- **Price levels:** Bitcoin exceed 50K? 75K? 100K?

Each instrument has an ordinal rank (rank 1 = lowest threshold). If rank 3 resolves YES, then ranks 1 and 2 must also resolve YES.

### How It Works

When you hold a lower-ranked long position that offsets a higher-ranked short position in the same directional event, your margin requirement is reduced.

**Without Collateral Return:**
- Long 3 contracts of BTC-hit-120K
- Short 2 contracts of BTC-hit-130K
- Margin requirement: **2** (full short position)

**With Collateral Return:**
- Long 3 contracts of BTC-hit-120K
- Short 2 contracts of BTC-hit-130K
- Margin requirement: **0** (short fully offset by lower-ranked long)

### Directionality Matters

Only a **lower-ranked long** can offset a **higher-ranked short**. The reverse does not work.

- ✅ Long BTC-120K, Short BTC-130K → collateral return applies
- ❌ Long BTC-130K, Short BTC-120K → NO collateral return

### Multiple Offsets

A single lower-ranked long position can offset multiple higher-ranked short positions. The exchange matches the highest-ranking short with the highest available long first, working down.

### Rules

Same as mutually exclusive: freed buying power can be used elsewhere but not in the same directional event. Closing positions requires returning collateral.

---

## 10. Fee Schedule & Rebates

*Effective exchange-wide from 3pm ET, Friday April 3, 2026.*

### Fee Formula

Fees are computed using a symmetric formula that scales with price uncertainty:

```
Fee = Θ × C × p × (1 − p)
```

Where:
- **C** = number of contracts
- **p** = trade price ($0.01 to $0.99)
- **Θ** (theta) = fee coefficient

| Role | Theta | Maximum Fee (at p = $0.50) per 100-lot |
|---|---|---|
| **Taker Fee** | 0.05 | $1.25 |
| **Maker Rebate** | −0.0125 | −$0.31 (rebate) |

### Rebate Structure

- **Maker rebate** (25% of taker fees): applied at the point of trade.
- **Taker rebate** (50% of taker fees): applied weekly.

### Fee Characteristics

- Fees are **symmetric around p = 0.50** and **lowest near the extremes** (0 and 1).
- All fees and rebates are rounded to the nearest $0.01 using **banker's rounding** (round half to even).
- Fees are only charged when a trade executes. Cancelled, expired, or rejected orders incur no fee.
- On very small trades (low quantity or prices near $0.00 / $1.00), the fee can round down to $0.00.

### Worked Fee Examples

| Scenario | Taker Pays | Maker Receives |
|---|---|---|
| Buy 1,000 @ $0.10 (long shot) | $4.50 | $1.13 |
| Buy 1,000 @ $0.65 (likely outcome) | $11.38 | $2.84 |
| Sell 1,000 @ $0.30 (sell low prob) | $10.50 | $2.63 |
| Sell 1,000 @ $0.90 (sell high prob) | $4.50 | $1.13 |
| Buy 1,000 @ $0.50 (coin flip) | $12.50 | $3.13 |

### Select Fee Table (per 100-lot)

| Price | Trade Value | Taker Pays | Maker Receives |
|---|---|---|---|
| $0.05 | $5 | $0.24 | $0.06 |
| $0.10 | $10 | $0.45 | $0.11 |
| $0.20 | $20 | $0.80 | $0.20 |
| $0.30 | $30 | $1.05 | $0.26 |
| $0.40 | $40 | $1.20 | $0.30 |
| $0.50 | $50 | $1.25 | $0.31 |
| $0.60 | $60 | $1.20 | $0.30 |
| $0.70 | $70 | $1.05 | $0.26 |
| $0.80 | $80 | $0.80 | $0.20 |
| $0.90 | $90 | $0.45 | $0.11 |
| $0.95 | $95 | $0.24 | $0.06 |

---

## 11. Incentive Programs

Polymarket US offers incentive programs that pay you for trading activity and providing liquidity.

| Program | Access | Description |
|---|---|---|
| **Volume Incentive Program** | Open (no signup) | Rewards for trading volume, maker or taker |
| **Liquidity Incentive Program** | Open (no signup) | Rewards for placing resting orders, whether they fill or not |
| **Fill Incentive Program** | Open (no signup) | Rewards for placing resting orders that fill |
| **Market Maker Program** | Application required | Strong incentives for providing stable liquidity across many markets; formal contractual obligations |

**Open** programs are live — you're already earning rewards every time you trade.

---

## 12. API Architecture

The Polymarket US API is split into two parts.

### Authenticated API (Trading)

```
Base URL: https://api.polymarket.us
```

Requires API key. Used for placing orders, checking positions, and managing your account.

| Group | Capabilities |
|---|---|
| **Orders** | Place, modify, cancel, and query orders |
| **Portfolio** | View positions and trading activity |
| **Account** | Check balances and buying power |

**WebSocket endpoints (authenticated):**

| Endpoint | Purpose |
|---|---|
| `wss://api.polymarket.us/v1/ws/private` | Real-time order, position, and balance updates |
| `wss://api.polymarket.us/v1/ws/markets` | Real-time order book and trade streaming |

### Public API (Market Data)

```
Base URL: https://gateway.polymarket.us
```

No API key needed. Used for browsing markets, events, series, sports data, and search.

| Group | Capabilities |
|---|---|
| **Markets** | List markets, get order books, BBO, settlement prices |
| **Events** | List events, get event details |
| **Series** | List series (e.g. NFL 2025-26 Season) |
| **Sports** | Leagues, teams, game schedules |
| **Search** | Full-text search across events and markets |
| **Subjects** | Browse subjects and their associated markets |
| **Tags** | Browse tags and their associated content |

---

## 13. Authentication

Authenticated endpoints (trading, portfolio, WebSocket) require an API key. Public endpoints (market data, events) do not.

### Getting API Keys

1. **Download the app** — Get the Polymarket US app from the App Store and create an account.
2. **Complete identity verification** — Verify your identity before you can trade or access the API.
3. **Go to the developer portal** — Visit `polymarket.us/developer` and sign in with the same method (Apple, Google, or email).
4. **Create an API key** — You'll get a **Key ID** and a **Secret Key**. The secret key is shown **only once**.

### Using the SDK

Pass your keys when creating the client — authentication is handled automatically.

**TypeScript:**
```typescript
import { PolymarketUS } from 'polymarket-us';

const client = new PolymarketUS({
  keyId: process.env.POLYMARKET_KEY_ID,
  secretKey: process.env.POLYMARKET_SECRET_KEY,
});
```

**Python:**
```python
from polymarket_us import PolymarketUS

client = PolymarketUS(
    key_id=os.environ["POLYMARKET_KEY_ID"],
    secret_key=os.environ["POLYMARKET_SECRET_KEY"],
)
```

### Making Raw Requests (Without SDK)

Each request needs three headers:

| Header | Value |
|---|---|
| `X-PM-Access-Key` | Your Key ID |
| `X-PM-Timestamp` | Current time in milliseconds |
| `X-PM-Signature` | Ed25519 signature |

The signature is built by combining the timestamp, HTTP method, and path, then signing it with your secret key (Ed25519). Timestamps must be within **30 seconds** of server time.

**Python example:**
```python
import time, base64, requests
from cryptography.hazmat.primitives.asymmetric import ed25519

private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
    base64.b64decode("YOUR_SECRET_KEY")[:32]
)

def auth_headers(method, path):
    timestamp = str(int(time.time() * 1000))
    message = f"{timestamp}{method}{path}"
    signature = base64.b64encode(private_key.sign(message.encode())).decode()
    return {
        "X-PM-Access-Key": "YOUR_KEY_ID",
        "X-PM-Timestamp": timestamp,
        "X-PM-Signature": signature,
        "Content-Type": "application/json",
    }

response = requests.get(
    "https://api.polymarket.us/v1/portfolio/positions",
    headers=auth_headers("GET", "/v1/portfolio/positions")
)
```

### Security Tips

- Store keys in environment variables, never in code.
- Don't commit keys to version control.
- Revoke compromised keys immediately at `polymarket.us/developer`.

---

## 14. Rate Limits

Rate limits are enforced per API key. Exceeding them returns `429 Too Many Requests`.

### Trading Endpoints

| Endpoint | Limit |
|---|---|
| `POST /v1/orders` (place order) | 440 requests / 10 seconds |
| `POST /v1/order/{id}/cancel` | 440 requests / 10 seconds |
| `POST /v1/order/{id}/modify` | 440 requests / 10 seconds |
| `POST /v1/orders/open/cancel` (cancel all) | 110 requests / 10 seconds |
| `POST /v1/order/close-position` | 220 requests / 10 seconds |
| **Global (all endpoints combined)** | 2,000 requests / 10 seconds |

### Query Endpoints

| Endpoint | Limit |
|---|---|
| `GET /v1/orders/open` | 55 requests / 10 seconds |
| `GET /v1/order/{id}` | 55 requests / 10 seconds |

### Public (Unauthenticated)

| Limit | Value |
|---|---|
| Max requests | 20 per second per IP |

### Handling Rate Limits

When rate limited, stop immediately, wait at least 1 second, then retry with exponential backoff:

```python
import time

def make_request_with_retry(fn, max_retries=3):
    for attempt in range(max_retries):
        response = fn()
        if response.status_code != 429:
            return response
        time.sleep(2 ** attempt)
    raise Exception("Max retries exceeded")
```

### Best Practices

**Use WebSocket instead of polling** — one persistent connection replaces hundreds of repeated REST calls:

| Don't poll | Use instead |
|---|---|
| `GET /v1/orders/open` repeatedly | `/v1/ws/private` — `SUBSCRIPTION_TYPE_ORDER` |
| `GET /v1/portfolio/positions` repeatedly | `/v1/ws/private` — `SUBSCRIPTION_TYPE_POSITION` |
| `GET /v1/account/balances` repeatedly | `/v1/ws/private` — `SUBSCRIPTION_TYPE_ACCOUNT_BALANCE` |
| `GET /v1/markets/{slug}/bbo` repeatedly | `/v1/ws/markets` — `SUBSCRIPTION_TYPE_MARKET_DATA_LITE` |
| `GET /v1/markets/{slug}/book` repeatedly | `/v1/ws/markets` — `SUBSCRIPTION_TYPE_MARKET_DATA` |

**Cache reference data** — market and event metadata changes infrequently. Fetch once on startup and refresh periodically (e.g. every 5 minutes).

**Need higher limits?** Email `support@polymarket.us` with your use case and expected request volume.

---

## 15. REST API Endpoint Reference

### Orders API (Authenticated)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/orders/open` | Get open orders |
| `GET` | `/v1/order/{id}` | Get a specific order |
| `POST` | `/v1/orders` | Create order |
| `POST` | `/v1/order/{id}/cancel` | Cancel order |
| `POST` | `/v1/orders/open/cancel` | Cancel all open orders |
| `POST` | `/v1/order/{id}/modify` | Modify order |
| `POST` | `/v1/order/preview` | Preview order (no execution) |
| `POST` | `/v1/order/close-position` | Close position order |

### Portfolio API (Authenticated)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/portfolio/positions` | Get user positions |
| `GET` | `/v1/portfolio/activities` | Get activities |
| `GET` | `/v1/account/balances` | Get account balances |

### Events API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/events` | List events |
| `GET` | `/v1/events/{id}` | Get event by ID |
| `GET` | `/v1/events/slug/{slug}` | Get event by slug |
| `GET` | `/v1/partner/events/{external_id}` | Get event by partner external ID |

### Markets API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/markets/{id}` | Get market by ID |
| `GET` | `/v1/markets/slug/{slug}` | Get market by slug |
| `GET` | `/v1/markets` | List markets |
| `GET` | `/v1/markets/{slug}/bbo` | Get market BBO (best bid/offer) |
| `GET` | `/v1/markets/{slug}/book` | Get full market order book |
| `GET` | `/v1/markets/{slug}/settlement` | Get market settlement info |

### Series API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/series` | List series |
| `GET` | `/v1/series/{id}` | Get series by ID |

### Sports API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/sports/leagues` | Get all leagues |
| `GET` | `/v1/sports/leagues/{slug}` | Get league by slug |
| `GET` | `/v1/sports/leagues/{slug}/events` | Get events by league slug |
| `GET` | `/v1/sports` | Get all sports |
| `GET` | `/v1/sports/{slug}` | Get sport by slug |
| `GET` | `/v1/sports/{slug}/events` | Get events by sport slug |

### Sports API — Legacy (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/sports` (legacy) | Get sports |
| `GET` | `/v1/sports/events` | Get sports events |
| `GET` | `/v1/sports/teams` | Get sports teams |
| `GET` | `/v1/sports/teams/{provider}` | Get sports teams for provider |

### Subjects API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/subjects` | List subjects |
| `GET` | `/v1/subjects/{id}` | Get subject by ID |
| `GET` | `/v1/subjects/{id}/markets` | Get markets for subject |
| `GET` | `/v1/subjects/slug/{slug}` | Get subject by slug |
| `GET` | `/v1/subjects/slug/{slug}/markets` | Get markets for subject by slug |

### Tags API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/tags` | List tags |
| `GET` | `/v1/tags/{id}` | Get tag by ID |
| `GET` | `/v1/tags/slug/{slug}` | Get tag by slug |

### Search API (Public)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/search` | Full-text search across events and markets |

---

## 16. WebSocket Streaming

Polymarket US provides two WebSocket endpoints for real-time data.

### Private WebSocket (Authenticated)

```
wss://api.polymarket.us/v1/ws/private
```

Subscription types:
- `SUBSCRIPTION_TYPE_ORDER` — real-time order updates (fills, cancels, status changes)
- `SUBSCRIPTION_TYPE_POSITION` — real-time position updates
- `SUBSCRIPTION_TYPE_ACCOUNT_BALANCE` — real-time balance changes

### Market WebSocket (Authenticated)

```
wss://api.polymarket.us/v1/ws/markets
```

Subscription types:
- `SUBSCRIPTION_TYPE_MARKET_DATA` — full order book depth updates
- `SUBSCRIPTION_TYPE_MARKET_DATA_LITE` — BBO (best bid/offer) updates only

---

## 17. SDKs (TypeScript & Python)

Official SDKs are provided for both TypeScript and Python.

### Installation

**TypeScript** (requires Node.js 18+):
```bash
npm install polymarket-us
```

**Python** (requires Python 3.10+):
```bash
pip install polymarket-us
```

### Client Configuration

**TypeScript:**
```typescript
import { PolymarketUS } from 'polymarket-us';

// Authenticated client
const client = new PolymarketUS({
  keyId: process.env.POLYMARKET_KEY_ID,
  secretKey: process.env.POLYMARKET_SECRET_KEY,
});

// Public-only client (no auth needed for market data)
const publicClient = new PolymarketUS();
```

**Python:**
```python
from polymarket_us import PolymarketUS

# Authenticated client
client = PolymarketUS(
    key_id=os.environ["POLYMARKET_KEY_ID"],
    secret_key=os.environ["POLYMARKET_SECRET_KEY"],
)

# Public-only client
public_client = PolymarketUS()
```

---

## 18. Quickstart: End-to-End Walkthrough

### Step 1: Get API Keys

1. Download the Polymarket US app and create an account.
2. Complete identity verification.
3. Visit `polymarket.us/developer` and sign in.
4. Create an API key — save your Secret Key immediately (shown only once).

### Step 2: Install the SDK

```bash
npm install polymarket-us    # TypeScript
pip install polymarket-us    # Python
```

### Step 3: Configure the Client

```typescript
import { PolymarketUS } from 'polymarket-us';

const client = new PolymarketUS({
  keyId: process.env.POLYMARKET_KEY_ID,
  secretKey: process.env.POLYMARKET_SECRET_KEY,
});
```

### Step 4: Fetch Market Data (No Auth Required)

```typescript
const client = new PolymarketUS();

const events = await client.events.list({ limit: 10, active: true });
const market = await client.markets.retrieveBySlug('chiefs-super-bowl');
const book = await client.markets.book('chiefs-super-bowl');
```

### Step 5: Place an Order

```typescript
const order = await client.orders.create({
  marketSlug: 'chiefs-super-bowl',
  intent: 'ORDER_INTENT_BUY_LONG',
  type: 'ORDER_TYPE_LIMIT',
  price: { value: '0.55', currency: 'USD' },
  quantity: 100,
  tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL',
});
```

### Step 6: Check Your Account

```typescript
const balances = await client.account.balances();
const positions = await client.portfolio.positions();
const openOrders = await client.orders.list();
```

---

## 19. Error Handling

The SDKs provide typed error classes for common failure modes.

| Error Class | Description |
|---|---|
| `AuthenticationError` | Invalid or missing credentials |
| `BadRequestError` | Invalid request parameters |
| `NotFoundError` | Resource not found |
| `RateLimitError` | Rate limit exceeded |
| `APITimeoutError` | Request timed out |
| `APIConnectionError` | Network connection error |

**TypeScript example:**
```typescript
import {
  AuthenticationError,
  BadRequestError,
  NotFoundError,
  RateLimitError,
} from 'polymarket-us';

try {
  const order = await client.orders.create({ marketSlug: '...' });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid credentials');
  } else if (error instanceof BadRequestError) {
    console.error('Invalid parameters:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limited — back off and retry');
  } else if (error instanceof NotFoundError) {
    console.error('Not found');
  }
}
```

---

---
---

# PART 2: Polymarket Analytics — Falcon API

> **Source:** [api.polymarketanalytics.com](https://api.polymarketanalytics.com)
> **Product Name:** Falcon API
> **Built by:** Polymarket Analytics

---

## Table of Contents (Falcon API)

20. [Falcon API Overview](#20-falcon-api-overview)
21. [API Architecture & Base URL](#21-api-architecture--base-url)
22. [Authentication](#22-falcon-api-authentication)
23. [Request Structure](#23-request-structure)
24. [Data Suite 1: Historical & Real-Time Market Data](#24-data-suite-1-historical--real-time-market-data)
25. [Data Suite 2: Trader Intelligence & Analytics](#25-data-suite-2-trader-intelligence--analytics)
26. [Data Suite 3: Cross-Market Analysis](#26-data-suite-3-cross-market-analysis)
27. [Data Suite 4: Web Intelligence & Sentiment](#27-data-suite-4-web-intelligence--sentiment)
28. [Trader Leaderboard & F-Score](#28-trader-leaderboard--f-score)
29. [Claude MCP Integration](#29-claude-mcp-integration)
30. [Quickstart](#30-falcon-api-quickstart)

---

## 20. Falcon API Overview

The Falcon API is a third-party analytics and intelligence layer built on top of prediction market data. It is developed by **Polymarket Analytics** and provides capabilities that go well beyond the official Polymarket US or International APIs — focusing on trader intelligence, cross-venue analysis, sentiment signals, and aggregated performance metrics.

### What Falcon Provides That the Official API Does Not

| Capability | Official Polymarket US API | Falcon API |
|---|---|---|
| Market data (prices, books, events) | ✅ | ✅ |
| Order placement & trading | ✅ | ❌ |
| Wallet/trader PnL & performance | ❌ | ✅ |
| Trader win rate, ROI, drawdowns | ❌ | ✅ |
| Smart money / whale activity | ❌ | ✅ |
| Cross-venue comparison (Polymarket vs Kalshi) | ❌ | ✅ |
| Social sentiment scoring | ❌ | ✅ |
| Narrative vs price divergence | ❌ | ✅ |
| Deep historical data for backtesting | Limited | ✅ |
| Trader leaderboard / F-Score rankings | ❌ | ✅ |
| Claude MCP server integration | ❌ | ✅ |

### Target Users

Falcon is designed for developers, AI agents, quantitative traders, data analysts, and teams building on prediction market data who need intelligence-layer features (not just raw market data).

### Key Design Principles

- **All endpoints use POST** — request parameters are sent as JSON body payloads, not query strings.
- **Unified API** — one base URL serves all data suites (markets, traders, cross-venue, sentiment).
- **Pagination built-in** — all list endpoints accept `pagination: { limit, offset }` parameters.
- **Formatter config** — responses can be returned in different formats via `formatter_config.format_type` (e.g. `"raw"`).
- **Distributed infrastructure** — built for reliability and scale, designed for production workloads and automation.

---

## 21. API Architecture & Base URL

All Falcon API requests are made to a single base URL:

```
https://narrative.agent.heisenberg.so/v2
```

The API version is `v2`. All endpoints are accessed via `POST` requests to paths under this base.

### Endpoint Naming Convention

Endpoints follow a `/{domain}/{action}` pattern:

| Domain | Example Endpoint | Purpose |
|---|---|---|
| `markets` | `/v2/markets/retrieve` | Market data retrieval |
| `traders` | `/v2/traders/stats` | Trader performance analytics |
| `cross` | `/v2/cross/compare` | Cross-venue analysis |
| `signals` | `/v2/signals/sentiment` | Web intelligence & sentiment |

---

## 22. Falcon API Authentication

All requests require a Bearer token passed in the `Authorization` header.

```
Authorization: Bearer YOUR_API_TOKEN
```

### Getting an API Key

1. Visit [api.polymarketanalytics.com/sign-up](https://api.polymarketanalytics.com/sign-up)
2. Create an account with your email address
3. Receive your API token

### Header Requirements

Every request must include:

| Header | Value |
|---|---|
| `Authorization` | `Bearer YOUR_API_TOKEN` |
| `Content-Type` | `application/json` |

---

## 23. Request Structure

All Falcon API endpoints use `POST` with a JSON body. The general request structure follows a consistent pattern:

### Standard Request Format

```json
{
  "agent_id": 574,
  "params": {
    // Endpoint-specific parameters
  },
  "pagination": {
    "limit": 100,
    "offset": 0
  },
  "formatter_config": {
    "format_type": "raw"
  }
}
```

### Common Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | integer | Varies | Identifies the calling agent/application |
| `params` | object | Yes | Endpoint-specific query parameters |
| `pagination` | object | Optional | Controls result set size and offset |
| `pagination.limit` | integer | Optional | Maximum number of results to return |
| `pagination.offset` | integer | Optional | Number of results to skip (for paging) |
| `formatter_config` | object | Optional | Controls output formatting |
| `formatter_config.format_type` | string | Optional | Output format — e.g. `"raw"` for raw JSON |

---

## 24. Data Suite 1: Historical & Real-Time Market Data

This suite provides clean, normalised data across the full market lifecycle. It covers markets, outcomes, metadata, trades, order books, prices, volume, liquidity, spreads, and deep historical coverage for backtesting.

### Endpoint: `/v2/markets/retrieve`

Retrieves market data with flexible filtering.

**Request:**
```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/markets/retrieve \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 574,
    "params": {
      "market_slug": "bitcoin-up-or-down-january-17-3pm-et",
      "min_volume": "100",
      "closed": "True"
    },
    "pagination": {"limit": 100, "offset": 0},
    "formatter_config": {"format_type": "raw"}
  }'
```

### Request Parameters (`params`)

| Parameter | Type | Description |
|---|---|---|
| `market_slug` | string | URL-friendly market identifier |
| `min_volume` | string | Minimum total volume filter |
| `closed` | string | Filter by market closure status (`"True"` / `"False"`) |

### Response Fields

```json
{
  "question": "Bitcoin Up or Down — January 17, 3PM ET",
  "slug": "bitcoin-up-or-down-january-17-3pm-et",
  "condition_id": "0xeaff81adbcd9dcd88a73a41402cb...",
  "volume_total": 104456.76,
  "closed": true,
  "side_a_outcome": "Up",
  "side_b_outcome": "Down",
  "winning_outcome": "Up",
  "start_date": "2026-01-15T20:01:06Z",
  "end_date": "2026-01-17T21:00:00Z"
}
```

| Field | Type | Description |
|---|---|---|
| `question` | string | Human-readable market question |
| `slug` | string | URL-friendly unique identifier |
| `condition_id` | string | On-chain condition ID (hex) — uniquely identifies the market on-chain |
| `volume_total` | float | Total trading volume in USD |
| `closed` | boolean | Whether the market has resolved/closed |
| `side_a_outcome` | string | Label for the first outcome (e.g. "Up", "Yes") |
| `side_b_outcome` | string | Label for the second outcome (e.g. "Down", "No") |
| `winning_outcome` | string | Which outcome won (only populated if `closed: true`) |
| `start_date` | string (ISO 8601) | When the market opened for trading |
| `end_date` | string (ISO 8601) | When the market resolved/closed |

### Data Capabilities

- Markets, outcomes, and metadata
- Trades and order books
- Prices, volume, liquidity, spreads
- Deep historical coverage suitable for backtesting strategies

---

## 25. Data Suite 2: Trader Intelligence & Analytics

This suite provides wallet-level and trader-level performance analysis. It goes beyond raw trade data to deliver aggregated intelligence about trading behaviour, profitability, and risk.

### Endpoint: `/v2/traders/stats`

Returns comprehensive performance metrics for a specific wallet address.

**Request:**
```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/traders/stats \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "0x1a2b3c4d5e6f...",
    "metrics": ["pnl", "roi", "win_rate", "drawdown"],
    "timeframe": "90d"
  }'
```

### Request Parameters

| Parameter | Type | Description |
|---|---|---|
| `wallet` | string | Ethereum wallet address (hex) |
| `metrics` | array of strings | Which metrics to compute and return |
| `timeframe` | string | Time window for analysis (e.g. `"90d"`, `"30d"`, `"7d"`, `"all"`) |

### Available Metrics

| Metric | Description |
|---|---|
| `pnl` | Total profit and loss in USD |
| `roi` | Return on investment (decimal, e.g. 0.342 = 34.2%) |
| `win_rate` | Fraction of trades that were profitable (decimal, e.g. 0.71 = 71%) |
| `drawdown` | Maximum peak-to-trough decline (decimal, e.g. -0.18 = -18%) |

### Response Fields

```json
{
  "wallet": "0x1a2b3c4d5e6f...",
  "total_pnl": 588617.70,
  "roi": 0.342,
  "win_rate": 0.71,
  "max_drawdown": -0.18,
  "total_trades": 1247,
  "active_positions": 23
}
```

| Field | Type | Description |
|---|---|---|
| `wallet` | string | The queried wallet address |
| `total_pnl` | float | Total profit/loss in USD across the timeframe |
| `roi` | float | Return on investment as a decimal (0.342 = 34.2%) |
| `win_rate` | float | Win rate as a decimal (0.71 = 71%) |
| `max_drawdown` | float | Maximum drawdown as a decimal (-0.18 = -18% peak-to-trough) |
| `total_trades` | integer | Total number of trades executed |
| `active_positions` | integer | Number of currently open positions |

### Intelligence Capabilities

- Wallet and trader performance insights
- PnL, ROI, win rate, drawdowns
- Financial indicators and trading patterns
- Smart money and whale activity detection

---

## 26. Data Suite 3: Cross-Market Analysis

This suite enables cross-venue comparison between prediction market platforms. It can match equivalent markets across Polymarket and Kalshi (and potentially other venues) to identify price disagreements, volume ratios, and lead-lag relationships.

### Endpoint: `/v2/cross/compare`

Compares matched markets across multiple prediction market venues.

**Request:**
```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/cross/compare \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "us-election-2026",
    "venues": ["polymarket", "kalshi"],
    "metrics": ["price_gap", "volume_ratio"]
  }'
```

### Request Parameters

| Parameter | Type | Description |
|---|---|---|
| `topic` | string | Topic or keyword to match markets across venues |
| `venues` | array of strings | Which venues to compare (e.g. `"polymarket"`, `"kalshi"`) |
| `metrics` | array of strings | Which cross-venue metrics to compute |

### Available Cross-Venue Metrics

| Metric | Description |
|---|---|
| `price_gap` | Absolute difference between YES prices on matched markets across venues |
| `volume_ratio` | Ratio of trading volume between venues for matched markets |

### Response Fields

```json
{
  "matched_markets": 12,
  "largest_disagreement": {
    "topic": "Senate Control 2026",
    "polymarket_yes": 0.62,
    "kalshi_yes": 0.55,
    "price_gap": 0.07,
    "volume_ratio": 3.2
  },
  "avg_price_gap": 0.031
}
```

| Field | Type | Description |
|---|---|---|
| `matched_markets` | integer | Number of equivalent markets found across venues |
| `largest_disagreement` | object | The market pair with the biggest price discrepancy |
| `largest_disagreement.topic` | string | Topic of the most-disagreed market |
| `largest_disagreement.polymarket_yes` | float | YES price on Polymarket |
| `largest_disagreement.kalshi_yes` | float | YES price on Kalshi |
| `largest_disagreement.price_gap` | float | Absolute difference between the two prices |
| `largest_disagreement.volume_ratio` | float | Volume on venue A / volume on venue B |
| `avg_price_gap` | float | Average price gap across all matched markets |

### Cross-Market Capabilities

- Market matching across Polymarket and Kalshi
- Cross-venue price disagreement detection
- Trader and wallet overlap detection
- Early signal and lead-lag analysis (which venue moves first)

---

## 27. Data Suite 4: Web Intelligence & Sentiment

This suite measures narrative pressure against market pricing by analysing social media, news, and other web sources in real time.

### Endpoint: `/v2/signals/sentiment`

Returns sentiment scoring and narrative analysis for a specific market.

**Request:**
```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/signals/sentiment \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "market_slug": "fed-rate-cut-march-2026",
    "sources": ["twitter", "reddit", "news"],
    "window": "24h"
  }'
```

### Request Parameters

| Parameter | Type | Description |
|---|---|---|
| `market_slug` | string | Market identifier to analyse |
| `sources` | array of strings | Which web sources to include in analysis |
| `window` | string | Time window for sentiment analysis (e.g. `"1h"`, `"6h"`, `"24h"`, `"7d"`) |

### Available Sources

| Source | Description |
|---|---|
| `twitter` | Twitter/X posts, mentions, and engagement |
| `reddit` | Reddit posts and comments |
| `news` | News articles and headlines |

### Response Fields

```json
{
  "market": "Fed Rate Cut — March 2026",
  "sentiment_score": 0.73,
  "mention_volume": 14820,
  "price_sentiment_divergence": -0.12,
  "top_influencer": "@macroanalyst",
  "narrative_trend": "bullish",
  "confidence": 0.88
}
```

| Field | Type | Description |
|---|---|---|
| `market` | string | Human-readable market name |
| `sentiment_score` | float | Aggregate sentiment score (0.0 = very bearish, 1.0 = very bullish) |
| `mention_volume` | integer | Total number of mentions across all sources in the window |
| `price_sentiment_divergence` | float | Gap between market price and sentiment-implied probability. Negative = sentiment is more bearish than the market price suggests; positive = more bullish. |
| `top_influencer` | string | Handle of the most impactful account driving sentiment |
| `narrative_trend` | string | Overall narrative direction (`"bullish"`, `"bearish"`, `"neutral"`) |
| `confidence` | float | Confidence level in the sentiment assessment (0.0–1.0) |

### Web Intelligence Capabilities

- Social media impressions and volume
- Sentiment scoring across multiple platforms
- Narrative vs price divergence (is the market mispriced relative to public sentiment?)
- Influential accounts and signals

---

## 28. Trader Leaderboard & F-Score

Falcon maintains a proprietary trader ranking system based on an **F-Score** — a composite performance metric. The leaderboard tracks the top-performing wallets on Polymarket.

### Leaderboard Structure

| Field | Description |
|---|---|
| **Rank** | Position on the overall leaderboard |
| **Wallet** | Trader's wallet address (truncated hex) |
| **F-Score** | Falcon's proprietary composite performance score |
| **15d ROI** | Return on investment over the trailing 15-day window |

### Example Leaderboard Data

| Rank | Wallet | 15d ROI |
|---|---|---|
| #1 | `0x93ab...9723` | +16.2% |
| #2 | `0x036c...178d` | +18.3% |
| #3 | `0xe524...d34f` | +20.2% |
| #4 | `0x3f5e...e7db` | +20.6% |
| #5 | `0x2707...0afa` | +15.8% |

The F-Score is a proprietary metric that likely combines multiple performance dimensions (PnL, consistency, win rate, risk-adjusted returns, drawdown management) into a single ranking score. Exact methodology is not publicly documented.

---

## 29. Claude MCP Integration

Falcon provides a native **Claude MCP (Model Context Protocol)** integration, allowing Claude Desktop or Claude-compatible clients to access all Falcon data suites directly through natural language.

### How It Works

The MCP integration works with both paid Claude plans and the free Claude Desktop app. Once configured, Claude can:

- Query market data and historical prices
- Look up trader performance by wallet address
- Compare markets across Polymarket and Kalshi
- Analyse sentiment around specific markets
- Access the trader leaderboard

### Setup

Setup instructions are available at `api.polymarketanalytics.com/quickstart` after obtaining an API key. The MCP server connects Claude to the Falcon API endpoints, translating natural language queries into structured API calls.

### Example Claude Prompts (via MCP)

- "What's the current sentiment on the Fed rate cut market?"
- "Show me the top 5 traders by F-Score"
- "Compare the Senate control market on Polymarket vs Kalshi"
- "What's the PnL and win rate for wallet 0x1a2b3c..."
- "Find markets with volume over $100k that closed in the last week"

---

## 30. Falcon API Quickstart

### Step 1: Get an API Key

Visit [api.polymarketanalytics.com/sign-up](https://api.polymarketanalytics.com/sign-up), create an account, and receive your API token.

### Step 2: Make Your First Request

**Fetch market data:**
```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/markets/retrieve \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 574,
    "params": {
      "min_volume": "1000"
    },
    "pagination": {"limit": 10, "offset": 0},
    "formatter_config": {"format_type": "raw"}
  }'
```

### Step 3: Query Trader Performance

```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/traders/stats \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "0x93ab...9723",
    "metrics": ["pnl", "roi", "win_rate", "drawdown"],
    "timeframe": "30d"
  }'
```

### Step 4: Cross-Venue Comparison

```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/cross/compare \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "nba-finals-2026",
    "venues": ["polymarket", "kalshi"],
    "metrics": ["price_gap", "volume_ratio"]
  }'
```

### Step 5: Sentiment Analysis

```bash
curl -X POST https://narrative.agent.heisenberg.so/v2/signals/sentiment \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "market_slug": "nba-finals-2026-celtics",
    "sources": ["twitter", "reddit", "news"],
    "window": "24h"
  }'
```

### Python Example

```python
import requests

BASE_URL = "https://narrative.agent.heisenberg.so/v2"
HEADERS = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}

# Fetch markets
response = requests.post(
    f"{BASE_URL}/markets/retrieve",
    headers=HEADERS,
    json={
        "agent_id": 574,
        "params": {"min_volume": "500"},
        "pagination": {"limit": 20, "offset": 0},
        "formatter_config": {"format_type": "raw"}
    }
)
markets = response.json()

# Get trader stats
response = requests.post(
    f"{BASE_URL}/traders/stats",
    headers=HEADERS,
    json={
        "wallet": "0x93ab...9723",
        "metrics": ["pnl", "roi", "win_rate"],
        "timeframe": "30d"
    }
)
stats = response.json()
print(f"PnL: ${stats['total_pnl']:,.2f}, Win Rate: {stats['win_rate']:.0%}")
```

### Endpoint Summary

| Endpoint | Method | Description |
|---|---|---|
| `/v2/markets/retrieve` | POST | Market data: prices, volume, outcomes, metadata, historical |
| `/v2/traders/stats` | POST | Trader analytics: PnL, ROI, win rate, drawdown, trade count |
| `/v2/cross/compare` | POST | Cross-venue: match markets across Polymarket & Kalshi, price gaps |
| `/v2/signals/sentiment` | POST | Sentiment: social media analysis, narrative trends, influencer signals |

### Key Differences from Official Polymarket API

| Aspect | Polymarket US Official API | Falcon API |
|---|---|---|
| **Purpose** | Trading + market data | Analytics + intelligence |
| **Auth** | API Key ID + Ed25519 signature | Bearer token |
| **HTTP methods** | GET and POST | POST only |
| **Can place orders** | Yes | No |
| **Trader-level analytics** | No | Yes |
| **Cross-venue data** | No | Yes (Polymarket + Kalshi) |
| **Sentiment analysis** | No | Yes |
| **Base URL** | `api.polymarket.us` / `gateway.polymarket.us` | `narrative.agent.heisenberg.so` |
| **MCP integration** | No | Yes (native Claude MCP) |

---

---
---

# PART 3: GitHub Repositories, SDKs & Community Tools

---

## Table of Contents (Tools & Repos)

31. [Official Polymarket SDKs & Repos](#31-official-polymarket-sdks--repos)
32. [Official Polymarket US SDKs](#32-official-polymarket-us-sdks)
33. [Official AI Agents Framework](#33-official-ai-agents-framework)
34. [Community Python Libraries](#34-community-python-libraries)
35. [Data Pipelines & Scrapers](#35-data-pipelines--scrapers)
36. [Trading Bots](#36-trading-bots)
37. [Market Making Bots](#37-market-making-bots)
38. [MCP Servers (Claude / AI Agent Integration)](#38-mcp-servers-claude--ai-agent-integration)
39. [Analytics Platforms & Dashboards](#39-analytics-platforms--dashboards)
40. [Browser Extensions & UI Tools](#40-browser-extensions--ui-tools)
41. [AI-Powered Analysis Tools](#41-ai-powered-analysis-tools)
42. [Awesome Lists & Meta-Resources](#42-awesome-lists--meta-resources)

---

## 31. Official Polymarket SDKs & Repos

These are maintained by the **Polymarket** GitHub organisation (`github.com/Polymarket`). They target Polymarket International (crypto/blockchain-based).

### Core SDKs

| Repo | Language | Description | Install |
|---|---|---|---|
| [`Polymarket/py-clob-client`](https://github.com/Polymarket/py-clob-client) | Python | Official Python client for the CLOB (Central Limit Order Book). Supports order placement, market data, order books, pricing, WebSocket. | `pip install py-clob-client` |
| [`@polymarket/clob-client`](https://github.com/Polymarket/clob-client) | TypeScript | Official TypeScript CLOB client. Order management, market data, WebSocket support. | `npm install @polymarket/clob-client` |
| [`Polymarket/polymarket-sdk`](https://github.com/Polymarket/polymarket-sdk) | TypeScript | SDK for interacting with Polymarket proxy wallets and trading operations. | Via npm |
| [`Polymarket/clob-order-utils`](https://github.com/Polymarket/clob-order-utils) | TypeScript | Order building and signing utilities for the CLOB. | Via npm |

### Builder & Relayer SDKs

| Repo | Language | Description |
|---|---|---|
| [`Polymarket/builder-signing-sdk`](https://github.com/Polymarket/builder-signing-sdk) | TypeScript | SDK for creating authenticated builder headers (Builder Program). |
| [`Polymarket/py-builder-signing-sdk`](https://github.com/Polymarket/py-builder-signing-sdk) | Python | Python SDK for builder authentication and signing. |
| [`Polymarket/py-builder-relayer-client`](https://github.com/Polymarket/py-builder-relayer-client) | Python | Client for submitting gasless transactions through Polymarket's relayer infrastructure. |

### Data & Infrastructure

| Repo | Language | Description |
|---|---|---|
| [`Polymarket/polymarket-subgraph`](https://github.com/Polymarket/polymarket-subgraph) | TypeScript | Public subgraph manifest for indexing on-chain trade, volume, user, liquidity, and market data. Uses The Graph protocol. |
| [`Polymarket/real-time-data-client`](https://github.com/Polymarket/real-time-data-client) | — | Client for real-time streaming data. |
| [`Polymarket/ctf-exchange`](https://github.com/Polymarket/ctf-exchange) | Solidity | The Conditional Token Framework (CTF) Exchange smart contracts. The on-chain settlement layer for Polymarket. 158+ stars, 344+ forks. |
| [`@polymarket/embeds`](https://github.com/Polymarket/embeds) | TypeScript | Official embeddable web components for displaying Polymarket markets in external websites. |

### Using py-clob-client (Quick Reference)

```python
from py_clob_client.client import ClobClient

# Public (no auth) — market data
client = ClobClient("https://clob.polymarket.com")
mid = client.get_midpoint("<token-id>")
price = client.get_price("<token-id>", side="BUY")
book = client.get_order_book("<token-id>")

# Authenticated — trading
client = ClobClient(
    "https://clob.polymarket.com",
    key="<private-key>",
    chain_id=137,
    signature_type=1,
    funder="<funder-address>"
)
client.set_api_creds(client.create_or_derive_api_creds())

# Place a market order
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

order = MarketOrderArgs(token_id="<token-id>", amount=25.0, side=BUY, order_type=OrderType.FOK)
signed = client.create_market_order(order)
resp = client.post_order(signed, OrderType.FOK)
```

---

## 32. Official Polymarket US SDKs

These are the SDKs specifically for **Polymarket US** (fiat/CFTC-regulated). They use different auth (Ed25519 API keys) and a different base URL (`api.polymarket.us`).

| Repo | Language | Description | Install |
|---|---|---|---|
| [`Polymarket/polymarket-us-python`](https://github.com/Polymarket/polymarket-us-python) | Python | Official Polymarket US Python SDK. MIT license. Requires Python 3.10+. | `pip install polymarket-us` |
| [`Polymarket/polymarket-us-typescript`](https://github.com/Polymarket/polymarket-us-typescript) | TypeScript | Official Polymarket US TypeScript SDK. MIT license. Requires Node.js 18+. | `npm install polymarket-us` |

### Python SDK Method Reference

```python
from polymarket_us import PolymarketUS

client = PolymarketUS()  # Public endpoints (no auth)

# Events
client.events.list({"limit": 10, "offset": 0, "active": True})
client.events.retrieve(123)
client.events.retrieve_by_slug("super-bowl-2025")

# Markets
client.markets.list()
client.markets.retrieve_by_slug("btc-100k")
client.markets.book("btc-100k")
client.markets.bbo("btc-100k")

# Search
client.search.query({"query": "bitcoin"})

# Series & Sports
client.series.list()
client.sports.list()

# Authenticated client — trading
import os
client = PolymarketUS(
    key_id=os.environ["POLYMARKET_KEY_ID"],
    secret_key=os.environ["POLYMARKET_SECRET_KEY"],
)

# Orders
client.orders.create({
    "marketSlug": "btc-100k-2025",
    "intent": "ORDER_INTENT_BUY_LONG",
    "type": "ORDER_TYPE_LIMIT",
    "price": {"value": "0.55", "currency": "USD"},
    "quantity": 100,
    "tif": "TIME_IN_FORCE_GOOD_TILL_CANCEL",
})
client.orders.list()
client.orders.cancel("<order-id>")

# Portfolio & Account
client.portfolio.positions()
client.account.balances()
```

### WebSocket (Async Only)

The US SDK also supports WebSocket connections for real-time order, position, balance, and market data streaming. WebSocket connections are async-only due to their event-driven nature.

---

## 33. Official AI Agents Framework

| Repo | Description |
|---|---|
| [`Polymarket/agents`](https://github.com/Polymarket/agents) | **Official** Polymarket AI Agents framework. A developer toolkit for building autonomous AI agents that trade on Polymarket. MIT license. |

### Architecture

The framework features modular components:

- **Polymarket.py** — Core class for API interaction, order execution, market/event data retrieval, order building and signing.
- **Gamma.py** — `GammaMarketClient` class interfacing with the Gamma API for market and event metadata.
- **Chroma.py** — ChromaDB integration for vectorising news sources and other API data. Supports custom vector database implementations.
- **Objects.py** — Pydantic data models for trades, markets, events, and related entities.
- **cli.py** — Primary user interface. Commands for API interaction, news retrieval, local data queries, LLM prompts, and trade execution.

### Usage

```bash
git clone https://github.com/Polymarket/agents.git
cd agents
# Load your wallet with USDC
# Use the CLI or build custom agents
```

---

## 34. Community Python Libraries

| Repo / Package | Description |
|---|---|
| [`polymarket-apis`](https://pypi.org/project/polymarket-apis/) | Unified Polymarket APIs with Pydantic data validation. Wraps CLOB, Gamma, Data, Web3, WebSocket, and GraphQL clients into one package. Install: `pip install polymarket-apis` |
| [`@polybased/sdk`](https://github.com/polybased/sdk) | Comprehensive TypeScript toolkit with real-time data and WebSocket streams. |

### polymarket-apis Key Concepts

The `polymarket-apis` package provides unified access to all Polymarket API layers with Pydantic models:

- **Events** contain multiple **Markets** (instruments)
- **Markets** contain two **Outcomes** (typically Yes/No), each identified by a **token ID**
- Tokens are ERC-1155 assets on Polygon blockchain
- A BUY order for Outcome 1 at price X is simultaneously visible as a SELL order for Outcome 2 at price (100¢ − X)
- Splits are the only way tokens are created — either user-initiated or automatic matching

---

## 35. Data Pipelines & Scrapers

### poly_data — Comprehensive Trade Data Pipeline

| Repo | [`warproxxx/poly_data`](https://github.com/warproxxx/poly_data) |
|---|---|
| **Description** | End-to-end pipeline for fetching, processing, and analysing Polymarket trading data. Collects market info, order-filled events from the Goldsky subgraph, and processes them into structured trade data. |
| **Language** | Python (UV package manager) |
| **Data snapshot** | Pre-built snapshot available to save 2+ days of initial collection |

**Architecture:**
```
poly_data/
├── update_all.py           # Main orchestrator
├── update_utils/
│   ├── update_markets.py   # Fetch markets from Polymarket API
│   ├── update_goldsky.py   # Scrape order events from Goldsky subgraph
│   └── process_live.py     # Process orders into structured trades
├── markets.csv             # Main markets dataset
├── goldsky/
│   └── orderFilled.csv     # Raw order-filled events
└── processed/
    └── trades.csv          # Processed trade data
```

**Output fields:**
- `markets.csv`: createdAt, id, question, answer1, answer2, neg_risk, market_slug, token1, token2, condition_id, volume, ticker, closedTime
- `trades.csv`: timestamp, maker, makerAssetId, makerAmountFilled, taker, takerAssetId, takerAmountFilled, transactionHash

### polymarket-data-scraper — Multi-Sport & Crypto Data Recorder

| Repo | [`TenghanZhong/polymarket-data-scraper`](https://github.com/TenghanZhong/polymarket-data-scraper) |
|---|---|
| **Description** | Tool-chain for gathering prediction market and financial data from Polymarket, Deribit, and more. Records structured data into PostgreSQL for quantitative analysis. |
| **Sports covered** | MLB, NBA (auto-discovery of game markets, per-minute price snapshots, live score tracking) |
| **Crypto covered** | Hourly BTC/ETH up-or-down markets, monthly price targets, scalar interval markets |
| **Deribit** | Daily BTC option chain snapshots via ccxt |

**Key scripts:**
- `MLB_Auto.py` / `NBA_Auto.py` — Auto-discover and monitor sports markets, record bid/ask per minute
- `hourly_crypto.py` — Generate current market slug, create PostgreSQL table, log yes/no bid/ask every minute
- `monthly_crypto.py` — Monitor monthly price-target markets for BTC, ETH, XRP
- `poly_interval_loader.py` — Discover all active scalar interval markets, write minute-level bracket snapshots

---

## 36. Trading Bots

### polymarket-trading-bot — Beginner-Friendly Bot

| Repo | [`discountry/polymarket-trading-bot`](https://github.com/discountry/polymarket-trading-bot) |
|---|---|
| **Description** | Beginner-friendly Python trading bot with gasless transactions, WebSocket data, flash crash strategy. 89 unit tests. |
| **Features** | Simple API, gasless transactions (Builder Program), real-time WebSocket, 15-minute BTC/ETH/SOL/XRP market support, encrypted key storage |

**Architecture:**
```
src/
├── bot.py              # TradingBot — main interface
├── client.py           # API clients (CLOB, Relayer)
├── signer.py           # Order signing (EIP-712)
├── gamma_client.py     # 15-minute market discovery
└── websocket_client.py # Real-time WebSocket client
strategies/
├── flash_crash_strategy.py  # Volatility trading
└── orderbook_tui.py         # Real-time orderbook display
```

### Polymarket-BTC-15-Minute-Trading-Bot — Production-Grade Algo Bot

| Repo | [`aulekator/Polymarket-BTC-15-Minute-Trading-Bot`](https://github.com/aulekator/Polymarket-BTC-15-Minute-Trading-Bot) |
|---|---|
| **Description** | Production-grade 7-phase algorithmic trading bot for 15-minute BTC prediction markets. Multiple signal sources, professional risk management, self-learning capabilities. |
| **Data sources** | Binance WebSocket, Coinbase REST, Fear & Greed Index, social sentiment |
| **Risk management** | Position sizing, stop-loss/take-profit, exposure limits |
| **Monitoring** | Grafana dashboards, Prometheus metrics |

### polybot — Strategy Reverse-Engineering Toolkit

| Repo | [`ent0n29/polybot`](https://github.com/ent0n29/polybot) |
|---|---|
| **Description** | Open-source trading infrastructure and strategy reverse-engineering toolkit. Microservices architecture with Kafka, ClickHouse, Grafana. Includes complete-set arbitrage strategy for Up/Down binaries. |
| **Stack** | Spring Boot microservices, Kafka data pipeline, ClickHouse analytics DB, Grafana monitoring |
| **Default mode** | Paper trading |

**Architecture:**
```
polybot/
├── polybot-core/
├── executor-service/
├── strategy-service/
├── ingestor-service/
├── analytics-service/
├── infrastructure-orchestrator-service/
├── research/
└── monitoring/
```

---

## 37. Market Making Bots

### polymarket-automated-mm (Poly-Maker)

| Repo | [`terrytrl100/polymarket-automated-mm`](https://github.com/terrytrl100/polymarket-automated-mm) |
|---|---|
| **Description** | Automated market making bot. Maintains orders on both sides with configurable parameters. Reward-optimised pricing based on Polymarket's maker reward formula. |
| **Features** | Automated market selection by profitability, position management with risk controls, Google Sheets config, maker reward tracking, intelligent cancellation thresholds (95% reduction in unnecessary order churn) |

### poly-market-maker (Official)

| Repo | [`Polymarket/poly-market-maker`](https://github.com/Polymarket/poly-market-maker) |
|---|---|
| **Description** | Official CLOB market maker with bands or AMM strategy. Docker support. |

### Production Market Making Bot (240+ stars)

A production-ready market-making bot managing inventory, placing optimal quotes, handling cancel/replace cycles, and applying automated risk controls. Designed for efficient spread capture, balanced YES/NO exposure, and real-time orderbook trading with low latency.

---

## 38. MCP Servers (Claude / AI Agent Integration)

MCP (Model Context Protocol) servers allow AI assistants like Claude to interact with Polymarket data programmatically.

### caiovicentino/polymarket-mcp-server (160+ stars)

| Repo | [`caiovicentino/polymarket-mcp-server`](https://github.com/caiovicentino/polymarket-mcp-server) |
|---|---|
| **Description** | AI-powered MCP server with 45 tools: market discovery (8), trading engine (12), market analysis (10), portfolio manager (8), plus real-time WebSocket monitoring. Enterprise-grade safety features. |
| **Trading safety** | Configurable max order size, total exposure, per-market position size, min liquidity, max spread tolerance, confirmation thresholds |

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "polymarket": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "polymarket_mcp.server"],
      "env": {
        "POLYGON_PRIVATE_KEY": "your_private_key",
        "POLYGON_ADDRESS": "0xYourAddress"
      }
    }
  }
}
```

### IQAIcom/mcp-polymarket

| Repo | [`IQAIcom/mcp-polymarket`](https://github.com/IQAIcom/mcp-polymarket) |
|---|---|
| **Description** | Full-featured MCP server: market discovery, real-time pricing, order books, trading (limit/market orders), portfolio positions with P&L. |
| **Install** | `npx -y @iqai/mcp-polymarket` |

### guangxiangdebizi/PolyMarket-MCP

| Repo | [`guangxiangdebizi/PolyMarket-MCP`](https://github.com/guangxiangdebizi/PolyMarket-MCP) |
|---|---|
| **Description** | Comprehensive MCP server. Market data, user positions, trading history, order books with liquidity analysis, activity tracking. SSE transport. |

### berlinbra/polymarket-mcp

| Repo | [`berlinbra/polymarket-mcp`](https://github.com/berlinbra/polymarket-mcp) |
|---|---|
| **Description** | Simpler, read-only MCP server. Good starting point for learning. Market listings, prices, historical data with configurable timeframes (1d/7d/30d/all). |

---

## 39. Analytics Platforms & Dashboards

| Platform | Description | URL |
|---|---|---|
| **Polymarket Analytics** | Market search, activity monitoring, portfolio tracking. Powers the Falcon API. | polymarketanalytics.com |
| **Oddpool** | "Bloomberg for prediction markets." Cross-venue aggregation (Polymarket + Kalshi), live odds, spreads, liquidity, order book depth, arbitrage detection, historical data. | oddpool.com |
| **loki.red** | Comprehensive Polymarket statistics and market insights. | loki.red |
| **Dune Analytics** | Multiple community-created dashboards for volume tracking, open interest, user analytics. | dune.com |
| **Bitquery** | Blockchain data and on-chain analytics for Polymarket smart contracts. | bitquery.io |

---

## 40. Browser Extensions & UI Tools

| Tool | Description |
|---|---|
| **PolyPulse** | Chrome extension: AI-powered news insights with Perplexity AI integration, auto market detection, secure API storage. Free. |
| **Polyteller** | Real-time countdowns, smart notifications, privacy mode. |
| **Polyhelper** | Enhanced Polymarket experience with countdowns, notifications, privacy features. |
| **Nevua Markets Plugin** | Price alerts with over/under thresholds and real-time monitoring. |
| **PolymarketOddsConverter** | Converts probabilities to decimal odds. Available for Chrome and Firefox. |
| **Polymarket Extension for Raycast** | Search and view markets from Raycast with price charts, volume tracking, real-time data. |
| **Polyprophet** | Chrome extension: AI-powered real-time predictions using multiple AI models and historical data analysis. |

---

## 41. AI-Powered Analysis Tools

| Tool | Description |
|---|---|
| **Alphascope** | AI-driven market intelligence engine: real-time signals, research, probability shifts. |
| **Polytrader** | AI-driven analysis, automated trading strategies, social sentiment tracking. |
| **Polybro** | Autonomous AI agent conducting structured research across papers, news, and live data for evidence-based predictions. |
| **Inside Edge** | Identifies market inefficiencies with quantified edge percentages. |
| **Jatevo** | Deep research platform powered by 6-agent AI pipeline with Polymarket API integration. |
| **PolyMaster** | Whale tracking, predictive modelling, real-time market intelligence. |
| **PolyTale** | First prediction market research AI agent on Twitter, providing real-time insights and whale tracking. |
| **Poly Cafe** | SocialFi platform with persistent 3D AI agents ("Quants") that autonomously discover, analyse, and trade on prediction markets 24/7. |
| **Sportstensor** | Decentralised AI-powered sports prediction using collective intelligence and ensemble modelling. |
| **BillyBets** | Autonomous 24/7 AI sports betting agent analysing real-time data from Sportstensor and top bettors. |

---

## 42. Awesome Lists & Meta-Resources

These curated lists aggregate the full ecosystem of tools:

| Repo | Description |
|---|---|
| [`harish-garg/Awesome-Polymarket-Tools`](https://github.com/harish-garg/Awesome-Polymarket-Tools) | Comprehensive list of tools, libraries, bots, and resources for the Polymarket ecosystem. Covers trading, analytics, SDKs, extensions, and more. |
| [`aarora4/Awesome-Prediction-Market-Tools`](https://github.com/aarora4/Awesome-Prediction-Market-Tools) | The most complete community-maintained directory of prediction market tools. Covers Polymarket, Kalshi, Manifold, Hyperliquid. Analytics, bots, dashboards, APIs, data feeds, alert systems, educational resources. |

---

## Quick Reference: Which Tool for Which Job

| Use Case | Recommended Tool(s) |
|---|---|
| **Trade on Polymarket US (fiat)** | `polymarket-us` Python/TS SDK |
| **Trade on Polymarket International (crypto)** | `py-clob-client` or `@polymarket/clob-client` |
| **Read-only market data (US)** | `polymarket-us` SDK (no auth needed) |
| **Read-only market data (International)** | `py-clob-client` or Gamma API directly |
| **Trader analytics / PnL / whale tracking** | Falcon API (`polymarketanalytics.com`) |
| **Cross-venue comparison (PM vs Kalshi)** | Falcon API or Oddpool |
| **Sentiment analysis** | Falcon API `/v2/signals/sentiment` |
| **Historical trade data pipeline** | `warproxxx/poly_data` |
| **Sports market data scraping** | `TenghanZhong/polymarket-data-scraper` |
| **AI agent integration with Claude** | MCP servers (caiovicentino, IQAIcom, berlinbra) |
| **Autonomous AI trading** | `Polymarket/agents` framework |
| **Market making** | `Polymarket/poly-market-maker` or `polymarket-automated-mm` |
| **Algo trading bot (BTC 15-min)** | `aulekator/Polymarket-BTC-15-Minute-Trading-Bot` |
| **Strategy reverse-engineering** | `ent0n29/polybot` |
| **On-chain data / subgraph queries** | `Polymarket/polymarket-subgraph` |
| **Smart contract interaction** | `Polymarket/ctf-exchange` (Solidity) |
| **Gasless trading via Builder Program** | `py-builder-relayer-client` + `py-builder-signing-sdk` |
| **Embed markets in your website** | `@polymarket/embeds` |

---

*Documentation compiled from [docs.polymarket.us](https://docs.polymarket.us), [api.polymarketanalytics.com](https://api.polymarketanalytics.com), and public GitHub repositories. For the latest information, always refer to the official sources. Falcon API is a third-party product by Polymarket Analytics. Community tools are independently maintained and not endorsed by Polymarket.*
