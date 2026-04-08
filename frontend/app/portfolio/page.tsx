"use client";

import { useState } from "react";

/* ─── Types ─── */
interface PortPosition {
  slug: string;
  question: string;
  side: "long" | "short";
  quantity: number;
  avgEntry: number;
  currentPrice: number;
  marketValue: number;
  pnl: number;
  pnlPct: number;
  sport: string;
}

interface TradeHistory {
  id: string;
  slug: string;
  side: string;
  price: number;
  quantity: number;
  fee: number;
  timestamp: string;
}

/* ─── Demo ─── */
const demoPositions: PortPosition[] = [
  { slug: "chiefs-super-bowl-lxi", question: "Chiefs win Super Bowl LXI?", side: "long", quantity: 200, avgEntry: 0.22, currentPrice: 0.24, marketValue: 48.0, pnl: 4.0, pnlPct: 9.09, sport: "NFL" },
  { slug: "celtics-nba-championship", question: "Celtics win NBA Championship?", side: "long", quantity: 150, avgEntry: 0.35, currentPrice: 0.32, marketValue: 48.0, pnl: -4.5, pnlPct: -8.57, sport: "NBA" },
  { slug: "mahomes-over-2-5-tds", question: "Mahomes over 2.5 TDs", side: "long", quantity: 100, avgEntry: 0.55, currentPrice: 0.595, marketValue: 59.5, pnl: 4.5, pnlPct: 8.18, sport: "NFL" },
  { slug: "djokovic-french-open", question: "Djokovic wins French Open?", side: "short", quantity: 75, avgEntry: 0.60, currentPrice: 0.42, marketValue: 43.5, pnl: 13.5, pnlPct: 30.0, sport: "Tennis" },
  { slug: "yankees-world-series", question: "Yankees win World Series?", side: "long", quantity: 300, avgEntry: 0.15, currentPrice: 0.18, marketValue: 54.0, pnl: 9.0, pnlPct: 20.0, sport: "MLB" },
];

const demoHistory: TradeHistory[] = [
  { id: "1", slug: "chiefs-super-bowl-lxi", side: "BUY YES", price: 0.22, quantity: 200, fee: 1.72, timestamp: "2026-04-05 10:30" },
  { id: "2", slug: "celtics-nba-championship", side: "BUY YES", price: 0.35, quantity: 150, fee: 1.71, timestamp: "2026-04-05 11:15" },
  { id: "3", slug: "djokovic-french-open", side: "SELL YES", price: 0.60, quantity: 75, fee: 0.90, timestamp: "2026-04-06 09:00" },
  { id: "4", slug: "mahomes-over-2-5-tds", side: "BUY YES", price: 0.55, quantity: 100, fee: 1.24, timestamp: "2026-04-06 14:45" },
  { id: "5", slug: "yankees-world-series", side: "BUY YES", price: 0.15, quantity: 300, fee: 1.91, timestamp: "2026-04-07 08:20" },
];

/* ─── Page ─── */
export default function PortfolioPage() {
  const [tab, setTab] = useState<"positions" | "history" | "margin">("positions");

  const totalValue = demoPositions.reduce((s, p) => s + p.marketValue, 0);
  const totalPnl = demoPositions.reduce((s, p) => s + p.pnl, 0);
  const totalPnlPct = (totalPnl / (totalValue - totalPnl)) * 100;
  const cashBalance = 750.00;
  const buyingPower = cashBalance - (cashBalance * 0.2); // 20% reserve

  // Sport allocation
  const sportAlloc: Record<string, number> = {};
  demoPositions.forEach((p) => {
    sportAlloc[p.sport] = (sportAlloc[p.sport] || 0) + p.marketValue;
  });

  return (
    <>
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">P</div>
          Polymarket Platform
          <span className="live-dot" style={{ marginLeft: 4 }} />
        </div>
        <nav className="nav">
          <a href="/" className="nav-item">Markets</a>
          <a href="/trading" className="nav-item">Trading</a>
          <a href="/arbitrage" className="nav-item">Arbitrage</a>
          <a href="/sentiment" className="nav-item">Sentiment</a>
          <a href="/portfolio" className="nav-item active">Portfolio</a>
        </nav>
        <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
          <span className="live-dot" style={{ marginRight: 6 }} />
          Connected
        </span>
      </header>

      <main className="main-content">
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 6 }}>
            Portfolio
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Positions, P&L tracking, margin analysis, and trade history
          </p>
        </div>

        {/* Portfolio Summary */}
        <div className="data-grid cols-4" style={{ marginBottom: 24 }}>
          <div className="stat-box">
            <div className="stat-label">Portfolio Value</div>
            <div className="stat-value mono">${(totalValue + cashBalance).toFixed(2)}</div>
            <div className="stat-sub">positions + cash</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Unrealised P&L</div>
            <div className={`stat-value mono ${totalPnl >= 0 ? "text-green" : "text-red"}`}>
              {totalPnl >= 0 ? "+" : ""}${totalPnl.toFixed(2)}
              <span style={{ fontSize: "0.85rem", marginLeft: 8 }}>
                ({totalPnlPct.toFixed(1)}%)
              </span>
            </div>
            <div className="stat-sub">across {demoPositions.length} positions</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Cash Balance</div>
            <div className="stat-value mono">${cashBalance.toFixed(2)}</div>
            <div className="stat-sub">available funds</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Buying Power</div>
            <div className="stat-value mono">${buyingPower.toFixed(2)}</div>
            <div className="stat-sub">after 20% reserve</div>
          </div>
        </div>

        {/* Sport Allocation */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <div className="card-title">Allocation by Sport</div>
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {Object.entries(sportAlloc)
              .sort((a, b) => b[1] - a[1])
              .map(([sport, value]) => {
                const pct = (value / totalValue) * 100;
                const colors: Record<string, string> = {
                  NFL: "var(--accent)", NBA: "var(--purple)", Tennis: "var(--green)",
                  MLB: "var(--red)", Golf: "var(--yellow)", NHL: "var(--cyan)",
                };
                return (
                  <div
                    key={sport}
                    style={{
                      flex: `${pct} 0 0`,
                      minWidth: 80,
                      padding: "10px 14px",
                      background: "var(--bg-tertiary)",
                      borderLeft: `3px solid ${colors[sport] || "var(--accent)"}`,
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>{sport}</div>
                    <div className="mono" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      ${value.toFixed(0)} ({pct.toFixed(0)}%)
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Tabs */}
        <div className="filters-bar" style={{ marginBottom: 0 }}>
          {(["positions", "history", "margin"] as const).map((t) => (
            <button
              key={t}
              className={`filter-chip ${tab === t ? "active" : ""}`}
              onClick={() => setTab(t)}
              style={{ textTransform: "capitalize" }}
            >
              {t === "margin" ? "Margin Analysis" : t === "history" ? "Trade History" : "Open Positions"}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {tab === "positions" && (
          <div className="table-container fade-in" style={{ marginTop: 16 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Market</th>
                  <th>Sport</th>
                  <th>Side</th>
                  <th>Qty</th>
                  <th>Entry</th>
                  <th>Current</th>
                  <th>Value</th>
                  <th>P&L</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {demoPositions.map((pos) => (
                  <tr key={pos.slug}>
                    <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>
                      {pos.question}
                    </td>
                    <td>
                      <span className="badge badge-blue" style={{ fontSize: "0.65rem" }}>{pos.sport}</span>
                    </td>
                    <td>
                      <span className={`badge ${pos.side === "long" ? "badge-green" : "badge-red"}`}>
                        {pos.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="mono">{pos.quantity}</td>
                    <td className="mono">${pos.avgEntry.toFixed(2)}</td>
                    <td className="mono">${pos.currentPrice.toFixed(2)}</td>
                    <td className="mono">${pos.marketValue.toFixed(2)}</td>
                    <td>
                      <span className={`mono ${pos.pnl >= 0 ? "text-green" : "text-red"}`} style={{ fontWeight: 600 }}>
                        {pos.pnl >= 0 ? "+" : ""}${pos.pnl.toFixed(2)} ({pos.pnlPct.toFixed(1)}%)
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-ghost btn-sm">Close</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === "history" && (
          <div className="table-container fade-in" style={{ marginTop: 16 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Market</th>
                  <th>Side</th>
                  <th>Price</th>
                  <th>Qty</th>
                  <th>Fee</th>
                  <th>Total Cost</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {demoHistory.map((trade) => (
                  <tr key={trade.id}>
                    <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>{trade.slug}</td>
                    <td>
                      <span className={`badge ${trade.side.includes("BUY") ? "badge-green" : "badge-red"}`} style={{ fontSize: "0.65rem" }}>
                        {trade.side}
                      </span>
                    </td>
                    <td className="mono">${trade.price.toFixed(2)}</td>
                    <td className="mono">{trade.quantity}</td>
                    <td className="mono text-muted">${trade.fee.toFixed(2)}</td>
                    <td className="mono">${(trade.price * trade.quantity + trade.fee).toFixed(2)}</td>
                    <td className="text-muted">{trade.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === "margin" && (
          <div className="fade-in" style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 16 }}>
            <div className="data-grid cols-3">
              <div className="stat-box">
                <div className="stat-label">Gross Margin Required</div>
                <div className="stat-value mono">${totalValue.toFixed(2)}</div>
                <div className="stat-sub">without ME offsets</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">ME Savings</div>
                <div className="stat-value mono text-green">$18.80</div>
                <div className="stat-sub">from 1 ME group (NFL)</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Net Margin Required</div>
                <div className="stat-value mono">${(totalValue - 18.8).toFixed(2)}</div>
                <div className="stat-sub">actual buying power locked</div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">Mutually Exclusive Groups</div>
              </div>
              <div style={{
                padding: "12px 16px",
                background: "var(--bg-tertiary)",
                borderRadius: "var(--radius-md)",
                fontSize: "0.85rem",
              }}>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>🏈 NFL Futures (2 positions)</div>
                <div style={{ display: "flex", gap: 24, color: "var(--text-secondary)" }}>
                  <span>Chiefs Super Bowl: $48.00</span>
                  <span>Mahomes o2.5 TDs: $59.50</span>
                </div>
                <div style={{ marginTop: 8, fontSize: "0.8rem" }}>
                  <span className="text-muted">Without ME: </span>
                  <span className="mono">$107.50</span>
                  <span className="text-muted"> → With ME: </span>
                  <span className="mono text-green">$59.50</span>
                  <span className="text-muted"> (savings: </span>
                  <span className="mono text-green">$48.00</span>
                  <span className="text-muted">)</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  );
}
