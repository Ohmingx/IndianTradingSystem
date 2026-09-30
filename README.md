# Indian Trading System - Data Pipeline (Phase 2)

This module forms the foundation of the Indian Trading System by providing a robust historical data pipeline. It downloads daily OHLCV data from Yahoo Finance (`yfinance`) for specified NSE symbols, validates the integrity of the data, normalizes the format, and stores it locally.

## Project Purpose
Phase 2 focuses *only* on creating a reliable local data store that can later be ingested or converted by the QuantConnect LEAN backtesting engine.

### What is Deliberately NOT Implemented Yet
- Intraday data processing.
- The QuantConnect LEAN backtesting engine itself.
- Trading strategies or portfolio management.
- Live trading or broker integration.
- Custom corporate-action adjustment engines (we rely on yfinance's adjustments).
- An explicit NSE holiday calendar (only basic missing-row metrics are calculated).

## Setup Instructions

### 1. Create a Python Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Running the Pipeline

### Configuration
Data download parameters are configured in `config/config.yaml`.
You can specify the `symbols`, `start_date`, `end_date`, and `invalid_row_behavior` (fail, warn, exclude).

### Execution
Run the main script from the root directory:
```powershell
python scripts/download_data.py
```
You can also specify a custom config file:
```powershell
python scripts/download_data.py --config config/my_config.yaml
```

## Data Storage Strategy

Data is stored in the `data/` directory:

1. **`data/raw/`**: 
   Contains the unaltered CSV data exactly as downloaded from `yfinance`, preserving the raw source information before our normalization transformation. We never modify this raw data, allowing us to debug or re-normalize if needed.
2. **`data/normalized/`**: 
   Contains the cleaned and validated CSV data. The schema is standardized to: `timestamp` (Asia/Kolkata), `symbol`, `open`, `high`, `low`, `close`, `volume`. This schema is designed to be LEAN-ready.
3. **`data/metadata/`**:
   Contains JSON Data Provenance and Quality Reports for each symbol. This records the exact download timestamp, configuration used, and any validation warnings.

## Validation Process

During normalization and validation, the pipeline checks for:
- **Missing Values**: Any rows with missing OHLCV data.
- **Duplicate Timestamps**: Multiple rows for the same datetime.
- **Invalid OHLC Relationships**: E.g., `high` must be $\ge$ `open`, `low` must be $\le$ `close`.
- **Negative Volume**: Volume must be $\ge 0$.
- **Sorting**: Timestamps must be chronologically ordered.

The behavior when encountering invalid rows depends on the `invalid_row_behavior` config setting.

## Assumptions & Limitations

1. **Explicit Adjustments**: The pipeline does not rely implicitly on `yfinance`'s default adjustment behavior. The `auto_adjust` setting in `config/config.yaml` explicitly dictates whether `yfinance` adjusts the data for splits and dividends. The chosen policy for this phase is `auto_adjust: false`, which means we receive the unadjusted `Close` alongside an `Adj Close` column (which is excluded in final normalization). The provenance metadata records this choice. We do not claim that these unadjusted prices are "correct" for all backtesting purposes.
2. **Timezones**: Normalized timestamps are localized to `Asia/Kolkata`.
3. **Missing Days**: The pipeline currently does not inject missing non-holiday trading days. This will be addressed when a formal NSE calendar is integrated.

## Phase 3: LEAN Data Integration (Custom Data Adapter)

In Phase 3, we successfully created a custom data adapter that allows QuantConnect's LEAN engine to consume our normalized Indian daily equity data without modifying the official LEAN repository.

### LEAN API Used
- **PythonData Mechanism**: The data adapter `IndianEquityData` inherits from `QuantConnect.Python.PythonData`.
- **`GetSource`**: Maps `config.Symbol.Value` directly to the `data/normalized/{symbol}.csv` file, utilizing `SubscriptionTransportMedium.LocalFile`.
- **`Reader`**: Parses the normalized schema (`timestamp,symbol,open,high,low,close,volume`) and constructs dynamic properties on the custom data instance.
- **Algorithm Config**: Uses `AddData(IndianEquityData, "RELIANCE.NS", Resolution.Daily, TimeZones.Kolkata)` to subscribe to the custom data feed.

### Data Source Path & Symbol Mapping
- We use a configurable `INDIAN_TRADING_SYSTEM_DATA_DIR` environment variable to dynamically map paths, ensuring the algorithm remains decoupled from hard-coded local paths.
- **Symbol**: For the integration test, we use `RELIANCE.NS` as the identifier. 
> [!NOTE] 
> This custom data symbol is strictly for reading historical CSVs and is **not** fully configured as a tradable Indian equity `Security` (e.g. mapping corporate actions, market hours, or brokerage routing).

### Timezone Behavior
- The pipeline normalizes source timestamps strictly to `Asia/Kolkata`.
- The `Reader` parses the local time (stripping the explicit `+05:30` offset) to create a pure local `DateTime` representation.
- In `minimal_algorithm.py`, we explicitly configure LEAN to treat the custom data stream as belonging to the Kolkata timezone using `TimeZones.Kolkata` in the `AddData` call. This perfectly aligns LEAN's internal UTC conversion logic with the data's native timezone.

### EndTime Convention
For daily resolution data, `Reader` sets the `EndTime` to `Time + 1 day`, adhering to standard LEAN conventions for daily bar endpoints.

### Integration Test Results
The integration test (`scripts/run_lean_backtest.ps1`) executes a full backtest loop and successfully delivered data directly into the `OnData` handler of the `MinimalIndianAlgorithm`. 

A dummy test order (`self.SetHoldings(self.indian_symbol, 0.5)`) was executed to prove that the execution model doesn't crash on custom data, but this **does not** validate realistic Indian brokerage execution, slippage, or transaction fees, which were excluded from Phase 3. Between this data pipeline and the QuantConnect LEAN engine, the next phase will choose between two primary paths for bringing this data into LEAN:
A. **LEAN native equity data format**: Transforming the CSVs into LEAN's strict expected directory structure, zipping them daily/minutely, and writing map/factor files.
B. **LEAN custom data using BaseData/PythonData**: Creating a custom data reader class within LEAN that directly parses our `normalized` CSVs.
