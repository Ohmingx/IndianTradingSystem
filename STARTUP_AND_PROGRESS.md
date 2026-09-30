# Indian Trading System: Startup and Progress

## Clone the Project

The local checkout currently has no Git remote configured. Copy the HTTPS or SSH clone URL from the GitHub repository's **Code** menu, then clone it with:

```powershell
git clone <GITHUB_REPOSITORY_URL> IndianTradingSystem
Set-Location .\IndianTradingSystem
```

The project expects QuantConnect LEAN in a separate directory. The current default is `D:\LeanT\Lean`; it must contain the compiled launcher at `Launcher\bin\Debug\QuantConnect.Lean.Launcher.exe` and reference data under `Data\`.

## Prerequisites

- Windows PowerShell and Git
- Python 3.10 (the LEAN PythonNet bridge needs a matching Python DLL)
- Node.js 22.12+ or 20.19+
- The separate LEAN checkout, built so its launcher executable exists
- LEAN daily ZIPs for the requested symbols under `data\equity\india\daily\`

The default five-symbol SMA run needs ZIPs for RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, and ICICIBANK.NS. WiproSmaAlgorithm also needs WIPRO.NS.

## First-Time Setup

From the project root, create the Python environment and install both sets of dependencies:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r backend\requirements.txt
```

Install frontend dependencies from the frontend directory:

```powershell
Set-Location .\frontend
npm.cmd ci
Set-Location ..
```

If LEAN is not at the default path, set `LEAN_ROOT` in the terminal used to start the API. The value must be set before Uvicorn starts:

```powershell
$env:LEAN_ROOT = 'D:\path\to\Lean'
```

The PowerShell runner derives `PYTHONNET_PYDLL` from `.venv\Scripts\python.exe`. It also sets the project-root and data-directory environment variables for LEAN.

## Start the Application

Open two PowerShell terminals at the project root.

Terminal 1, start FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, start Vite:

```powershell
npm.cmd --prefix .\frontend run dev -- --host 127.0.0.1
```

Open <http://127.0.0.1:5173/>. The backtest workspace is at <http://127.0.0.1:5173/backtesting>. Vite proxies `/api` requests to FastAPI on port 8000.

Confirm the API is reachable before using the UI:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/strategies
Invoke-RestMethod http://127.0.0.1:8000/api/data/symbols
```

The `POST /api/backtest/run` endpoint runs synchronously. A full backtest can take several minutes; the current API allows one LEAN run at a time. Do not edit or replace the canonical strategy files while a run is active.

## Tests and Build

Run backend tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```

Build the frontend:

```powershell
npm.cmd --prefix .\frontend run build
```

## Progress

- **Phase 1, frontend foundation:** Present in the workspace with the eight-area navigation and design tokens.
- **Phase 2, backtest configuration UI:** Present, including the strategy/symbol/date/capital/brokerage/SMA controls and responsive screenshots.
- **Phase 3, API and isolated runtime configuration:** Backend routes, request validation, run-specific JSON configuration, runtime strategy adapters, and integration with the existing PowerShell runners are present. The canonical strategy files were not edited.
- **Phase 3 end-to-end sign-off:** Not complete. A browser-triggered LEAN run exposed Windows log/process lifecycle and stale-result issues. Runtime guards were subsequently added, but a clean final baseline run and comparison against the recorded metrics have not been confirmed.
- **Phases 4–9:** Not started. Live progress streaming and the results dashboard are intentionally outside the current scope.

Before treating Phase 3 as complete, run the backend tests and frontend build above, then use the UI once with the verified SMA defaults and check its response and archived run under `.runtime\archive\<run_id>\`.
