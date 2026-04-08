"use client";

import { useCallback, useEffect, useState } from "react";

/* ─── Types ─── */
interface Market {
  id: string;
  slug: string;
  question: string;
  market_type?: string;
  state?: string;
  best_bid?: number;
  best_ask?: number;
  mid_price?: number;
  spread?: number;
  volume_total?: number;
  // Polymarket US API fields (flexible)
  [key: string]: unknown;
}

interface Event {
  id: string;
  slug: string;
  title?: string;
  name?: string;
  start_time?: string;
  markets?: Market[];
  [key: string]: unknown;
}

/* ─── Constants ─── */
const SPORTS_FILTERS = [
  "All",
  "NFL",
  "NBA",
  "NHL",
  "MLB",
  "MLS",
  "CBB",
  "Tennis",
  "Golf",
] as const;

const PLATFORMS = ["Polymarket US", "Polymarket Intl", "Kalshi"] as const;

/* ─── Helpers ─── */
function formatPrice(price?: number): string {
  if (price === undefined || price === null) return "—";
  return `$${price.toFixed(2)}`;
}

function formatProbability(price?: number): string {
  if (price === undefined || price === null) return "—";
  return `${(price * 100).toFixed(0)}%`;
}

function formatVolume(vol?: number): string {
  if (!vol) return "$0";
  if (vol >= 1_000_000) return `$${(vol / 1_000_000).toFixed(1)}M`;
  if (vol >= 1_000) return `$${(vol / 1_000).toFixed(0)}K`;
  return `$${vol.toFixed(0)}`;
}

function probColor(p?: number): string {
  if (p === undefined || p === null) return "var(--text-muted)";
  if (p >= 0.7) return "var(--green)";
  if (p >= 0.4) return "var(--yellow)";
  return "var(--red)";
}

function probGradient(p: number): string {
  const pct = Math.max(0, Math.min(p * 100, 100));
  if (pct >= 70) return `linear-gradient(90deg, var(--green), #16a34a)`;
  if (pct >= 40) return `linear-gradient(90deg, var(--yellow), #d97706)`;
  return `linear-gradient(90deg, var(--red), #dc2626)`;
}

/* ─── Demo Data ─── */
function generateDemoData(): Market[] {
  const markets: Market[] = [
    {
      id: "1", slug: "chiefs-super-bowl-lxi",
      question: "Will the Chiefs win Super Bowl LXI?",
      market_type: "moneyline", state: "open",
      best_bid: 0.23, best_ask: 0.25, mid_price: 0.24, spread: 0.02, volume_total: 2_450_000,
    },
    {
      id: "2", slug: "celtics-nba-championship-2027",
      question: "Will the Celtics win the 2026-27 NBA Championship?",
      market_type: "moneyline", state: "open",
      best_bid: 0.31, best_ask: 0.33, mid_price: 0.32, spread: 0.02, volume_total: 1_870_000,
    },
    {
      id: "3", slug: "yankees-world-series-2026",
      question: "Will the Yankees win the 2026 World Series?",
      market_type: "moneyline", state: "open",
      best_bid: 0.17, best_ask: 0.19, mid_price: 0.18, spread: 0.02, volume_total: 980_000,
    },
    {
      id: "4", slug: "oilers-stanley-cup-2026",
      question: "Will the Oilers win the 2026 Stanley Cup?",
      market_type: "moneyline", state: "open",
      best_bid: 0.28, best_ask: 0.30, mid_price: 0.29, spread: 0.02, volume_total: 640_000,
    },
    {
      id: "5", slug: "djokovic-french-open-2026",
      question: "Will Djokovic win the 2026 French Open?",
      market_type: "moneyline", state: "open",
      best_bid: 0.41, best_ask: 0.43, mid_price: 0.42, spread: 0.02, volume_total: 410_000,
    },
    {
      id: "6", slug: "scheffler-masters-2027",
      question: "Will Scottie Scheffler win the 2027 Masters?",
      market_type: "moneyline", state: "open",
      best_bid: 0.14, best_ask: 0.16, mid_price: 0.15, spread: 0.02, volume_total: 320_000,
    },
    {
      id: "7",slug: "chiefs-spread-minus-3-5",
      question: "Chiefs -3.5 vs Bills — AFC Championship",
      market_type: "spread", state: "open",
      best_bid: 0.52, best_ask: 0.54, mid_price: 0.53, spread: 0.02, volume_total: 1_120_000,
    },
    {
      id: "8", slug: "nba-total-over-220-5",
      question: "Celtics vs Lakers — Total Points Over 220.5",
      market_type: "total", state: "open",
      best_bid: 0.47, best_ask: 0.50, mid_price: 0.485, spread: 0.03, volume_total: 780_000,
    },
    {
      id: "9", slug: "mahomes-over-2-5-tds",
      question: "Mahomes over 2.5 TDs — AFC Championship",
      market_type: "prop", state: "open",
      best_bid: 0.58, best_ask: 0.61, mid_price: 0.595, spread: 0.03, volume_total: 560_000,
    },
    {
      id: "10", slug: "inter-miami-mls-cup-2026",
      question: "Will Inter Miami win the 2026 MLS Cup?",
      market_type: "moneyline", state: "open",
      best_bid: 0.20, best_ask: 0.22, mid_price: 0.21, spread: 0.02, volume_total: 290_000,
    },
    {
      id: "11", slug: "uconn-march-madness-2027",
      question: "Will UConn win March Madness 2027?",
      market_type: "moneyline", state: "open",
      best_bid: 0.08, best_ask: 0.10, mid_price: 0.09, spread: 0.02, volume_total: 1_340_000,
    },
    {
      id: "12", slug: "panthers-over-7-5-wins",
      question: "Panthers Over 7.5 Wins — 2026-27 NFL Season",
      market_type: "total", state: "open",
      best_bid: 0.38, best_ask: 0.41, mid_price: 0.395, spread: 0.03, volume_total: 230_000,
    },
  ];
  return markets;
}

/* ─── Summary Stats ─── */
function SummaryStats({ markets }: { markets: Market[] }) {
  const totalVolume = markets.reduce((s, m) => s + (m.volume_total || 0), 0);
  const avgSpread =
    markets.reduce((s, m) => s + (m.spread || 0), 0) / (markets.length || 1);
  const openCount = markets.filter((m) => m.state === "open").length;

  return (
    <div className="data-grid cols-4" style={{ marginBottom: 24 }}>
      <div className="stat-box">
        <div className="stat-label">Active Markets</div>
        <div className="stat-value">{openCount}</div>
        <div className="stat-sub">across all sports</div>
      </div>
      <div className="stat-box">
        <div className="stat-label">Total Volume</div>
        <div className="stat-value">{formatVolume(totalVolume)}</div>
        <div className="stat-sub">combined trading volume</div>
      </div>
      <div className="stat-box">
        <div className="stat-label">Avg Spread</div>
        <div className="stat-value mono">{(avgSpread * 100).toFixed(1)}¢</div>
        <div className="stat-sub">bid-ask spread</div>
      </div>
      <div className="stat-box">
        <div className="stat-label">Platforms</div>
        <div className="stat-value">3</div>
        <div className="stat-sub">PM-US · PM-Intl · Kalshi</div>
      </div>
    </div>
  );
}

/* ─── Market Card ─── */
function MarketCard({ market }: { market: Market }) {
  const prob = market.mid_price || 0;
  const typeLabels: Record<string, string> = {
    moneyline: "MONEYLINE",
    spread: "SPREAD",
    total: "TOTAL",
    prop: "PROP",
  };

  return (
    <div className="market-card fade-in" id={`market-${market.slug}`}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
        <div className="market-card-question">{market.question}</div>
        <span className={`badge ${market.state === "open" ? "badge-green" : "badge-red"}`}>
          {market.state === "open" ? "LIVE" : market.state?.toUpperCase()}
        </span>
      </div>

      <div className="market-card-meta">
        {market.market_type && (
          <span className="badge badge-blue" style={{ fontSize: "0.65rem" }}>
            {typeLabels[market.market_type] || market.market_type.toUpperCase()}
          </span>
        )}
        <span className="market-card-meta-item">
          📊 {formatVolume(market.volume_total)}
        </span>
        <span className="market-card-meta-item mono">
          Spread: {((market.spread || 0) * 100).toFixed(1)}¢
        </span>
      </div>

      <div className="market-card-price-row">
        <div className="market-card-yes">
          <span className="market-card-yes-label">YES Price</span>
          <span className="market-card-yes-price" style={{ color: probColor(prob) }}>
            {formatProbability(prob)}
          </span>
        </div>

        <div style={{ flex: 1, margin: "0 20px" }}>
          <div className="prob-bar-container">
            <div
              className="prob-bar"
              style={{
                width: `${prob * 100}%`,
                background: probGradient(prob),
              }}
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-green btn-sm">Buy YES</button>
          <button className="btn btn-red btn-sm">Buy NO</button>
        </div>
      </div>

      {/* BBO detail */}
      <div
        style={{
          display: "flex",
          gap: 24,
          marginTop: 10,
          fontSize: "0.75rem",
          color: "var(--text-dim)",
          fontFamily: "var(--font-mono)",
        }}
      >
        <span>Bid: {formatPrice(market.best_bid)}</span>
        <span>Ask: {formatPrice(market.best_ask)}</span>
        <span>Mid: {formatPrice(market.mid_price)}</span>
      </div>
    </div>
  );
}

/* ─── Main Page ─── */
export default function Home() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [activePlatform, setActivePlatform] = useState("Polymarket US");
  const [activeView, setActiveView] = useState<"Markets" | "Trading" | "Arbitrage" | "Sentiment" | "Portfolio">("Markets");
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<"volume" | "price" | "spread">("volume");

  useEffect(() => {
    // Load demo data (will be replaced with API calls)
    const timer = setTimeout(() => {
      setMarkets(generateDemoData());
      setLoading(false);
    }, 600);
    return () => clearTimeout(timer);
  }, []);

  const filteredMarkets = markets
    .filter((m) => {
      if (searchQuery) {
        return m.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
          m.slug.toLowerCase().includes(searchQuery.toLowerCase());
      }
      return true;
    })
    .filter((m) => {
      if (activeFilter === "All") return true;
      // Simple sport detection from question text
      const q = m.question.toLowerCase();
      const sportMap: Record<string, string[]> = {
        NFL: ["chiefs", "eagles", "bills", "panthers", "nfl", "super bowl", "afc", "nfc", "mahomes"],
        NBA: ["celtics", "lakers", "nba", "basketball"],
        NHL: ["oilers", "stanley cup", "nhl", "hockey"],
        MLB: ["yankees", "world series", "mlb", "baseball"],
        MLS: ["miami", "mls", "soccer"],
        CBB: ["uconn", "march madness", "ncaa", "cbb"],
        Tennis: ["djokovic", "french open", "wimbledon", "tennis"],
        Golf: ["scheffler", "masters", "pga", "golf"],
      };
      const keywords = sportMap[activeFilter] || [];
      return keywords.some((kw) => q.includes(kw));
    })
    .sort((a, b) => {
      if (sortBy === "volume") return (b.volume_total || 0) - (a.volume_total || 0);
      if (sortBy === "price") return (b.mid_price || 0) - (a.mid_price || 0);
      return (a.spread || 0) - (b.spread || 0);
    });

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">P</div>
          Polymarket Platform
          <span className="live-dot" style={{ marginLeft: 4 }} />
        </div>

        <nav className="nav">
          {(["Markets", "Trading", "Arbitrage", "Sentiment", "Portfolio"] as const).map((view) => (
            <button
              key={view}
              className={`nav-item ${activeView === view ? "active" : ""}`}
              onClick={() => setActiveView(view)}
              id={`nav-${view.toLowerCase()}`}
            >
              {view}
            </button>
          ))}
        </nav>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
            <span className="live-dot" style={{ marginRight: 6 }} />
            Connected
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Page Title */}
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 6 }}>
            Market Explorer
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Real-time prediction markets across Polymarket US, Polymarket International, and Kalshi
          </p>
        </div>

        {/* Summary Stats */}
        <SummaryStats markets={filteredMarkets} />

        {/* Platform Tabs */}
        <div className="filters-bar">
          {PLATFORMS.map((p) => (
            <button
              key={p}
              className={`filter-chip ${activePlatform === p ? "active" : ""}`}
              onClick={() => setActivePlatform(p)}
              id={`platform-${p.toLowerCase().replace(/\s/g, "-")}`}
            >
              {p}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          {/* Search */}
          <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search markets, events, teams..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              id="search-input"
            />
          </div>
        </div>

        {/* Sport Filters */}
        <div className="filters-bar">
          {SPORTS_FILTERS.map((sport) => (
            <button
              key={sport}
              className={`filter-chip ${activeFilter === sport ? "active" : ""}`}
              onClick={() => setActiveFilter(sport)}
              id={`filter-${sport.toLowerCase()}`}
            >
              {sport}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          {/* Sort */}
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>Sort:</span>
            {(["volume", "price", "spread"] as const).map((s) => (
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
        </div>

        {/* Market Cards Grid */}
        {loading ? (
          <div className="data-grid cols-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="market-card">
                <div className="skeleton" style={{ height: 20, width: "80%", marginBottom: 12 }} />
                <div className="skeleton" style={{ height: 14, width: "40%", marginBottom: 16 }} />
                <div className="skeleton" style={{ height: 32, width: "30%" }} />
              </div>
            ))}
          </div>
        ) : filteredMarkets.length === 0 ? (
          <div style={{
            textAlign: "center",
            padding: 60,
            color: "var(--text-muted)",
          }}>
            <div style={{ fontSize: "2rem", marginBottom: 8 }}>🔍</div>
            <div style={{ fontSize: "1rem", fontWeight: 500 }}>No markets found</div>
            <div style={{ fontSize: "0.85rem", marginTop: 4 }}>
              Try adjusting your search or filters
            </div>
          </div>
        ) : (
          <div className="data-grid cols-2">
            {filteredMarkets.map((market, i) => (
              <div
                key={market.id}
                className="fade-in-delayed"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <MarketCard market={market} />
              </div>
            ))}
          </div>
        )}

        {/* Footer Stats */}
        <div
          style={{
            marginTop: 32,
            padding: "16px 0",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "0.75rem",
            color: "var(--text-dim)",
          }}
        >
          <span>
            Showing {filteredMarkets.length} of {markets.length} markets
          </span>
          <span className="mono">
            Polymarket Platform v0.1.0 • PM-US • PM-Intl • Kalshi
          </span>
        </div>
      </main>
    </>
  );
}
