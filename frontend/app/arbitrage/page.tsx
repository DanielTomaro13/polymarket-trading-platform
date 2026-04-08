"use client";

import { useState } from "react";

/* ─── Types ─── */
interface ArbOpportunity {
  id: string;
  topic: string;
  pmSlug: string;
  kalshiTicker: string;
  pmYesPrice: number;
  kalshiYesPrice: number;
  grossGap: number;
  pmFee: number;
  kalshiFee: number;
  netGap: number;
  direction: string;
  volumeRatio: number | null;
  isActionable: boolean;
  detectedAt: string;
}

interface CompleteSetArb {
  eventName: string;
  outcomes: { name: string; askPrice: number }[];
  totalCost: number;
  profit: number;
  roiPct: number;
  isActionable: boolean;
}

/* ─── Demo Data ─── */
const demoArbs: ArbOpportunity[] = [
  {
    id: "1", topic: "Will the Chiefs win Super Bowl LXI?",
    pmSlug: "chiefs-super-bowl-lxi", kalshiTicker: "CHIEFS-SB-LXI",
    pmYesPrice: 0.24, kalshiYesPrice: 0.28, grossGap: 0.04,
    pmFee: 0.0091, kalshiFee: 0.07,
    netGap: 0.0209, direction: "BUY PM / SELL KALSHI",
    volumeRatio: 3.2, isActionable: true, detectedAt: "12s ago",
  },
  {
    id: "2", topic: "Will UConn win March Madness 2027?",
    pmSlug: "uconn-march-madness-2027", kalshiTicker: "UCONN-MM-27",
    pmYesPrice: 0.09, kalshiYesPrice: 0.12, grossGap: 0.03,
    pmFee: 0.0041, kalshiFee: 0.07,
    netGap: 0.0141, direction: "BUY PM / SELL KALSHI",
    volumeRatio: 1.8, isActionable: false, detectedAt: "34s ago",
  },
  {
    id: "3", topic: "Djokovic wins 2026 French Open",
    pmSlug: "djokovic-french-open-2026", kalshiTicker: "DJOK-FO-26",
    pmYesPrice: 0.42, kalshiYesPrice: 0.38, grossGap: 0.04,
    pmFee: 0.0122, kalshiFee: 0.07,
    netGap: 0.0222, direction: "BUY KALSHI / SELL PM",
    volumeRatio: 0.7, isActionable: true, detectedAt: "1m ago",
  },
  {
    id: "4", topic: "Oilers win 2026 Stanley Cup",
    pmSlug: "oilers-stanley-cup-2026", kalshiTicker: "OILERS-SC-26",
    pmYesPrice: 0.29, kalshiYesPrice: 0.31, grossGap: 0.02,
    pmFee: 0.0103, kalshiFee: 0.07,
    netGap: 0.0003, direction: "BUY PM / SELL KALSHI",
    volumeRatio: 2.1, isActionable: false, detectedAt: "2m ago",
  },
];

const demoCompleteSets: CompleteSetArb[] = [
  {
    eventName: "NBA Championship 2026-27",
    outcomes: [
      { name: "Celtics", askPrice: 0.33 },
      { name: "Thunder", askPrice: 0.18 },
      { name: "Nuggets", askPrice: 0.12 },
      { name: "Knicks", askPrice: 0.10 },
      { name: "Field", askPrice: 0.22 },
    ],
    totalCost: 0.95, profit: 0.05, roiPct: 5.26, isActionable: true,
  },
  {
    eventName: "2026 World Series",
    outcomes: [
      { name: "Yankees", askPrice: 0.19 },
      { name: "Dodgers", askPrice: 0.22 },
      { name: "Braves", askPrice: 0.14 },
      { name: "Field", askPrice: 0.48 },
    ],
    totalCost: 1.03, profit: -0.03, roiPct: -2.91, isActionable: false,
  },
];

/* ─── Page ─── */
export default function ArbitragePage() {
  const [scanMode, setScanMode] = useState<"cross-venue" | "complete-set">("cross-venue");
  const [scanning, setScanning] = useState(false);

  const actionableCount = demoArbs.filter((a) => a.isActionable).length;
  const totalNetValue = demoArbs
    .filter((a) => a.isActionable)
    .reduce((s, a) => s + a.netGap * 100, 0); // per 100 contracts

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
          <a href="/arbitrage" className="nav-item active">Arbitrage</a>
          <a href="/sentiment" className="nav-item">Sentiment</a>
          <a href="/portfolio" className="nav-item">Portfolio</a>
        </nav>
        <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
          <span className="live-dot" style={{ marginRight: 6 }} />
          Connected
        </span>
      </header>

      <main className="main-content">
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 6 }}>
            Arbitrage Scanner
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Cross-venue price discrepancy detection between Polymarket and Kalshi
          </p>
        </div>

        {/* Summary Stats */}
        <div className="data-grid cols-4" style={{ marginBottom: 24 }}>
          <div className="stat-box">
            <div className="stat-label">Opportunities Found</div>
            <div className="stat-value">{demoArbs.length}</div>
            <div className="stat-sub">across all matched markets</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Actionable</div>
            <div className="stat-value text-green">{actionableCount}</div>
            <div className="stat-sub">net gap &gt; 2¢ after fees</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Best Net Gap</div>
            <div className="stat-value mono text-green">
              {Math.max(...demoArbs.map((a) => a.netGap)).toFixed(4)}¢
            </div>
            <div className="stat-sub">per contract</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Est. Profit (100 lots)</div>
            <div className="stat-value mono text-green">
              ${totalNetValue.toFixed(2)}
            </div>
            <div className="stat-sub">on actionable opportunities</div>
          </div>
        </div>

        {/* Mode Tabs */}
        <div className="filters-bar">
          <button
            className={`filter-chip ${scanMode === "cross-venue" ? "active" : ""}`}
            onClick={() => setScanMode("cross-venue")}
          >
            ↔️ Cross-Venue (PM ↔ Kalshi)
          </button>
          <button
            className={`filter-chip ${scanMode === "complete-set" ? "active" : ""}`}
            onClick={() => setScanMode("complete-set")}
          >
            🎯 Complete-Set Arbitrage
          </button>
          <div style={{ flex: 1 }} />
          <button
            className="btn btn-primary btn-sm"
            onClick={() => { setScanning(true); setTimeout(() => setScanning(false), 1500); }}
          >
            {scanning ? "Scanning..." : "🔄 Scan Now"}
          </button>
        </div>

        {scanMode === "cross-venue" ? (
          /* Cross-Venue Table */
          <div className="table-container fade-in">
            <table className="table">
              <thead>
                <tr>
                  <th>Market</th>
                  <th>PM Price</th>
                  <th>Kalshi Price</th>
                  <th>Gross Gap</th>
                  <th>Fees</th>
                  <th>Net Gap</th>
                  <th>Direction</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {demoArbs.map((arb) => (
                  <tr key={arb.id}>
                    <td style={{ fontWeight: 500, color: "var(--text-primary)", maxWidth: 250 }}>
                      {arb.topic}
                      <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: 2 }}>
                        {arb.detectedAt}
                      </div>
                    </td>
                    <td className="mono">${arb.pmYesPrice.toFixed(2)}</td>
                    <td className="mono">${arb.kalshiYesPrice.toFixed(2)}</td>
                    <td className="mono" style={{ color: arb.grossGap >= 0.03 ? "var(--green)" : "var(--yellow)" }}>
                      {(arb.grossGap * 100).toFixed(1)}¢
                    </td>
                    <td className="mono text-muted" style={{ fontSize: "0.75rem" }}>
                      PM: {(arb.pmFee * 100).toFixed(2)}¢<br />
                      K: {(arb.kalshiFee * 100).toFixed(1)}¢
                    </td>
                    <td>
                      <span
                        className="mono"
                        style={{
                          fontWeight: 700,
                          color: arb.netGap >= 0.02 ? "var(--green)" : arb.netGap > 0 ? "var(--yellow)" : "var(--red)",
                        }}
                      >
                        {(arb.netGap * 100).toFixed(2)}¢
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${arb.direction.includes("BUY PM") ? "badge-blue" : "badge-purple"}`} style={{ fontSize: "0.65rem" }}>
                        {arb.direction}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${arb.isActionable ? "badge-green" : "badge-yellow"}`}>
                        {arb.isActionable ? "ACTIONABLE" : "BELOW THRESHOLD"}
                      </span>
                    </td>
                    <td>
                      <button
                        className={`btn btn-sm ${arb.isActionable ? "btn-green" : "btn-ghost"}`}
                        disabled={!arb.isActionable}
                      >
                        Execute
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Complete-Set Table */
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {demoCompleteSets.map((cs, i) => (
              <div key={i} className="card fade-in" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="card-header">
                  <div>
                    <div className="card-title">{cs.eventName}</div>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: 2 }}>
                      {cs.outcomes.length} outcomes in mutually exclusive group
                    </div>
                  </div>
                  <span className={`badge ${cs.isActionable ? "badge-green" : "badge-red"}`}>
                    {cs.isActionable ? "PROFITABLE" : "NO ARB"}
                  </span>
                </div>

                {/* Outcome breakdown */}
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
                  {cs.outcomes.map((o) => (
                    <div
                      key={o.name}
                      style={{
                        padding: "8px 14px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "var(--radius-md)",
                        fontSize: "0.8rem",
                      }}
                    >
                      <span style={{ color: "var(--text-secondary)" }}>{o.name}</span>
                      <span className="mono" style={{ marginLeft: 8, fontWeight: 600 }}>
                        ${o.askPrice.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Summary */}
                <div
                  style={{
                    display: "flex",
                    gap: 32,
                    padding: "12px 16px",
                    background: "var(--bg-tertiary)",
                    borderRadius: "var(--radius-md)",
                    fontSize: "0.85rem",
                  }}
                >
                  <div>
                    <span className="text-muted">Total Cost: </span>
                    <span className="mono" style={{ fontWeight: 600 }}>${cs.totalCost.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-muted">Settlement: </span>
                    <span className="mono" style={{ fontWeight: 600 }}>$1.00</span>
                  </div>
                  <div>
                    <span className="text-muted">Profit/Set: </span>
                    <span className={`mono ${cs.profit > 0 ? "text-green" : "text-red"}`} style={{ fontWeight: 700 }}>
                      {cs.profit > 0 ? "+" : ""}${cs.profit.toFixed(2)} ({cs.roiPct.toFixed(1)}%)
                    </span>
                  </div>
                  {cs.isActionable && (
                    <div style={{ marginLeft: "auto" }}>
                      <button className="btn btn-green btn-sm">Execute Complete Set</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
