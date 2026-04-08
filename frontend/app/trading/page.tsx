"use client";

import { useCallback, useEffect, useState } from "react";
import styles from "./trading.module.css";

/* ─── Types ─── */
interface OrderBookLevel {
  price: number;
  size: number;
  total: number;
}

interface Position {
  slug: string;
  side: "long" | "short";
  quantity: number;
  avgEntry: number;
  currentPrice: number;
  pnl: number;
  pnlPct: number;
}

interface Order {
  id: string;
  slug: string;
  side: "buy" | "sell";
  type: "limit" | "market";
  price: number;
  quantity: number;
  filled: number;
  status: string;
  createdAt: string;
}

interface RiskStatus {
  circuitBreakerTriggered: boolean;
  dailyPnl: number;
  maxDailyLoss: number;
}

/* ─── Demo Data ─── */
function generateOrderBook(): { bids: OrderBookLevel[]; asks: OrderBookLevel[] } {
  const bids: OrderBookLevel[] = [];
  const asks: OrderBookLevel[] = [];
  let bidTotal = 0;
  let askTotal = 0;

  for (let i = 0; i < 10; i++) {
    const bidSize = Math.floor(Math.random() * 500) + 50;
    const askSize = Math.floor(Math.random() * 500) + 50;
    bidTotal += bidSize;
    askTotal += askSize;

    bids.push({
      price: 0.55 - i * 0.01,
      size: bidSize,
      total: bidTotal,
    });
    asks.push({
      price: 0.56 + i * 0.01,
      size: askSize,
      total: askTotal,
    });
  }
  return { bids, asks };
}

function generatePositions(): Position[] {
  return [
    { slug: "chiefs-super-bowl-lxi", side: "long", quantity: 200, avgEntry: 0.22, currentPrice: 0.24, pnl: 4.0, pnlPct: 9.09 },
    { slug: "celtics-nba-championship", side: "long", quantity: 150, avgEntry: 0.35, currentPrice: 0.32, pnl: -4.5, pnlPct: -8.57 },
    { slug: "mahomes-over-2-5-tds", side: "long", quantity: 100, avgEntry: 0.55, currentPrice: 0.595, pnl: 4.5, pnlPct: 8.18 },
    { slug: "djokovic-french-open", side: "short", quantity: 75, avgEntry: 0.60, currentPrice: 0.42, pnl: 13.5, pnlPct: 30.0 },
  ];
}

function generateOrders(): Order[] {
  return [
    { id: "ord_1", slug: "chiefs-super-bowl-lxi", side: "buy", type: "limit", price: 0.21, quantity: 100, filled: 0, status: "open", createdAt: "2026-04-07T10:30:00Z" },
    { id: "ord_2", slug: "celtics-nba-championship", side: "sell", type: "limit", price: 0.38, quantity: 50, filled: 0, status: "open", createdAt: "2026-04-07T11:15:00Z" },
    { id: "ord_3", slug: "mahomes-over-2-5-tds", side: "buy", type: "limit", price: 0.57, quantity: 75, filled: 30, status: "partially_filled", createdAt: "2026-04-07T12:00:00Z" },
  ];
}

/* ─── Subcomponents ─── */

function OrderBookPanel({ bids, asks }: { bids: OrderBookLevel[]; asks: OrderBookLevel[] }) {
  const maxTotal = Math.max(
    bids[bids.length - 1]?.total || 0,
    asks[asks.length - 1]?.total || 0
  );

  return (
    <div className={styles.orderBook}>
      <div className={styles.panelHeader}>
        <h3>Order Book</h3>
        <span className="live-dot" />
      </div>
      <div className={styles.bookHeader}>
        <span>Price</span>
        <span>Size</span>
        <span>Total</span>
      </div>
      {/* Asks (reversed — best ask at bottom) */}
      <div className={styles.bookAsks}>
        {[...asks].reverse().map((level, i) => (
          <div key={`ask-${i}`} className={styles.bookRow}>
            <div
              className={styles.bookDepthBar}
              style={{
                width: `${(level.total / maxTotal) * 100}%`,
                background: "var(--red-subtle)",
              }}
            />
            <span className="mono text-red">${level.price.toFixed(2)}</span>
            <span className="mono">{level.size}</span>
            <span className="mono text-muted">{level.total}</span>
          </div>
        ))}
      </div>
      {/* Spread */}
      <div className={styles.bookSpread}>
        <span className="mono">Spread: {((asks[0]?.price || 0) - (bids[0]?.price || 0)).toFixed(2)}¢</span>
      </div>
      {/* Bids */}
      <div className={styles.bookBids}>
        {bids.map((level, i) => (
          <div key={`bid-${i}`} className={styles.bookRow}>
            <div
              className={styles.bookDepthBar}
              style={{
                width: `${(level.total / maxTotal) * 100}%`,
                background: "var(--green-subtle)",
              }}
            />
            <span className="mono text-green">${level.price.toFixed(2)}</span>
            <span className="mono">{level.size}</span>
            <span className="mono text-muted">{level.total}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function OrderTicket({
  selectedMarket,
  onSubmit,
}: {
  selectedMarket: string;
  onSubmit: (order: any) => void;
}) {
  const [side, setSide] = useState<"yes" | "no">("yes");
  const [orderType, setOrderType] = useState<"limit" | "market">("limit");
  const [price, setPrice] = useState("0.55");
  const [quantity, setQuantity] = useState("100");
  const [tif, setTif] = useState<"GTC" | "IOC" | "FOK">("GTC");

  const priceNum = parseFloat(price) || 0;
  const qtyNum = parseInt(quantity) || 0;
  const cost = qtyNum * priceNum;
  const takerFee = 0.05 * qtyNum * priceNum * (1 - priceNum);
  const potentialPayout = side === "yes" ? qtyNum * (1 - priceNum) : qtyNum * priceNum;

  return (
    <div className={styles.orderTicket}>
      <div className={styles.panelHeader}>
        <h3>Order Ticket</h3>
      </div>

      {/* Side Toggle */}
      <div className={styles.sideToggle}>
        <button
          className={`${styles.sideBtn} ${side === "yes" ? styles.sideBtnYesActive : ""}`}
          onClick={() => setSide("yes")}
        >
          Buy YES
        </button>
        <button
          className={`${styles.sideBtn} ${side === "no" ? styles.sideBtnNoActive : ""}`}
          onClick={() => setSide("no")}
        >
          Buy NO
        </button>
      </div>

      {/* Order Type */}
      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Order Type</label>
        <div className={styles.typeToggle}>
          <button
            className={`${styles.typeBtn} ${orderType === "limit" ? styles.typeBtnActive : ""}`}
            onClick={() => setOrderType("limit")}
          >
            Limit
          </button>
          <button
            className={`${styles.typeBtn} ${orderType === "market" ? styles.typeBtnActive : ""}`}
            onClick={() => setOrderType("market")}
          >
            Market
          </button>
        </div>
      </div>

      {/* Price */}
      {orderType === "limit" && (
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Price</label>
          <div className={styles.inputRow}>
            <button className={styles.stepBtn} onClick={() => setPrice((p) => (Math.max(0.01, parseFloat(p) - 0.01)).toFixed(2))}>−</button>
            <input
              type="text"
              className={styles.priceInput}
              value={`$${price}`}
              onChange={(e) => setPrice(e.target.value.replace("$", ""))}
            />
            <button className={styles.stepBtn} onClick={() => setPrice((p) => (Math.min(0.99, parseFloat(p) + 0.01)).toFixed(2))}>+</button>
          </div>
          <div className={styles.probHint}>= {(priceNum * 100).toFixed(0)}% probability</div>
        </div>
      )}

      {/* Quantity */}
      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Contracts</label>
        <div className={styles.inputRow}>
          <button className={styles.stepBtn} onClick={() => setQuantity((q) => String(Math.max(1, parseInt(q) - 10)))}>−</button>
          <input
            type="text"
            className={styles.priceInput}
            value={quantity}
            onChange={(e) => setQuantity(e.target.value.replace(/\D/g, ""))}
          />
          <button className={styles.stepBtn} onClick={() => setQuantity((q) => String(parseInt(q) + 10))}>+</button>
        </div>
        <div className={styles.quickQtys}>
          {[25, 50, 100, 250, 500].map((q) => (
            <button key={q} className={styles.quickQtyBtn} onClick={() => setQuantity(String(q))}>
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* TIF */}
      <div className={styles.fieldGroup}>
        <label className={styles.fieldLabel}>Time in Force</label>
        <div className={styles.typeToggle}>
          {(["GTC", "IOC", "FOK"] as const).map((t) => (
            <button
              key={t}
              className={`${styles.typeBtn} ${tif === t ? styles.typeBtnActive : ""}`}
              onClick={() => setTif(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Cost Summary */}
      <div className={styles.costSummary}>
        <div className={styles.costRow}>
          <span>Cost</span>
          <span className="mono">${cost.toFixed(2)}</span>
        </div>
        <div className={styles.costRow}>
          <span>Est. Taker Fee</span>
          <span className="mono">${takerFee.toFixed(2)}</span>
        </div>
        <div className={styles.costRow}>
          <span>Potential Payout</span>
          <span className="mono text-green">${potentialPayout.toFixed(2)}</span>
        </div>
        <div className={`${styles.costRow} ${styles.costRowTotal}`}>
          <span>Total Cost</span>
          <span className="mono">${(cost + takerFee).toFixed(2)}</span>
        </div>
      </div>

      {/* Submit */}
      <button
        className={`${styles.submitBtn} ${side === "yes" ? styles.submitBtnYes : styles.submitBtnNo}`}
        onClick={() => onSubmit({ side, orderType, price: priceNum, quantity: qtyNum, tif, slug: selectedMarket })}
      >
        {side === "yes" ? "Place YES Order" : "Place NO Order"} — ${(cost + takerFee).toFixed(2)}
      </button>
    </div>
  );
}

function PositionsPanel({ positions }: { positions: Position[] }) {
  const totalPnl = positions.reduce((s, p) => s + p.pnl, 0);

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <h3>Open Positions</h3>
        <span className={`badge ${totalPnl >= 0 ? "badge-green" : "badge-red"}`}>
          P&L: ${totalPnl.toFixed(2)}
        </span>
      </div>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Market</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Entry</th>
              <th>Current</th>
              <th>P&L</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
              <tr key={pos.slug}>
                <td style={{ fontWeight: 500, color: "var(--text-primary)", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {pos.slug}
                </td>
                <td>
                  <span className={`badge ${pos.side === "long" ? "badge-green" : "badge-red"}`}>
                    {pos.side.toUpperCase()}
                  </span>
                </td>
                <td className="mono">{pos.quantity}</td>
                <td className="mono">${pos.avgEntry.toFixed(2)}</td>
                <td className="mono">${pos.currentPrice.toFixed(2)}</td>
                <td>
                  <span className={`mono ${pos.pnl >= 0 ? "text-green" : "text-red"}`}>
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
    </div>
  );
}

function OpenOrdersPanel({ orders, onCancel }: { orders: Order[]; onCancel: (id: string) => void }) {
  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <h3>Open Orders</h3>
        <button className="btn btn-ghost btn-sm" onClick={() => orders.forEach((o) => onCancel(o.id))}>
          Cancel All
        </button>
      </div>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Market</th>
              <th>Side</th>
              <th>Type</th>
              <th>Price</th>
              <th>Qty</th>
              <th>Filled</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td style={{ fontWeight: 500, color: "var(--text-primary)", maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {order.slug}
                </td>
                <td>
                  <span className={`badge ${order.side === "buy" ? "badge-green" : "badge-red"}`}>
                    {order.side.toUpperCase()}
                  </span>
                </td>
                <td className="mono" style={{ textTransform: "uppercase" }}>{order.type}</td>
                <td className="mono">${order.price.toFixed(2)}</td>
                <td className="mono">{order.quantity}</td>
                <td className="mono">{order.filled}/{order.quantity}</td>
                <td>
                  <span className={`badge ${order.status === "open" ? "badge-blue" : "badge-yellow"}`}>
                    {order.status.toUpperCase().replace("_", " ")}
                  </span>
                </td>
                <td>
                  <button className="btn btn-ghost btn-sm" onClick={() => onCancel(order.id)}>
                    Cancel
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RiskPanel({ riskStatus }: { riskStatus: RiskStatus }) {
  return (
    <div className={styles.riskPanel}>
      <div className={styles.panelHeader}>
        <h3>Risk Controls</h3>
        <span className={`badge ${riskStatus.circuitBreakerTriggered ? "badge-red" : "badge-green"}`}>
          {riskStatus.circuitBreakerTriggered ? "HALTED" : "ACTIVE"}
        </span>
      </div>
      <div className={styles.riskGrid}>
        <div className={styles.riskItem}>
          <span className={styles.riskLabel}>Daily P&L</span>
          <span className={`${styles.riskValue} mono ${riskStatus.dailyPnl >= 0 ? "text-green" : "text-red"}`}>
            {riskStatus.dailyPnl >= 0 ? "+" : ""}${riskStatus.dailyPnl.toFixed(2)}
          </span>
        </div>
        <div className={styles.riskItem}>
          <span className={styles.riskLabel}>Max Loss Limit</span>
          <span className={`${styles.riskValue} mono`}>${riskStatus.maxDailyLoss.toFixed(2)}</span>
        </div>
        <div className={styles.riskItem}>
          <span className={styles.riskLabel}>Drawdown Used</span>
          <div className="prob-bar-container" style={{ marginTop: 4 }}>
            <div
              className="prob-bar"
              style={{
                width: `${Math.min(100, (Math.abs(riskStatus.dailyPnl) / riskStatus.maxDailyLoss) * 100)}%`,
                background: Math.abs(riskStatus.dailyPnl) > riskStatus.maxDailyLoss * 0.7
                  ? "var(--red)"
                  : "var(--yellow)",
              }}
            />
          </div>
        </div>
      </div>
      <button className={`${styles.killSwitch}`}>
        🛑 Kill Switch — Cancel All & Close Positions
      </button>
    </div>
  );
}

/* ─── Main Trading Page ─── */
export default function TradingPage() {
  const [orderBook, setOrderBook] = useState(generateOrderBook());
  const [positions, setPositions] = useState(generatePositions());
  const [orders, setOrders] = useState(generateOrders());
  const [selectedMarket, setSelectedMarket] = useState("chiefs-super-bowl-lxi");
  const [bottomTab, setBottomTab] = useState<"positions" | "orders">("positions");
  const [riskStatus] = useState<RiskStatus>({
    circuitBreakerTriggered: false,
    dailyPnl: 17.5,
    maxDailyLoss: 500,
  });

  // Simulate order book updates
  useEffect(() => {
    const interval = setInterval(() => {
      setOrderBook(generateOrderBook());
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = useCallback((order: any) => {
    const newOrder: Order = {
      id: `ord_${Date.now()}`,
      slug: order.slug,
      side: order.side === "yes" ? "buy" : "sell",
      type: order.orderType,
      price: order.price,
      quantity: order.quantity,
      filled: 0,
      status: "open",
      createdAt: new Date().toISOString(),
    };
    setOrders((prev) => [newOrder, ...prev]);
    setBottomTab("orders");
  }, []);

  const handleCancelOrder = useCallback((id: string) => {
    setOrders((prev) => prev.filter((o) => o.id !== id));
  }, []);

  return (
    <div className={styles.tradingLayout}>
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">P</div>
          Polymarket Platform
          <span className="live-dot" style={{ marginLeft: 4 }} />
        </div>
        <nav className="nav">
          <a href="/" className="nav-item">Markets</a>
          <a href="/trading" className="nav-item active">Trading</a>
          <button className="nav-item">Arbitrage</button>
          <button className="nav-item">Sentiment</button>
          <button className="nav-item">Portfolio</button>
        </nav>
        <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
          <span className="live-dot" style={{ marginRight: 6 }} />
          Connected
        </span>
      </header>

      {/* Trading Grid */}
      <div className={styles.tradingGrid}>
        {/* Left: Order Book */}
        <div className={styles.leftPanel}>
          <OrderBookPanel bids={orderBook.bids} asks={orderBook.asks} />
        </div>

        {/* Center: Chart Area + Bottom Panels */}
        <div className={styles.centerPanel}>
          {/* Market Info Bar */}
          <div className={styles.marketInfoBar}>
            <div className={styles.marketName}>
              <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>
                Will the Chiefs win Super Bowl LXI?
              </span>
              <span className="badge badge-green" style={{ marginLeft: 8 }}>LIVE</span>
            </div>
            <div className={styles.marketStats}>
              <div className={styles.marketStatItem}>
                <span className={styles.marketStatLabel}>Mid</span>
                <span className="mono" style={{ fontWeight: 600, fontSize: "1.1rem" }}>$0.555</span>
              </div>
              <div className={styles.marketStatItem}>
                <span className={styles.marketStatLabel}>24h Vol</span>
                <span className="mono">$245K</span>
              </div>
              <div className={styles.marketStatItem}>
                <span className={styles.marketStatLabel}>Spread</span>
                <span className="mono">1.0¢</span>
              </div>
              <div className={styles.marketStatItem}>
                <span className={styles.marketStatLabel}>24h Chg</span>
                <span className="mono text-green">+2.3%</span>
              </div>
            </div>
          </div>

          {/* Chart placeholder */}
          <div className={styles.chartArea}>
            <div className={styles.chartPlaceholder}>
              <span style={{ fontSize: "2rem", marginBottom: 8 }}>📈</span>
              <span style={{ color: "var(--text-muted)" }}>Price chart — connect API to display live data</span>
            </div>
          </div>

          {/* Bottom Tabs: Positions / Orders */}
          <div className={styles.bottomSection}>
            <div className={styles.bottomTabs}>
              <button
                className={`${styles.bottomTab} ${bottomTab === "positions" ? styles.bottomTabActive : ""}`}
                onClick={() => setBottomTab("positions")}
              >
                Positions ({positions.length})
              </button>
              <button
                className={`${styles.bottomTab} ${bottomTab === "orders" ? styles.bottomTabActive : ""}`}
                onClick={() => setBottomTab("orders")}
              >
                Open Orders ({orders.length})
              </button>
            </div>
            {bottomTab === "positions" ? (
              <PositionsPanel positions={positions} />
            ) : (
              <OpenOrdersPanel orders={orders} onCancel={handleCancelOrder} />
            )}
          </div>
        </div>

        {/* Right: Order Ticket + Risk */}
        <div className={styles.rightPanel}>
          <OrderTicket selectedMarket={selectedMarket} onSubmit={handleSubmit} />
          <RiskPanel riskStatus={riskStatus} />
        </div>
      </div>
    </div>
  );
}
