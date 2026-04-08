"use client";

import { useEffect, useState } from "react";

const SECTIONS = [
  { id: "intro", title: "1. Understanding Prediction Markets" },
  { id: "platform", title: "2. Platform Architecture" },
  { id: "trading", title: "3. Advanced Trading Concepts" },
  { id: "fees-margins", title: "4. Fees & Portfolio Margin" },
  { id: "capital", title: "5. Sizing & Capital Efficiency" },
  { id: "arbitrage", title: "6. Arbitrage Strategies" },
  { id: "ai-sentiment", title: "7. AI & Sentiment Intelligence" },
  { id: "backtesting", title: "8. Algorithmic Backtesting" },
];

export default function LearnPage() {
  const [activeSection, setActiveSection] = useState("intro");

  // Intersection Observer for scroll spy
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: "-20% 0px -70% 0px" } // Adjust trigger area
    );

    SECTIONS.forEach((section) => {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => setActiveSection(id), 500); // UI update sync
    }
  };

  return (
    <>
      <header className="header" style={{ position: "sticky", top: 0, zIndex: 100 }}>
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
          <a href="/backtest" className="nav-item">Backtest</a>
          <a href="/learn" className="nav-item active">Learn</a>
        </nav>
      </header>

      <div style={{ display: "flex", width: "100%", maxWidth: "1400px", margin: "0 auto" }}>
        
        {/* Sticky Sidebar */}
        <aside style={{
          width: "300px",
          position: "sticky",
          top: "64px",
          height: "calc(100vh - 64px)",
          padding: "32px 24px",
          borderRight: "1px solid var(--border-subtle)",
          overflowY: "auto"
        }}>
          <h2 style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-dim)", marginBottom: "20px", fontWeight: 700 }}>
            Documentation
          </h2>
          <nav style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {SECTIONS.map((section) => (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                style={{
                  textAlign: "left",
                  padding: "10px 12px",
                  borderRadius: "var(--radius-sm)",
                  background: activeSection === section.id ? "var(--bg-tertiary)" : "transparent",
                  color: activeSection === section.id ? "var(--text-primary)" : "var(--text-secondary)",
                  fontWeight: activeSection === section.id ? 600 : 400,
                  fontSize: "0.9rem",
                  border: "none",
                  cursor: "pointer",
                  transition: "all var(--transition-fast)",
                }}
              >
                {section.title}
              </button>
            ))}
          </nav>
        </aside>

        {/* Scrollable Content */}
        <main style={{ flex: 1, padding: "48px 64px", overflowY: "auto" }}>
          
          <div style={{ maxWidth: "800px", margin: "0 auto" }}>
            
            <h1 style={{ fontSize: "3rem", fontWeight: 800, marginBottom: "16px", letterSpacing: "-0.03em" }}>
              Trading & Platform Guide
            </h1>
            <p style={{ fontSize: "1.2rem", color: "var(--text-muted)", marginBottom: "64px", lineHeight: 1.6 }}>
              A comprehensive educational resource explaining prediction markets, platform mechanics, algorithms, and AI-driven trading strategies within our unified infrastructure.
            </p>

            {/* SECTION 1 */}
            <section id="intro" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 1</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Understanding Prediction Markets</h2>
              
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                At their core, prediction markets are financial markets where the traded assets are shares representing the outcome of future events. Unlike stocks, which represent ownership in a company, prediction market shares are binary contracts.
              </p>

              <div className="card" style={{ padding: "24px", marginBottom: "24px", borderLeft: "4px solid var(--accent)" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "12px" }}>The Core Mechanism: The $1.00 Peg</h3>
                <p style={{ color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 0 }}>
                  Every market resolves to a known outcome. If an event occurs, <strong>YES</strong> shares resolve at $1.00 and <strong>NO</strong> shares resolve at $0.00. 
                  <br/><br/>
                  If the current price of YES is $0.65, this means the market assigns a <strong>65% probability</strong> to the event occurring. If you buy at $0.65 and it happens, you profit $0.35 per share.
                </p>
              </div>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginTop: "32px", marginBottom: "16px" }}>Why Trade Them?</h3>
              <ul style={{ color: "var(--text-secondary)", lineHeight: 1.7, paddingLeft: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
                <li><strong>Information Aggregation:</strong> Markets are highly efficient at synthesizing disparate information into a single statistical truth.</li>
                <li><strong>Uncorrelated Returns:</strong> A bet on who wins the Super Bowl is uncorrelated to the S&P 500, offering excellent portfolio diversification.</li>
                <li><strong>Hedge Real-World Risks:</strong> Businesses and individuals can hedge against political outcomes, economic metrics (like CPI prints), or supply chain disruptions.</li>
              </ul>
            </section>

            {/* SECTION 2 */}
            <section id="platform" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 2</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Platform Architecture</h2>
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                This platform is an aggregator and execution engine built on top of three major prediction market venues. We normalise data across these venues to provide a unified trading experience.
              </p>

              <div className="data-grid cols-3" style={{ marginBottom: "32px" }}>
                <div className="card" style={{ padding: "20px" }}>
                  <h4 style={{ color: "var(--accent)", marginBottom: "8px", fontWeight: 700 }}>1. Polymarket US</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    The primary U.S. facing entity, utilizing fiat settlement and complying with CFTC regulations. Focuses heavily on high-liquidity macro, political, and sports events.
                  </p>
                </div>
                <div className="card" style={{ padding: "20px" }}>
                  <h4 style={{ color: "var(--purple)", marginBottom: "8px", fontWeight: 700 }}>2. Polymarket Intl</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    The global, crypto-native platform operating via the Gamma API and an off-chain CLOB (Central Limit Order Book). Settles in USDC on Polygon.
                  </p>
                </div>
                <div className="card" style={{ padding: "20px" }}>
                  <h4 style={{ color: "var(--green)", marginBottom: "8px", fontWeight: 700 }}>3. Kalshi</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    A fully CFTC-regulated U.S. exchange. Offers unique financial and economic markets. We integrate Kalshi primarily to surface cross-venue arbitrage opportunities.
                  </p>
                </div>
              </div>

              <div style={{ padding: "24px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-lg)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontWeight: 600, marginBottom: "16px" }}>The Unified Core</h4>
                <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 0 }}>
                  Under the hood, a high-performance Python/FastAPI backend manages Ed25519 cryptography for Polymarket connections and RSA-PSS signatures for Kalshi. The <strong>WebSocket Manager</strong> sustains private, live-updating streams to ensure your risk system and order book depth are never stale.
                </p>
              </div>
            </section>

            {/* SECTION 3 */}
            <section id="trading" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 3</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Advanced Trading Concepts</h2>
              
              <div style={{ display: "flex", gap: "32px", marginBottom: "24px" }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "12px" }}>Central Limit Order Book (CLOB)</h3>
                  <p style={{ fontSize: "1rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                    Instead of trading against a liquidity pool (AMM), you trade against other users on an order book. Our trading terminal visually displays <em>depth bars</em> behind open orders, allowing you to gauge where heavy resistance and support lie.
                  </p>
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "12px" }}>The Bid-Ask Spread</h3>
                  <p style={{ fontSize: "1rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                    The difference between the highest price a buyer is willing to pay (Bid) and the lowest price a seller will accept (Ask). Tight spreads (e.g. 0.01¢) indicate a highly liquid market.
                  </p>
                </div>
              </div>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px", marginTop: "32px" }}>Order Types & Execution</h3>
              <ul style={{ color: "var(--text-secondary)", lineHeight: 1.7, paddingLeft: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
                <li><strong>Limit Orders:</strong> You specify the exact price. It rests on the order book until filled. Excellent for capturing maker fees/rebates.</li>
                <li><strong>Market Orders:</strong> Executes immediately at the best available prices. You cross the spread and pay <em>Taker Fees</em>. Risk of <em>Slippage</em> if liquidity is thin.</li>
                <li><strong>Time in Force (TIF):</strong> GTC (Good Til Cancelled), IOC (Immediate or Cancel — kills remainder), FOK (Fill or Kill — full size or nothing).</li>
              </ul>
            </section>

            {/* SECTION 4 */}
            <section id="fees-margins" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 4</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Fees & Portfolio Margin</h2>

              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Profitability in predictions requires obsessing over fee drag and capital efficiency.
              </p>

              <div className="card" style={{ padding: "24px", marginBottom: "32px" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "12px" }}>The Symmetric Fee Formula</h3>
                <p style={{ color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: "16px" }}>
                  Polymarket applies fees symmetrically to discourage wash trading around extreme probabilities. The fee is maximized at 50/50 odds and tapers off near 1% and 99%. Our platform calculates this in real-time on your order ticket.
                </p>
                <code style={{ display: "block", background: "var(--bg-primary)", padding: "16px", borderRadius: "var(--radius-sm)", fontFamily: "var(--font-mono)", fontSize: "0.9rem", color: "var(--green)" }}>
                  Fee = Taker_Rate × Quantity × Price × (1 - Price)
                </code>
              </div>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px" }}>Mutually Exclusive (ME) Margin Offsets</h3>
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                If you buy YES on the "Chiefs" winning the Super Bowl, and YES on the "49ers", it is impossible for both positions to lose. The system recognizes <strong>Mutually Exclusive</strong> groups and applies collateral return offsets.
              </p>
              
              <div style={{ background: "var(--bg-tertiary)", borderLeft: "4px solid var(--accent)", padding: "16px 24px", borderRadius: "var(--radius-md)", color: "var(--text-secondary)", fontSize: "0.95rem" }}>
                <strong>Example:</strong> Buying $100 of Chiefs and $100 of 49ers would normally cost $200. Because they are mutually exclusive, if Chiefs lose, your 49ers bet might win. The exact offset depends on the math, but our <strong>Margin Calculator</strong> dynamically frees up buying power rather than keeping it locked, supercharging capital efficiency.
              </div>
            </section>

            {/* SECTION 5 */}
            <section id="capital" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 5</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Sizing & Capital Efficiency</h2>

              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Finding an edge is only half the battle; the other half is knowing how much to bet. The platform relies on quantitative principles to optimize trade sizing.
              </p>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px" }}>Expected Value (EV)</h3>
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                A bet is only worth taking if the expected value is positive. 
                <br />
                <code>EV = (Prob_Win × Payout) - (Prob_Loss × Stake)</code>
                <br />
                Our AI agents constantly calculate the EV of the order book against Falcon's fair-value estimates.
              </p>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px" }}>The Kelly Criterion</h3>
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                The Kelly Criterion is a formula used to determine the optimal size of a series of bets to maximize long-term wealth growth, while avoiding ruin.
              </p>
              
              <div style={{ display: "flex", alignItems: "center", gap: "24px", background: "var(--bg-tertiary)", padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border-default)" }}>
                <div style={{ fontSize: "1.8rem" }}>🧮</div>
                <div>
                  <h4 style={{ fontWeight: 600, marginBottom: "8px", fontSize: "1.1rem" }}>f* = (bp - q) / b</h4>
                  <ul style={{ color: "var(--text-muted)", fontSize: "0.9rem", paddingLeft: "16px", lineHeight: 1.5, margin: 0 }}>
                    <li><strong>f*</strong> = fraction of bankroll to wager</li>
                    <li><strong>b</strong> = decimal odds - 1 (the profit multiplier)</li>
                    <li><strong>p</strong> = probability of winning</li>
                    <li><strong>q</strong> = probability of losing (1-p)</li>
                  </ul>
                </div>
              </div>
              <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", marginTop: "16px" }}>
                <em>Note: Our AI Agent relies on a "Fractional" or "Quarter-Kelly" approach, dividing the Kelly suggestion by 4. This heavily protects against estimation errors and volatility constraints.</em>
              </p>
            </section>

            {/* SECTION 6 */}
            <section id="arbitrage" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 6</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Arbitrage Strategies</h2>
              
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Arbitrage implies a risk-free profit. Our platform contains an Arbitrage Engine scanning across two primary vectors.
              </p>

              <div className="card" style={{ padding: "24px", marginBottom: "24px" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "12px", color: "var(--green)" }}>1. Cross-Venue Arbitrage</h3>
                <p style={{ color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 0 }}>
                  The same event is listed on both Polymarket and Kalshi. <br/>
                  If Polymarket prices a YES at 40¢, and Kalshi prices a NO at 45¢, you can buy both for 85¢ total. Since the event must resolve definitively, one side is guaranteed to pay out 100¢. <br/>
                  <strong>Guaranteed Profit = 100¢ - 85¢ - Fees.</strong> <br/>
                  Our Arbitrage scanner automatically checks the <em>Net Gap</em> to ensure it is actionable after deducting both platforms' taker fees.
                </p>
              </div>

              <div className="card" style={{ padding: "24px" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "12px", color: "var(--purple)" }}>2. Complete-Set Arbitrage</h3>
                <p style={{ color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 0 }}>
                  In a tournament or mutually exclusive group (e.g., "Who will win the NBA Championship?"), exactly one team MUST win. <br/>
                  If you buy YES on <em>every single team</em> in the field, and the total cost is less than $1.00 (e.g., $0.95), you have mathematically secured a 5¢ profit. This frequently occurs during high-volume volatility.
                </p>
              </div>

            </section>

            {/* SECTION 7 */}
            <section id="ai-sentiment" style={{ marginBottom: "80px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 7</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>AI & Sentiment Intelligence</h2>

              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Prediction markets operate heavily on news cycles. The system integrates closely with the <strong>Falcon AI APIs</strong> and Claude via <strong>MCP (Model Context Protocol)</strong>.
              </p>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px" }}>Falcon Sentiment Divergence</h3>
              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Falcon ingests real-time data from Twitter/X, News, and Reddit to produce a structured sentiment score [-1.0 to 1.0]. The platform graphs this against the actual order book price to find <strong>Divergences</strong>. <br/><br/>
                If social sentiment is highly bullish (+0.8), but the asset is dropping in price on Polymarket, the algorithm flags a <em>Strong Buy Divergence</em>.
              </p>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "16px" }}>The Automated Agent Workflow</h3>
              <ol style={{ color: "var(--text-secondary)", lineHeight: 1.7, paddingLeft: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
                <li><strong>Research:</strong> The Agent requests market depth, past price momentum, and Falcon sentiment.</li>
                <li><strong>Fair Value Generation:</strong> Fuses these inputs (e.g. 40% Tape, 30% Sentiment, 20% Momentum, 10% Arb checks) to compute a "Fair Value".</li>
                <li><strong>Trade Suggestion:</strong> Checks Fair Value against current Ask price. If Kelly &gt; 0, it produces a ranked trade rationale.</li>
                <li><strong>Execution:</strong> In "Auto" mode, it passes the pre-trade <code>RiskManager</code> checks (position limits, liquidations, daily loss barriers) and executes.</li>
              </ol>
            </section>

            {/* SECTION 8 */}
            <section id="backtesting" style={{ paddingBottom: "120px", scrollMarginTop: "100px" }}>
              <div style={{ color: "var(--accent)", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", marginBottom: "8px", textTransform: "uppercase" }}>Chapter 8</div>
              <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "24px" }}>Algorithmic Backtesting</h2>

              <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                Never deploy capital to a theory that hasn't been stress tested. The built-in Backtesting Lab processes historical tick data to simulate algorithm performance using the matching engine's actual fee structures and slippage models.
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "32px" }}>
                <div style={{ padding: "20px", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)" }}>
                  <div style={{ fontSize: "1.8rem", marginBottom: "8px" }}>📈</div>
                  <h4 style={{ fontWeight: 600, marginBottom: "8px" }}>Momentum Strategy</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
                    Tracks moving averages over rolling windows. Enters trades on positive breakouts to ride market overreactions, exiting before normalization.
                  </p>
                </div>
                <div style={{ padding: "20px", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)" }}>
                  <div style={{ fontSize: "1.8rem", marginBottom: "8px" }}>📉</div>
                  <h4 style={{ fontWeight: 600, marginBottom: "8px" }}>Mean Reversion</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
                    Uses Z-Scores indicating an asset has strayed too far from its historical moving average. Bets against the trend expecting a snap-back.
                  </p>
                </div>
              </div>

              <div style={{ background: "var(--bg-tertiary)", padding: "24px", borderRadius: "var(--radius-lg)" }}>
                <h4 style={{ fontWeight: 600, marginBottom: "12px", color: "var(--text-primary)" }}>Simulation Integrity</h4>
                <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                  Backtests simulate real-world illiquidity via a configurable <strong>Slippage BPS</strong> parameter, ensuring that testing against hypothetical historical mid-prices doesn't result in false positives. Expected performance metrics include Sharpe Ratios, Maximum Drawdown (exposing risk of ruin), and Hit Rate percentages.
                </p>
              </div>

            </section>

          </div>
        </main>
      </div>
    </>
  );
}
