"""
FinPulse Global Macroeconomic & Financial Market Data Engine.
Simulates and stores multi-asset class indices, macroeconomic indicators (Inflation, Rates, Oil, VIX),
and global market sentiments in DuckDB for high-speed quantitative analysis.
"""

import os
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
import duckdb

from src.database.connection import DuckDBManager


class MarketDataEngine:
    """Manages macroeconomic streams, multi-asset tickers, and portfolio positions."""

    def __init__(self, db: DuckDBManager | None = None):
        self.db = db if db else DuckDBManager(read_only=False)
        self.init_market_tables()

    def init_market_tables(self) -> None:
        """Creates the quantitative tables for global assets, macro indicators, and portfolio holdings."""
        ddl = """
        CREATE TABLE IF NOT EXISTS macro_indicators (
            date DATE,
            interest_rate DOUBLE,      -- Central Bank Policy Rate (%)
            inflation_cpi DOUBLE,      -- YoY CPI (%)
            crude_oil_brent DOUBLE,    -- USD / Barrel
            vix_volatility DOUBLE,     -- CBOE Volatility Index
            usd_index DOUBLE           -- DXY Dollar Index
        );

        CREATE TABLE IF NOT EXISTS asset_prices (
            date DATE,
            ticker VARCHAR,
            asset_class VARCHAR,       -- Equities, Commodities, Fixed Income, Digital Assets
            close_price DOUBLE,
            daily_return DOUBLE,
            volume DOUBLE
        );

        CREATE TABLE IF NOT EXISTS portfolio_positions (
            position_id VARCHAR PRIMARY KEY,
            asset_name VARCHAR,
            ticker VARCHAR,
            allocation_pct DOUBLE,     -- Portfolio Weight
            entry_price DOUBLE,
            current_price DOUBLE,
            unrealized_pnl DOUBLE,
            risk_tier VARCHAR          -- Low, Moderate, High, Speculative
        );

        CREATE TABLE IF NOT EXISTS macro_sentiment_feed (
            article_id VARCHAR PRIMARY KEY,
            timestamp TIMESTAMP,
            headline VARCHAR,
            source VARCHAR,
            sentiment_score DOUBLE,    -- -1.0 (Extreme Bearish) to +1.0 (Extreme Bullish)
            sentiment_label VARCHAR,   -- Bullish, Neutral, Bearish, Volatile
            impacted_sector VARCHAR
        );
        """
        self.db.execute(ddl)

    def seed_market_data(self, days: int = 180) -> None:
        """Seeds realistic historical macro indicators, asset time-series, and institutional portfolio data."""
        np.random.seed(42)
        random.seed(42)

        start_date = datetime.now().date() - timedelta(days=days)
        dates = [start_date + timedelta(days=i) for i in range(days)]

        # 1. Macro Indicators Time Series
        base_rate = 5.25
        base_cpi = 3.2
        base_oil = 82.5
        base_vix = 16.4
        base_dxy = 104.2

        macro_rows = []
        for d in dates:
            base_rate += np.random.normal(0, 0.01)
            base_cpi += np.random.normal(0, 0.02)
            base_oil += np.random.normal(0, 0.8)
            base_vix = max(11.0, base_vix + np.random.normal(0, 0.5))
            base_dxy += np.random.normal(0, 0.15)

            macro_rows.append({
                "date": d,
                "interest_rate": round(base_rate, 2),
                "inflation_cpi": round(base_cpi, 2),
                "crude_oil_brent": round(base_oil, 2),
                "vix_volatility": round(base_vix, 2),
                "usd_index": round(base_dxy, 2)
            })
        df_macro = pd.DataFrame(macro_rows)

        # 2. Asset Prices
        assets = [
            ("SPY", "Equities (US Large Cap)", 480.0, 0.012),
            ("QQQ", "Equities (Global Tech)", 410.0, 0.016),
            ("GLD", "Commodities (Gold)", 195.0, 0.008),
            ("BND", "Fixed Income (Global Bonds)", 72.0, 0.005),
            ("BTC", "Digital Assets (Bitcoin)", 62000.0, 0.035),
            ("USO", "Commodities (Crude Oil)", 75.0, 0.022)
        ]

        price_rows = []
        for ticker, a_class, start_p, vol in assets:
            curr_p = start_p
            for d in dates:
                ret = np.random.normal(0.0004, vol)
                curr_p = max(1.0, curr_p * (1 + ret))
                price_rows.append({
                    "date": d,
                    "ticker": ticker,
                    "asset_class": a_class,
                    "close_price": round(curr_p, 2),
                    "daily_return": round(ret, 4),
                    "volume": round(float(np.random.uniform(500000, 10000000)), 0)
                })
        df_prices = pd.DataFrame(price_rows)

        # 3. Institutional Portfolio Holdings
        portfolio = [
            {"position_id": "POS-001", "asset_name": "S&P 500 Core Index", "ticker": "SPY", "allocation_pct": 35.0, "entry_price": 465.0, "current_price": 508.4, "unrealized_pnl": 9.33, "risk_tier": "Moderate"},
            {"position_id": "POS-002", "asset_name": "Global Tech Disruptors", "ticker": "QQQ", "allocation_pct": 25.0, "entry_price": 380.0, "current_price": 442.1, "unrealized_pnl": 16.34, "risk_tier": "High"},
            {"position_id": "POS-003", "asset_name": "Gold Bullion Trust", "ticker": "GLD", "allocation_pct": 15.0, "entry_price": 182.0, "current_price": 218.5, "unrealized_pnl": 20.05, "risk_tier": "Low"},
            {"position_id": "POS-004", "asset_name": "Aggregate Bond Shield", "ticker": "BND", "allocation_pct": 15.0, "entry_price": 74.5, "current_price": 72.1, "unrealized_pnl": -3.22, "risk_tier": "Low"},
            {"position_id": "POS-005", "asset_name": "Decentralized Liquidity", "ticker": "BTC", "allocation_pct": 10.0, "entry_price": 54000.0, "current_price": 67800.0, "unrealized_pnl": 25.56, "risk_tier": "Speculative"}
        ]
        df_portfolio = pd.DataFrame(portfolio)

        # 4. Macro Sentiment Stream
        headlines = [
            ("Central Banks Signal Cautious Stance Amid Sticky Core Inflation", "Reuters Macro", -0.35, "Bearish", "Global Banking"),
            ("Tech Earnings Surge Driven by Enterprise Generative AI Adoption", "Bloomberg Markets", 0.78, "Bullish", "Information Technology"),
            ("OPEC+ Extends Voluntary Oil Output Cuts, Tightening Crude Supply", "Financial Times", -0.45, "Volatile", "Energy & Commodities"),
            ("Sovereign Bond Yields Stabilize as Labor Market Shows Controlled Softening", "Wall Street Journal", 0.42, "Bullish", "Fixed Income"),
            ("Geopolitical Flashpoint Stokes Safe-Haven Surge in Gold and Treasury Assets", "CNBC Global", -0.25, "Hedge Alert", "Precious Metals"),
            ("Global Semiconductor Foundry Utilization Reaches 94% Capacity", "TechWire Intelligence", 0.65, "Bullish", "Hardware & Supply Chain")
        ]
        sentiment_rows = []
        for i, (hl, src, sc, lbl, sec) in enumerate(headlines, 1):
            sentiment_rows.append({
                "article_id": f"NEWS-{i:03d}",
                "timestamp": datetime.now() - timedelta(minutes=i * 45),
                "headline": hl,
                "source": src,
                "sentiment_score": sc,
                "sentiment_label": lbl,
                "impacted_sector": sec
            })
        df_sentiment = pd.DataFrame(sentiment_rows)

        # Clear and Insert
        self.db.conn.execute("DELETE FROM macro_indicators;")
        self.db.conn.execute("DELETE FROM asset_prices;")
        self.db.conn.execute("DELETE FROM portfolio_positions;")
        self.db.conn.execute("DELETE FROM macro_sentiment_feed;")

        self.db.conn.register("tmp_macro", df_macro)
        self.db.conn.execute("INSERT INTO macro_indicators SELECT * FROM tmp_macro;")

        self.db.conn.register("tmp_prices", df_prices)
        self.db.conn.execute("INSERT INTO asset_prices SELECT * FROM tmp_prices;")

        self.db.conn.register("tmp_port", df_portfolio)
        self.db.conn.execute("INSERT INTO portfolio_positions SELECT * FROM tmp_port;")

        self.db.conn.register("tmp_sent", df_sentiment)
        self.db.conn.execute("INSERT INTO macro_sentiment_feed SELECT * FROM tmp_sent;")

        print(f"FinPulse Market Engine populated with {len(df_macro)} macro days and {len(df_prices)} asset records.")


if __name__ == "__main__":
    engine = MarketDataEngine()
    engine.seed_market_data()
