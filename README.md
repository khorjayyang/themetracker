# Theme Rotation Tracker

A daily auto-updating dashboard showing which themes money is rotating into across 6 investment themes: AI & Tech, Defence & Aerospace, Financials & Banks, Clean Energy, Commodities & Mining, and Healthcare & Biotech.

## Features
- **Composite Momentum Score** — weighted 1D (30%) + 1W (40%) + 1M (30%) signal
- **Theme Ranking Table** — sortable by any timeframe, expandable ETF breakdown
- **1W Heatmap** — colour-coded performance at a glance
- **Rotation Quadrant Map** — phase analysis (Leading / Recovering / Fading / Outflow)
- **Auto-refreshed daily** — GitHub Actions runs at 23:00 UTC (after US close)

## Setup (5 minutes)

### 1. Create a GitHub repository
Go to https://github.com/new and create a public repository (must be public for free GitHub Pages).

### 2. Upload these files
Upload all files from this folder to your repository:
```
index.html
fetch_data.py
.github/
  workflows/
    daily-refresh.yml
```

### 3. Enable GitHub Pages
- Go to your repo → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` / `(root)`
- Click **Save**

Your dashboard will be live at: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

### 4. Enable GitHub Actions
- Go to your repo → **Actions**
- If prompted, click **"I understand my workflows, go ahead and enable them"**

### 5. Run the first data fetch manually
- Go to **Actions** → **Daily Data Refresh** → **Run workflow**
- This generates `data.json` immediately (instead of waiting until 23:00 UTC)

That's it. The dashboard auto-refreshes every weekday at 23:00 UTC.

## How it works
- `fetch_data.py` downloads 3 months of daily closes for all ETFs via Yahoo Finance (free, no API key)
- It writes `data.json` to the repo with all performance metrics
- `index.html` loads `data.json` on page open and renders everything client-side
- If `data.json` is missing, the dashboard falls back to live Yahoo Finance fetching via a public proxy

## ETFs tracked

| Theme | ETFs |
|-------|------|
| AI & Tech | QQQ, BOTZ, AIQ, SOXX, ARKQ |
| Defence & Aerospace | ITA, XAR, PPA, DFEN |
| Financials & Banks | XLF, KBE, KRE, IAI |
| Clean Energy | ICLN, QCLN, TAN, FAN, BATT |
| Commodities & Mining | GLD, SLV, COPX, XME, DBC |
| Healthcare & Biotech | XLV, IBB, XBI, IHI, ARKG |

## Customisation
To add or change themes/ETFs, edit `THEMES` in both `index.html` (the JS array near the top) and `fetch_data.py` (the Python list at the top). They must stay in sync.
