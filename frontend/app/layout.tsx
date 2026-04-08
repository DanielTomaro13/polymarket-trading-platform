import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Polymarket Platform — Trading & Analysis",
  description:
    "Real-time prediction market trading, cross-venue arbitrage detection, sentiment analysis, and portfolio management across Polymarket US, Polymarket International, and Kalshi.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
