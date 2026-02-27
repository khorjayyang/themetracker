#!/usr/bin/env python3
"""
Daily data fetcher for Theme Rotation Tracker
Runs via GitHub Actions — fetches Yahoo Finance data and writes data.json
"""

import json
import sys
import time
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)

# ─── THEME DEFINITIONS ──────────────────────────────────────────────────────
THEMES = [
    {
        "name": "AI & Tech",
        "etfs": [
            {"ticker": "QQQ",  "label": "Nasdaq 100"},
            {"ticker": "BOTZ", "label": "AI & Robots"},
            {"ticker": "AIQ",  "label": "AI & Big Data"},
            {"ticker": "SOXX", "label": "Semiconductors"},
            {"ticker": "ARKQ", "label": "Autonomous Tech"},
        ]
    },
    {
        "name": "Defence & Aerospace",
        "etfs": [
            {"ticker": "ITA",  "label": "iShares Aerospace"},
            {"ticker": "XAR",  "label": "SPDR Aerospace"},
            {"ticker": "PPA",  "label": "Invesco Defence"},
            {"ticker": "DFEN", "label": "3x Aerospace"},
        ]
    },
    {
        "name": "Financials & Banks",
        "etfs": [
            {"ticker": "XLF",  "label": "Financials SPDR"},
            {"ticker": "KBE",  "label": "Bank ETF"},
            {"ticker": "KRE",  "label": "Regional Banks"},
            {"ticker": "IAI",  "label": "Broker-Dealers"},
        ]
    },
    {
        "name": "Clean Energy",
        "etfs": [
            {"ticker": "ICLN", "label": "Global Clean Energy"},
            {"ticker": "QCLN", "label": "Clean Edge Energy"},
            {"ticker": "TAN",  "label": "Solar Energy"},
            {"ticker": "FAN",  "label": "Wind Energy"},
            {"ticker": "BATT", "label": "Battery Storage"},
        ]
    },
    {
        "name": "Commodities & Mining",
        "etfs": [
            {"ticker": "GLD",  "label": "Gold"},
            {"ticker": "SLV",  "label": "Silver"},
            {"ticker": "COPX", "label": "Copper Miners"},
            {"ticker": "XME",  "label": "Metals & Mining"},
            {"ticker": "DBC",  "label": "Commodities Basket"},
        ]
    },
    {
        "name": "Healthcare & Biotech",
        "etfs": [
            {"ticker": "XLV",  "label": "Healthcare SPDR"},
            {"ticker": "IBB",  "label": "Biotech"},
            {"ticker": "XBI",  "label": "Biotech Equal Weight"},
            {"ticker": "IHI",  "label": "Medical Devices"},
            {"ticker": "ARKG", "label": "Genomic Innovation"},
        ]
    }
]

# ─── FETCH LOGIC ─────────────────────────────────────────────────────────────
def fetch_ticker(ticker):
    """Fetch 3 months of daily data for a ticker."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="3mo", auto_adjust=True)
        if hist.empty:
            print(f"  WARNING: No data for {ticker}")
            return None

        closes = hist["Close"].tolist()
        if len(closes) < 2:
            return None

        last = closes[-1]

        def pct(prev_idx):
            idx = max(0, len(closes) - 1 - prev_idx)
            prev = closes[idx]
            if prev == 0:
                return None
            return round((last - prev) / prev * 100, 2)

        # 1D = yesterday's close vs today's
        pct1d = pct(1)
        # 1W = 5 trading days
        pct1w = pct(5)
        # 1M = ~21 trading days
        pct1m = pct(21)

        # YTD: find first close of the year
        hist_ytd = hist[hist.index.year == datetime.now().year]
        if not hist_ytd.empty:
            first_of_year = hist_ytd["Close"].iloc[0]
            pct_ytd = round((last - first_of_year) / first_of_year * 100, 2)
        else:
            pct_ytd = None

        # 5-day trend (last 5 closes for sparkline)
        trend5 = [round(x, 2) for x in closes[-5:]]

        return {
            "ticker": ticker,
            "price": round(last, 2),
            "pct1d": pct1d,
            "pct1w": pct1w,
            "pct1m": pct1m,
            "pctYtd": pct_ytd,
            "trend5": trend5
        }
    except Exception as e:
        print(f"  ERROR fetching {ticker}: {e}")
        return None


def build_output():
    all_tickers = list({e["ticker"] for t in THEMES for e in t["etfs"]})
    print(f"Fetching {len(all_tickers)} tickers...")

    ticker_data = {}
    for i, ticker in enumerate(all_tickers):
        print(f"  [{i+1}/{len(all_tickers)}] {ticker}")
        data = fetch_ticker(ticker)
        ticker_data[ticker] = data
        time.sleep(0.3)  # polite rate limiting

    themes_out = []
    for theme in THEMES:
        etf_results = []
        for etf_def in theme["etfs"]:
            t = ticker_def = etf_def["ticker"]
            td = ticker_data.get(t) or {
                "ticker": t, "price": None, "pct1d": None,
                "pct1w": None, "pct1m": None, "pctYtd": None, "trend5": []
            }
            etf_results.append({**etf_def, **td})

        # Composite averages (exclude nulls)
        def avg_pct(key):
            vals = [e[key] for e in etf_results if e.get(key) is not None]
            return round(sum(vals) / len(vals), 2) if vals else None

        avg1d = avg_pct("pct1d")
        avg1w = avg_pct("pct1w")
        avg1m = avg_pct("pct1m")
        avg_ytd = avg_pct("pctYtd")

        def score(d1, w1, m1):
            parts = []
            if d1 is not None: parts.append(d1 * 0.3)
            if w1 is not None: parts.append(w1 * 0.4)
            if m1 is not None: parts.append(m1 * 0.3)
            return round(sum(parts), 2) if parts else None

        themes_out.append({
            "name": theme["name"],
            "lead": etf_results[0],
            "etfs": etf_results,
            "avg1d": avg1d,
            "avg1w": avg1w,
            "avg1m": avg1m,
            "avgYtd": avg_ytd,
            "momentum": score(avg1d, avg1w, avg1m)
        })

    now = datetime.now(timezone.utc)
    return {
        "updated": now.strftime("%d %b %Y %H:%M UTC"),
        "timestamp": now.isoformat(),
        "themes": themes_out
    }


if __name__ == "__main__":
    print("=== Theme Rotation Tracker — Daily Data Fetch ===")
    output = build_output()
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✓ data.json written ({len(output['themes'])} themes)")
    print(f"  Updated: {output['updated']}")
