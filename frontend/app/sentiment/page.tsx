"use client";

import { useState } from "react";

/* ─── Types ─── */
interface SentimentData {
  slug: string;
  question: string;
  sentimentScore: number; // -1 to +1
  mentionVolume: number;
  priceSentimentDivergence: number;
  narrativeTrend: "bullish" | "bearish" | "neutral";
  confidence: number;
  topInfluencer: string;
  priceYes: number;
  priceChange24h: number;
  sources: { name: string; score: number; volume: number }[];
}

/* ─── Demo Data ─── */
const demoSentiment: SentimentData[] = [
  {
    slug: "chiefs-super-bowl-lxi", question: "Will the Chiefs win Super Bowl LXI?",
    sentimentScore: 0.72, mentionVolume: 12400, priceSentimentDivergence: 0.15,
    narrativeTrend: "bullish", confidence: 0.85, topInfluencer: "@AdamSchefter",
    priceYes: 0.24, priceChange24h: 2.3,
    sources: [
      { name: "Twitter/X", score: 0.78, volume: 8200 },
      { name: "Reddit", score: 0.64, volume: 2800 },
      { name: "News", score: 0.71, volume: 1400 },
    ],
  },
  {
    slug: "celtics-nba-championship",
    question: "Will the Celtics win the 2026-27 NBA Championship?",
    sentimentScore: -0.18, mentionVolume: 8700, priceSentimentDivergence: -0.32,
    narrativeTrend: "bearish", confidence: 0.71, topInfluencer: "@wojespn",
    priceYes: 0.32, priceChange24h: -1.8,
    sources: [
      { name: "Twitter/X", score: -0.22, volume: 5100 },
      { name: "Reddit", score: -0.14, volume: 2400 },
      { name: "News", score: -0.12, volume: 1200 },
    ],
  },
  {
    slug: "djokovic-french-open-2026",
    question: "Will Djokovic win the 2026 French Open?",
    sentimentScore: 0.55, mentionVolume: 4200, priceSentimentDivergence: 0.08,
    narrativeTrend: "bullish", confidence: 0.62, topInfluencer: "@BenRothenberg",
    priceYes: 0.42, priceChange24h: 0.5,
    sources: [
      { name: "Twitter/X", score: 0.61, volume: 2400 },
      { name: "Reddit", score: 0.48, volume: 1100 },
      { name: "News", score: 0.52, volume: 700 },
    ],
  },
  {
    slug: "mahomes-over-2-5-tds",
    question: "Mahomes over 2.5 TDs — AFC Championship",
    sentimentScore: 0.41, mentionVolume: 6100, priceSentimentDivergence: -0.05,
    narrativeTrend: "neutral", confidence: 0.58, topInfluencer: "@PFF",
    priceYes: 0.595, priceChange24h: 1.1,
    sources: [
      { name: "Twitter/X", score: 0.45, volume: 3800 },
      { name: "Reddit", score: 0.38, volume: 1500 },
      { name: "News", score: 0.35, volume: 800 },
    ],
  },
  {
    slug: "yankees-world-series-2026",
    question: "Will the Yankees win the 2026 World Series?",
    sentimentScore: 0.82, mentionVolume: 9300, priceSentimentDivergence: 0.45,
    narrativeTrend: "bullish", confidence: 0.91, topInfluencer: "@JeffPassan",
    priceYes: 0.18, priceChange24h: 4.2,
    sources: [
      { name: "Twitter/X", score: 0.88, volume: 6100 },
      { name: "Reddit", score: 0.76, volume: 2100 },
      { name: "News", score: 0.79, volume: 1100 },
    ],
  },
];

/* ─── Helpers ─── */
function sentimentColor(score: number): string {
  if (score > 0.3) return "var(--green)";
  if (score < -0.3) return "var(--red)";
  return "var(--yellow)";
}

function trendIcon(trend: string): string {
  if (trend === "bullish") return "📈";
  if (trend === "bearish") return "📉";
  return "➡️";
}

function divergenceSignal(div: number): { label: string; color: string; badge: string } {
  if (div > 0.2)
    return { label: "STRONG BUY SIGNAL", color: "var(--green)", badge: "badge-green" };
  if (div > 0.1)
    return { label: "MILD BUY SIGNAL", color: "var(--green)", badge: "badge-green" };
  if (div < -0.2)
    return { label: "STRONG SELL SIGNAL", color: "var(--red)", badge: "badge-red" };
  if (div < -0.1)
    return { label: "MILD SELL SIGNAL", color: "var(--red)", badge: "badge-red" };
  return { label: "NEUTRAL", color: "var(--text-muted)", badge: "badge-yellow" };
}

/* ─── Page ─── */
export default function SentimentPage() {
  const [window, setWindow] = useState<"1h" | "6h" | "24h" | "7d">("24h");
  const [sortBy, setSortBy] = useState<"divergence" | "sentiment" | "volume">("divergence");

  const sorted = [...demoSentiment].sort((a, b) => {
    if (sortBy === "divergence") return Math.abs(b.priceSentimentDivergence) - Math.abs(a.priceSentimentDivergence);
    if (sortBy === "sentiment") return Math.abs(b.sentimentScore) - Math.abs(a.sentimentScore);
    return b.mentionVolume - a.mentionVolume;
  });

  const avgSentiment = demoSentiment.reduce((s, d) => s + d.sentimentScore, 0) / demoSentiment.length;
  const strongSignals = demoSentiment.filter((d) => Math.abs(d.priceSentimentDivergence) > 0.2).length;

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
          <a href="/sentiment" className="nav-item active">Sentiment</a>
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
            Sentiment Intelligence
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Falcon-powered sentiment analysis, price-sentiment divergence signals, and social mention tracking
          </p>
        </div>

        {/* Summary Stats */}
        <div className="data-grid cols-4" style={{ marginBottom: 24 }}>
          <div className="stat-box">
            <div className="stat-label">Avg Sentiment</div>
            <div className="stat-value" style={{ color: sentimentColor(avgSentiment) }}>
              {avgSentiment > 0 ? "+" : ""}{avgSentiment.toFixed(2)}
            </div>
            <div className="stat-sub">{avgSentiment > 0 ? "bullish overall" : "mixed"}</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Markets Tracked</div>
            <div className="stat-value">{demoSentiment.length}</div>
            <div className="stat-sub">with active mentions</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Strong Divergence Signals</div>
            <div className="stat-value text-accent">{strongSignals}</div>
            <div className="stat-sub">price vs. sentiment mismatch &gt;20%</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Total Mentions</div>
            <div className="stat-value mono">
              {(demoSentiment.reduce((s, d) => s + d.mentionVolume, 0) / 1000).toFixed(1)}K
            </div>
            <div className="stat-sub">across Twitter, Reddit, News</div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-bar">
          <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginRight: 4 }}>Window:</span>
          {(["1h", "6h", "24h", "7d"] as const).map((w) => (
            <button
              key={w}
              className={`filter-chip ${window === w ? "active" : ""}`}
              onClick={() => setWindow(w)}
            >
              {w}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginRight: 4 }}>Sort:</span>
          {(["divergence", "sentiment", "volume"] as const).map((s) => (
            <button
              key={s}
              className={`filter-chip ${sortBy === s ? "active" : ""}`}
              onClick={() => setSortBy(s)}
              style={{ textTransform: "capitalize" }}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Sentiment Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {sorted.map((data, i) => {
            const signal = divergenceSignal(data.priceSentimentDivergence);
            return (
              <div
                key={data.slug}
                className="card fade-in-delayed"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                  <div>
                    <div style={{ fontSize: "1rem", fontWeight: 600, marginBottom: 4 }}>
                      {data.question}
                    </div>
                    <div style={{ display: "flex", gap: 12, alignItems: "center", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      <span>YES: <span className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>${data.priceYes.toFixed(2)}</span></span>
                      <span className={`price-change ${data.priceChange24h >= 0 ? "up" : "down"}`}>
                        {data.priceChange24h >= 0 ? "▲" : "▼"} {Math.abs(data.priceChange24h).toFixed(1)}%
                      </span>
                      <span>📊 {(data.mentionVolume / 1000).toFixed(1)}K mentions</span>
                      <span>Top: {data.topInfluencer}</span>
                    </div>
                  </div>
                  <span className={`badge ${signal.badge}`}>{signal.label}</span>
                </div>

                {/* Metrics Row */}
                <div className="data-grid cols-4" style={{ marginBottom: 16 }}>
                  <div style={{ padding: "10px 14px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)" }}>
                    <div style={{ fontSize: "0.65rem", fontWeight: 600, textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 4 }}>
                      Sentiment Score
                    </div>
                    <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: sentimentColor(data.sentimentScore) }}>
                      {data.sentimentScore > 0 ? "+" : ""}{data.sentimentScore.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ padding: "10px 14px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)" }}>
                    <div style={{ fontSize: "0.65rem", fontWeight: 600, textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 4 }}>
                      Price-Sentiment Divergence
                    </div>
                    <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: signal.color }}>
                      {data.priceSentimentDivergence > 0 ? "+" : ""}{(data.priceSentimentDivergence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div style={{ padding: "10px 14px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)" }}>
                    <div style={{ fontSize: "0.65rem", fontWeight: 600, textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 4 }}>
                      Narrative
                    </div>
                    <div style={{ fontSize: "1.2rem", fontWeight: 700 }}>
                      {trendIcon(data.narrativeTrend)} {data.narrativeTrend.charAt(0).toUpperCase() + data.narrativeTrend.slice(1)}
                    </div>
                  </div>
                  <div style={{ padding: "10px 14px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)" }}>
                    <div style={{ fontSize: "0.65rem", fontWeight: 600, textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 4 }}>
                      Confidence
                    </div>
                    <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700 }}>
                      {(data.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Source Breakdown */}
                <div style={{ display: "flex", gap: 12 }}>
                  {data.sources.map((src) => (
                    <div
                      key={src.name}
                      style={{
                        flex: 1,
                        padding: "8px 12px",
                        background: "var(--bg-secondary)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "0.75rem",
                      }}
                    >
                      <div style={{ fontWeight: 600, marginBottom: 4 }}>{src.name}</div>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ color: sentimentColor(src.score) }} className="mono">
                          {src.score > 0 ? "+" : ""}{src.score.toFixed(2)}
                        </span>
                        <span className="text-muted">{(src.volume / 1000).toFixed(1)}K</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </>
  );
}
