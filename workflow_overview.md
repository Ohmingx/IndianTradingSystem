# Complete Strategy Execution Workflow
## Frontend → Backend → Results

---

## 🖥️ PART 1 — What the User Selects in the Frontend

A strategy execution UI would have these input panels:

```
┌─────────────────────────────────────────────────────────────┐
│  PANEL A — Strategy Configuration                           │
│                                                             │
│  Strategy Type:   [ SMA Crossover ▼ ]                      │
│  Fast Period:     [ 20 ]                                    │
│  Slow Period:     [ 50 ]                                    │
│  Position Weight: [ 20% per stock ]                        │
│                                                             │
│  PANEL B — Stock Selection                                  │
│                                                             │
│  ☑ RELIANCE.NS    ☑ TCS.NS    ☑ INFY.NS                  │
│  ☑ HDFCBANK.NS   ☑ ICICIBANK.NS                           │
│  [ + Add New Stock: WIPRO.NS ]                             │
│                                                             │
│  PANEL C — Backtest Parameters                              │
│                                                             │
│  Start Date:     [ 2015-01-01 ]                            │
│  End Date:       [ 2023-12-31 ]                            │
│  Starting Cash:  [ ₹10,00,000 ]                           │
│  Brokerage:      [ Zerodha ▼ ]                            │
│  Account Type:   [ Margin ▼ ]                             │
│                                                             │
│  [ ▶  RUN BACKTEST ]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Every field the user touches maps directly to a value in the algorithm `.py` file.**

---

## 🗂️ PART 2 — Complete File Structure

### What exists BEFORE any strategy runs

```
D:\LeanT\
│
├── Lean\                          ← LEAN Engine (the backtesting engine)
│   ├── Launcher\
│   │   └── bin\Debug\
│   │       ├── QuantConnect.Lean.Launcher.exe   ← ENGINE BINARY
│   │       ├── config.json                       ← ENGINE ENTRY POINT (gets swapped per run)
│   │       └── results\                          ← OUTPUT FOLDER (all results land here)
│   │
│   └── Data\                      ← LEAN's built-in reference data
│       ├── market-hours\          ← NSE/BSE trading hours
│       └── symbol-properties\    ← lot sizes, min price steps
│
└── IndianTradingSystem\           ← YOUR PROJECT
    ├── config\
    │   ├── config.yaml            ← user's stock list + date range
    │   └── lean_config_template.json  ← template for LEAN config injection
    │
    ├── data\                      ← ALL MARKET DATA LIVES HERE
    │   ├── raw\                   ← raw CSV from yfinance
    │   ├── normalized\            ← cleaned/typed CSV
    │   ├── metadata\              ← provenance JSON per symbol
    │   ├── equity\india\daily\    ← LEAN-format ZIPs (engine reads these)
    │   ├── market-hours\          ← copied from Lean\Data\ on first run
    │   └── symbol-properties\    ← copied from Lean\Data\ on first run
    │
    ├── scripts\
    │   ├── download_data.py       ← Step 1: downloads from yfinance
    │   └── run_lean_backtest_sma.ps1  ← Step 3: launches LEAN
    │
    └── src\
        ├── data_pipeline\
        │   ├── downloader\        ← yfinance_downloader.py
        │   ├── normalization\     ← normalizer.py
        │   ├── validation\        ← validators.py
        │   └── storage\           ← local_storage.py
        │
        └── lean_integration\
            └── sma_crossover_algorithm.py   ← Step 2: THE STRATEGY FILE
```

---

## ⚙️ PART 3 — The Complete Step-by-Step Pipeline

### STEP 1 — Data Download & Processing
**Script:** `scripts/download_data.py`  
**Triggered by:** User clicking "Run" or pre-run data check

```
User selects stocks + date range
        │
        ▼
yfinance_downloader.py
  → yfinance.Ticker("RELIANCE.NS").history(...)
  → Returns DataFrame: [Date, Open, High, Low, Close, Adj Close, Volume]
        │
        ▼  [SAVES FILE]
data/raw/RELIANCE.NS.csv          ← raw yfinance output, unchanged
        │
        ▼
normalizer.py
  → Renames columns to [timestamp, open, high, low, close, volume]
  → Converts timestamps to Asia/Kolkata timezone
  → Sorts chronologically
        │
        ▼  [SAVES FILE]
data/normalized/RELIANCE.NS.csv   ← clean typed data
        │
        ▼
validators.py
  → Checks: no NaN prices, High >= Low, volume >= 0
  → Produces validation report dict
        │
        ▼  [SAVES FILE]
data/metadata/RELIANCE.NS_report.json  ← provenance + quality report
        │
        ▼
LEAN FORMAT EXPORT (export_lean_format.py or inline in runner)
  → prices × 10,000  (LEAN uses integer microprices)
  → Format: "YYYYMMDD HH:MM,open,high,low,close,volume"
  → Zipped as: reliance.ns.csv inside reliance.ns.zip
        │
        ▼  [SAVES FILE]
data/equity/india/daily/reliance.ns.zip  ← ENGINE INPUT FILE
```

**Files created per stock:** 4 files total
| File | Path | Purpose |
|------|------|---------|
| `RELIANCE.NS.csv` | `data/raw/` | Raw yfinance download |
| `RELIANCE.NS.csv` | `data/normalized/` | Cleaned data |
| `RELIANCE.NS_report.json` | `data/metadata/` | Data quality report |
| `reliance.ns.zip` | `data/equity/india/daily/` | LEAN engine input |

---

### STEP 2 — Strategy File Creation
**File:** `src/lean_integration/sma_crossover_algorithm.py`  
**Created by:** Developer (once). For new strategies, a new `.py` is created.

The algorithm file is parameterized by constants at the top:

```python
FAST_PERIOD = 20       ← from frontend "Fast Period" input
SLOW_PERIOD = 50       ← from frontend "Slow Period" input
POSITION_WEIGHT = 0.2  ← from frontend "Position Weight" input

SYMBOLS = [            ← from frontend "Stock Selection" checkboxes
    "RELIANCE.NS",
    "TCS.NS",
    ...
]
```

**For each new strategy the user wants to test, ONE new `.py` file is added:**
```
lean_integration/
  sma_crossover_algorithm.py    ← SMA strategy
  wipro_sma_algorithm.py        ← SMA on single stock (new)
  macd_algorithm.py             ← (future: MACD strategy)
  rsi_mean_reversion.py         ← (future: RSI strategy)
```

---

### STEP 3 — LEAN Engine Execution
**Script:** `scripts/run_lean_backtest_sma.ps1`

```
PowerShell script runs:

1. VERIFY all .zip files exist in data/equity/india/daily/
2. SET environment variables:
      INDIAN_TRADING_SYSTEM_ROOT  → project path
      PYTHONNET_PYDLL             → Python DLL for C#↔Python bridge
3. INJECT config into LEAN:
      config.json ← {
        "algorithm-type-name": "SmaCrossoverAlgorithm",
        "algorithm-location":  "path/to/sma_crossover_algorithm.py",
        "data-folder":         "path/to/data/",
        "results-destination-folder": "results"
      }
4. LAUNCH: QuantConnect.Lean.Launcher.exe
5. MONITOR: watch results/log.txt for "Analysis Completed"
6. RESTORE: original config.json
```

**Inside LEAN engine — per trading day:**
```
For each daily bar of each symbol:
  │
  ├─ WARMUP PHASE (first 50 bars)
  │    → Feed data into SMA indicators
  │    → Log every 10 bars: "WARMUP RELIANCE.NS bar=10 fast_ready=False"
  │
  ├─ SIGNAL DETECTION
  │    → SMA(20) crossed above SMA(50)? → pending_signal = "long"
  │    → SMA(20) crossed below SMA(50)? → pending_signal = "flat"
  │    → Log: "SIGNAL LONG RELIANCE.NS fast=198.99 slow=198.79"
  │
  ├─ ORDER SUBMISSION (next bar after signal)
  │    → Calculate qty = (portfolio_value × weight) / price
  │    → LimitOrder(symbol, qty, bar.Close)
  │    → Log: "ORDER_SUBMIT LONG RELIANCE.NS qty=1011 limit=197.77"
  │
  └─ FILL CONFIRMATION (next day, via OnOrderEvent)
       → Log: "FILL #1 qty=1011 @ 197.04 fee=37.69 INR"
       → portfolio_value and cash updated
```

---

### STEP 4 — Output Files Generated
**Location:** `D:\LeanT\Lean\Launcher\bin\Debug\results\`

**Files created per backtest run:** 6 files total

```
results/
├── SmaCrossoverAlgorithm-log.txt          ← ALGORITHM DEBUG LOG
│     Every WARMUP, SIGNAL, ORDER_SUBMIT, FILL line
│     Final summary: total fills, P&L, consistency check
│     Size: ~100KB for 9-year 5-stock run
│
├── SmaCrossoverAlgorithm-order-events.json  ← ALL ORDER EVENTS
│     JSON array: every order, fill, cancel
│     Fields: orderId, symbol, quantity, fillPrice, fee, status
│     Size: ~200KB for 242 fills
│
├── SmaCrossoverAlgorithm-summary.json     ← PERFORMANCE METRICS
│     Sharpe ratio, drawdown, annual return, win rate
│     Equity curve data points (daily portfolio values)
│     Benchmark comparison (vs SPY or Nifty)
│     Size: ~30KB
│
├── SmaCrossoverAlgorithm.json             ← FULL BACKTEST RESULT
│     Complete chart data: OHLCV + indicator values + trade markers
│     Rolling statistics, benchmark, all series
│     Size: ~3MB (this is the main results file)
│
├── log.txt                                ← LEAN ENGINE SYSTEM LOG
│     LEAN internal traces: data feed, handlers, timing
│     Not user-facing — for debugging engine issues
│
├── succeeded-data-requests-TIMESTAMP.txt  ← DATA AUDIT
│     List of every ZIP file LEAN successfully read
│
└── failed-data-requests-TIMESTAMP.txt     ← MISSING DATA AUDIT
      List of any symbols LEAN couldn't find data for
```

---

## 📈 PART 4 — How Results Are Plotted in the Frontend

The `SmaCrossoverAlgorithm.json` (3MB file) contains all chart-ready data.

### What's inside that JSON

```json
{
  "Charts": {
    "Strategy Equity": {
      "Series": {
        "Equity": [
          { "x": 1420070400, "y": 1000000 },   ← daily portfolio value
          { "x": 1422748800, "y": 1002518 },
          ...2240 data points...
        ],
        "Benchmark": [
          ...comparison index values...
        ]
      }
    }
  },
  "Statistics": {
    "Total Orders": "242",
    "Average Win": "2.15%",
    "Average Loss": "-1.87%",
    "Compounding Annual Return": "8.39%",
    "Drawdown": "14.200%",
    "Sharpe Ratio": "0.627",
    "Win Rate": "48%"
  },
  "TotalPerformance": {
    "TradeStatistics": { ... },
    "PortfolioStatistics": { ... }
  }
}
```

### Frontend Charts to Build

```
CHART 1 — Equity Curve
  Source: Charts.Strategy Equity.Series.Equity
  Type: Line chart
  X-axis: Date (Unix timestamp → human date)
  Y-axis: Portfolio value in INR
  Overlay: Benchmark line, buy/sell markers

CHART 2 — Drawdown
  Source: Computed from equity curve
  Type: Area chart (filled red below zero)
  Shows: % drop from peak at each point in time

CHART 3 — Trade P&L Waterfall
  Source: SmaCrossoverAlgorithm-order-events.json
  Type: Bar chart (green=profit, red=loss per round trip)

CHART 4 — SMA Indicator (per stock)
  Source: SmaCrossoverAlgorithm.json Charts section
  Type: Candlestick + 2 line overlays (SMA20, SMA50)
  Markers: ▲ BUY signal, ▼ SELL signal at crossover points

TABLE — Performance Statistics
  Source: Statistics block in SmaCrossoverAlgorithm.json
  Shows: Sharpe, CAGR, max drawdown, win rate, total fees
```

---

## 🔄 PART 5 — Full Flow Summary (One diagram)

```
USER FRONTEND
─────────────
  Selects: stocks, dates, strategy, parameters
      │
      │ POST /run-backtest
      ▼
BACKEND API
─────────────
  1. Validate inputs
  2. Update config.yaml with selected stocks + dates
      │
      ▼
DATA PIPELINE  (download_data.py)
─────────────
  For each stock:
  ┌─────────────────────────────────────────┐
  │ yfinance → raw CSV                      │
  │           → normalized CSV              │
  │           → validation report JSON      │
  │           → LEAN ZIP (prices × 10000)   │
  └─────────────────────────────────────────┘
      │
      ▼
ALGORITHM FILE  (sma_crossover_algorithm.py)
─────────────
  ┌─────────────────────────────────────────┐
  │ Reads: SYMBOLS, FAST_PERIOD, SLOW_PERIOD│
  │ Logic: crossover detection + pending    │
  │        signal pattern (T, T+1, T+2)    │
  └─────────────────────────────────────────┘
      │
      ▼
LEAN ENGINE  (QuantConnect.Lean.Launcher.exe)
─────────────
  ┌─────────────────────────────────────────┐
  │ Reads:  config.json                     │
  │ Reads:  data/equity/india/daily/*.zip   │
  │ Reads:  data/market-hours/              │
  │ Reads:  data/symbol-properties/        │
  │                                         │
  │ Runs:   WiproSmaAlgorithm.Initialize()  │
  │         WiproSmaAlgorithm.OnData() ×N   │
  │         WiproSmaAlgorithm.OnOrderEvent()│
  │         WiproSmaAlgorithm.OnEndOfAlgo() │
  └─────────────────────────────────────────┘
      │
      ▼
OUTPUT FILES  (results/ folder)
─────────────
  ┌─────────────────────────────────────────┐
  │  *-log.txt          → trade log         │
  │  *-order-events.json → all orders/fills │
  │  *-summary.json     → key stats         │
  │  *.json             → full chart data   │
  └─────────────────────────────────────────┘
      │
      │ API reads these files
      ▼
USER FRONTEND
─────────────
  ┌─────────────────────────────────────────┐
  │  Equity curve chart (line)              │
  │  Drawdown chart (area)                  │
  │  Per-trade P&L bars                     │
  │  Candlestick + SMA indicators           │
  │  Stats table: Sharpe, CAGR, Win Rate    │
  └─────────────────────────────────────────┘
```

---

## 📁 PART 6 — Files Count per Strategy Run

| Phase | Files Created | Where |
|-------|--------------|-------|
| **Per stock, data download** | 4 files | `data/raw/`, `data/normalized/`, `data/metadata/`, `data/equity/india/daily/` |
| **Strategy definition** | 1 file | `src/lean_integration/your_strategy.py` |
| **LEAN config (temporary)** | 1 file | `config/temp_config.json` (deleted after run) |
| **Per backtest run output** | 6 files | `Lean/Launcher/bin/Debug/results/` |
| **TOTAL for 5 stocks + 1 run** | **27 files** | Across the whole project |

> [!IMPORTANT]
> The **only file you change per new strategy** is the `.py` algorithm file in `lean_integration/`.
> The **only files LEAN actually reads** are the `.zip` files in `data/equity/india/daily/` + `config.json`.
> Everything else is scaffolding or output.

---

## 🆕 Adding a Brand New Strategy (e.g. MACD)

1. **Create** `src/lean_integration/macd_algorithm.py` — write the strategy class
2. **Add** new ZIPs to `data/equity/india/daily/` if using new stocks
3. **Update** runner script with `AlgoTypeName = "MacdAlgorithm"`
4. **Run** — output lands in `results/MacdAlgorithm-log.txt` etc.
5. **Plot** from `results/MacdAlgorithm.json`

**No other files change.** The data pipeline is reused. The engine is reused.
