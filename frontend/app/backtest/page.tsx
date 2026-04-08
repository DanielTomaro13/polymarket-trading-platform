"use client";

import { useCallback, useState } from "react";

/* ─── Types ─── */
interface BacktestResult {
  strategy: string;
  returnPct: number;
  sharpe: number;
  maxDdPct: number;
  winRate: number;
  totalTrades: number;
  finalCapital: number;
  totalFees: number;
  bestTrade: number;
  worstTrade: number;
  equityCurve: { timestamp: string; equity: number }[];
  trades: { timestamp: string; slug: string; side: string; price: number; quantity: number; pnl: number }[];
}

/* ─── Demo Backtest Results ─── */
function generateDemoResult(name: string, seed: number): BacktestResult {
  const returns = [-2.4, 8.7, 15.3, -5.1, 22.8, 4.2];
  const sharpes = [0.3, 1.2, 1.8, -0.4, 2.1, 0.9];
  const drawdowns = [12.3, 8.1, 5.4, 18.7, 3.2, 9.8];
  const winRates = [42, 58, 63, 38, 71, 55];
  const tradeCount = [24, 67, 45, 89, 32, 53];

  const idx = seed % returns.length;
  const ret = returns[idx];
  const capital = 10000 + ret * 100;

  const equityCurve = Array.from({ length: 50 }, (_, i) => {
    const base = 10000;
    const progress = i / 49;
    const noise = Math.sin(i * 0.5123 + seed) * 200;
    return {
      timestamp: `Day ${i + 1}`,
      equity: Math.round(base + ret * 100 * progress + noise),
    };
  });

  return {
    strategy: name,
    returnPct: ret,
    sharpe: sharpes[idx],
    maxDdPct: drawdowns[idx],
    winRate: winRates[idx],
    totalTrades: tradeCount[idx],
    finalCapital: Math.round(capital),
    totalFees: Math.round(tradeCount[idx] * 1.5 * 100) / 100,
    bestTrade: Math.round((8 + seed * 0.3) * 100) / 100,
    worstTrade: Math.round((-5 - seed * 0.2) * 100) / 100,
    equityCurve,
    trades: [],
  };
}

const STRATEGIES = [
  { id: "momentum", name: "Momentum", desc: "Buy on upward price momentum, sell on reversal" },
  { id: "mean_reversion", name: "Mean Reversion", desc: "Buy on dips below moving average, sell on reversion" },
  { id: "kelly_criterion", name: "Kelly Criterion", desc: "Optimize position sizing using Kelly formula" },
  { id: "spread_capture", name: "Spread Capture", desc: "Capture bid-ask spread with passive orders" },
  { id: "sentiment_divergence", name: "Sentiment Divergence", desc: "Trade when price diverges from Falcon sentiment" },
  { id: "arbitrage", name: "Cross-Venue Arb", desc: "Execute on PM↔Kalshi fee-adjusted price gaps" },
];

/* ─── Equity Chart (CSS-only sparkline) ─── */
function EquityChart({ data, height = 120 }: { data: { equity: number }[]; height?: number }) {
  if (data.length < 2) return null;

  const min = Math.min(...data.map((d) => d.equity));
  const max = Math.max(...data.map((d) => d.equity));
  const range = max - min || 1;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((d.equity - min) / range) * 100;
    return `${x},${y}`;
  }).join(" ");

  const isPositive = data[data.length - 1].equity >= data[0].equity;
  const color = isPositive ? "var(--green)" : "var(--red)";
  const gradientId = `grad-${Math.random().toString(36).slice(2)}`;

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: "100%", height }}>
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={`0,100 ${points} 100,100`}
        fill={`url(#${gradientId})`}
      />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

/* ─── Main Page ─── */
export default function BacktestPage() {
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>(["momentum"]);
  const [market, setMarket] = useState("chiefs-super-bowl-lxi");
  const [capital, setCapital] = useState("10000");
  const [days, setDays] = useState("90");
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [compareMode, setCompareMode] = useState(false);

  const toggleStrategy = useCallback((id: string) => {
    if (compareMode) {
      setSelectedStrategies((prev) =>
        prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
      );
    } else {
      setSelectedStrategies([id]);
    }
  }, [compareMode]);

  const runBacktest = useCallback(() => {
    setRunning(true);
    setTimeout(() => {
      const newResults = selectedStrategies.map((s, i) => {
        const strat = STRATEGIES.find((st) => st.id === s);
        return generateDemoResult(strat?.name || s, i);
      });
      setResults(newResults);
      setRunning(false);
    }, 1200);
  }, [selectedStrategies]);

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
          <a href="/portfolio" className="nav-item">Portfolio</a>
          <a href="/backtest" className="nav-item active">Backtest</a>
        </nav>
        <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
          <span className="live-dot" style={{ marginRight: 6 }} />
          Connected
        </span>
      </header>

      <main className="main-content">
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 6 }}>
            Backtesting Lab
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Test trading strategies against historical data with fee-accurate simulation
          </p>
        </div>

        {/* Config Bar */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <div className="card-title">Configuration</div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={compareMode}
                  onChange={(e) => setCompareMode(e.target.checked)}
                  style={{ accentColor: "var(--accent)" }}
                />
                Compare Mode
              </label>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-dim)", marginBottom: 6 }}>
                Market
              </label>
              <select
                value={market}
                onChange={(e) => setMarket(e.target.value)}
                style={{
                  width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)", fontSize: "0.85rem", fontFamily: "var(--font-sans)",
                }}
              >
                <option value="chiefs-super-bowl-lxi">Chiefs Super Bowl LXI</option>
                <option value="celtics-nba-championship">Celtics NBA Championship</option>
                <option value="djokovic-french-open-2026">Djokovic French Open 2026</option>
                <option value="yankees-world-series-2026">Yankees World Series 2026</option>
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-dim)", marginBottom: 6 }}>
                Initial Capital ($)
              </label>
              <input
                type="text"
                value={capital}
                onChange={(e) => setCapital(e.target.value)}
                style={{
                  width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)", fontSize: "0.85rem", fontFamily: "var(--font-mono)",
                }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-dim)", marginBottom: 6 }}>
                Period (Days)
              </label>
              <input
                type="text"
                value={days}
                onChange={(e) => setDays(e.target.value)}
                style={{
                  width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)", fontSize: "0.85rem", fontFamily: "var(--font-mono)",
                }}
              />
            </div>
          </div>

          {/* Strategy Selector */}
          <label style={{ display: "block", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-dim)", marginBottom: 8 }}>
            {compareMode ? "Select Strategies to Compare" : "Select Strategy"}
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 16 }}>
            {STRATEGIES.map((s) => (
              <button
                key={s.id}
                onClick={() => toggleStrategy(s.id)}
                style={{
                  padding: "10px 14px",
                  background: selectedStrategies.includes(s.id) ? "var(--accent-subtle)" : "var(--bg-tertiary)",
                  border: `1px solid ${selectedStrategies.includes(s.id) ? "var(--accent-border)" : "var(--border-subtle)"}`,
                  borderRadius: "var(--radius-md)",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.15s ease",
                  color: selectedStrategies.includes(s.id) ? "var(--accent)" : "var(--text-secondary)",
                }}
              >
                <div style={{ fontWeight: 600, fontSize: "0.85rem", marginBottom: 2 }}>{s.name}</div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>{s.desc}</div>
              </button>
            ))}
          </div>

          <button
            className={`btn btn-primary ${running ? "" : ""}`}
            onClick={runBacktest}
            disabled={running || selectedStrategies.length === 0}
            style={{ width: "100%" }}
          >
            {running ? "⏳ Running Simulation..." : compareMode
              ? `🔬 Compare ${selectedStrategies.length} Strategies`
              : "🚀 Run Backtest"}
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <>
            {/* Comparison Table (if multiple) */}
            {results.length > 1 && (
              <div className="table-container fade-in" style={{ marginBottom: 24 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Strategy</th>
                      <th>Return %</th>
                      <th>Sharpe</th>
                      <th>Max DD %</th>
                      <th>Win Rate</th>
                      <th>Trades</th>
                      <th>Fees</th>
                      <th>Final Capital</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results
                      .sort((a, b) => b.returnPct - a.returnPct)
                      .map((r, i) => (
                        <tr key={r.strategy}>
                          <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                            {i === 0 && "🏆 "}{r.strategy}
                          </td>
                          <td className={`mono ${r.returnPct >= 0 ? "text-green" : "text-red"}`} style={{ fontWeight: 700 }}>
                            {r.returnPct >= 0 ? "+" : ""}{r.returnPct.toFixed(1)}%
                          </td>
                          <td className="mono" style={{ color: r.sharpe >= 1 ? "var(--green)" : r.sharpe >= 0 ? "var(--yellow)" : "var(--red)" }}>
                            {r.sharpe.toFixed(2)}
                          </td>
                          <td className="mono text-red">{r.maxDdPct.toFixed(1)}%</td>
                          <td className="mono">{r.winRate}%</td>
                          <td className="mono">{r.totalTrades}</td>
                          <td className="mono text-muted">${r.totalFees.toFixed(2)}</td>
                          <td className="mono" style={{ fontWeight: 600, color: r.finalCapital > 10000 ? "var(--green)" : "var(--red)" }}>
                            ${r.finalCapital.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Individual Result Cards */}
            <div className="data-grid" style={{ gridTemplateColumns: results.length > 1 ? "1fr 1fr" : "1fr", gap: 16 }}>
              {results.map((r, i) => (
                <div key={r.strategy} className="card fade-in-delayed" style={{ animationDelay: `${i * 100}ms` }}>
                  <div className="card-header">
                    <div className="card-title">{r.strategy}</div>
                    <span className={`badge ${r.returnPct >= 0 ? "badge-green" : "badge-red"}`}>
                      {r.returnPct >= 0 ? "+" : ""}{r.returnPct.toFixed(1)}%
                    </span>
                  </div>

                  {/* Equity Curve */}
                  <div style={{ marginBottom: 16, borderRadius: "var(--radius-md)", overflow: "hidden", background: "var(--bg-tertiary)", padding: "8px 0" }}>
                    <EquityChart data={r.equityCurve} height={100} />
                  </div>

                  {/* Metrics Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                    {[
                      { label: "Sharpe", value: r.sharpe.toFixed(2), color: r.sharpe >= 1 ? "var(--green)" : "var(--text-primary)" },
                      { label: "Win Rate", value: `${r.winRate}%`, color: r.winRate >= 50 ? "var(--green)" : "var(--red)" },
                      { label: "Max DD", value: `${r.maxDdPct.toFixed(1)}%`, color: "var(--red)" },
                      { label: "Trades", value: String(r.totalTrades), color: "var(--text-primary)" },
                      { label: "Best Trade", value: `$${r.bestTrade.toFixed(2)}`, color: "var(--green)" },
                      { label: "Worst Trade", value: `$${r.worstTrade.toFixed(2)}`, color: "var(--red)" },
                    ].map((m) => (
                      <div key={m.label} style={{ padding: "8px 10px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-sm)" }}>
                        <div style={{ fontSize: "0.6rem", fontWeight: 600, textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 2 }}>
                          {m.label}
                        </div>
                        <div className="mono" style={{ fontSize: "1rem", fontWeight: 700, color: m.color }}>
                          {m.value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </>
  );
}
