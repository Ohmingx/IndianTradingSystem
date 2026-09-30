"""
Prepare WIPRO.NS data for LEAN and run SMA crossover backtest.

Steps:
  1. Download WIPRO.NS daily data from yfinance (2015-01-01 to 2023-12-31)
  2. Convert to LEAN's internal format (prices * 10000, no decimals)
  3. Save as zip file in data/equity/india/daily/
  4. Print a summary of the data

Run this from the IndianTradingSystem project root.
"""

import sys
import os
import zipfile
import io
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

SYMBOL = "WIPRO.NS"
LEAN_SYMBOL = "wipro.ns"
START_DATE = "2015-01-01"
END_DATE = "2023-12-31"
LEAN_DAILY_DIR = PROJECT_ROOT / "data" / "equity" / "india" / "daily"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def download_wipro():
    """Download WIPRO.NS from yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        print("ERROR: yfinance not installed. Run: pip install yfinance")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"STEP 1: Downloading {SYMBOL} from yfinance")
    print(f"  Date range: {START_DATE} to {END_DATE}")
    print(f"{'='*60}")

    ticker = yf.Ticker(SYMBOL)
    df = ticker.history(start=START_DATE, end=END_DATE, interval="1d", auto_adjust=False)

    if df is None or df.empty:
        print(f"ERROR: No data returned for {SYMBOL}")
        sys.exit(1)

    # Ensure index is tz-naive UTC date
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    df.index = pd.to_datetime(df.index).normalize()
    df = df.sort_index()

    print(f"  Downloaded {len(df)} rows")
    print(f"  Date range in data: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  Sample rows (first 5):")
    print(df[["Open", "High", "Low", "Close", "Volume"]].head(5).to_string())

    # Save raw CSV
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{SYMBOL}.csv"
    df.to_csv(raw_path)
    print(f"\n  Saved raw CSV to: {raw_path}")

    return df


def export_lean_zip(df):
    """Convert DataFrame to LEAN daily zip format."""
    print(f"\n{'='*60}")
    print(f"STEP 2: Converting to LEAN format")
    print(f"  Format: YYYYMMDD HH:MM, open*10000, high*10000, low*10000, close*10000, volume")
    print(f"{'='*60}")

    LEAN_DAILY_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    skipped = 0
    for date, row in df.iterrows():
        try:
            o = int(round(float(row["Open"]) * 10000))
            h = int(round(float(row["High"]) * 10000))
            l = int(round(float(row["Low"]) * 10000))
            c = int(round(float(row["Close"]) * 10000))
            v = int(row["Volume"])
            date_str = date.strftime("%Y%m%d") + " 00:00"
            lines.append(f"{date_str},{o},{h},{l},{c},{v}")
        except Exception as e:
            skipped += 1
            print(f"  Skipped row {date}: {e}")

    print(f"  Converted {len(lines)} rows (skipped {skipped})")
    print(f"\n  Sample LEAN-format rows (first 5):")
    for line in lines[:5]:
        print(f"    {line}")

    csv_content = "\n".join(lines) + "\n"
    zip_path = LEAN_DAILY_DIR / f"{LEAN_SYMBOL}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{LEAN_SYMBOL}.csv", csv_content)

    print(f"\n  Saved LEAN ZIP to: {zip_path}")
    print(f"  ZIP size: {zip_path.stat().st_size:,} bytes")
    return zip_path


def verify_zip(zip_path):
    """Verify the ZIP file is readable."""
    print(f"\n{'='*60}")
    print(f"STEP 3: Verifying ZIP file")
    print(f"{'='*60}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        content = zf.read(names[0]).decode()
        rows = [r for r in content.strip().split("\n") if r]

    print(f"  Files in ZIP: {names}")
    print(f"  Total rows inside ZIP: {len(rows)}")
    print(f"  First row : {rows[0]}")
    print(f"  Last row  : {rows[-1]}")
    print(f"\n  ZIP verification: PASSED")


def print_summary(df):
    """Print descriptive statistics."""
    print(f"\n{'='*60}")
    print(f"STEP 4: Data Summary for {SYMBOL}")
    print(f"{'='*60}")

    close = df["Close"]
    print(f"  Total trading days: {len(df)}")
    print(f"  Date range        : {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"  Price (Close) stats:")
    print(f"    Min   : Rs{close.min():.2f}")
    print(f"    Max   : Rs{close.max():.2f}")
    print(f"    Mean  : Rs{close.mean():.2f}")
    print(f"    Std   : Rs{close.std():.2f}")
    print(f"    Start : Rs{close.iloc[0]:.2f}  ({df.index[0].date()})")
    print(f"    End   : Rs{close.iloc[-1]:.2f}  ({df.index[-1].date()})")

    total_return = (close.iloc[-1] / close.iloc[0] - 1) * 100
    print(f"  Total return (raw): {total_return:+.1f}%")

    vol = df["Volume"]
    print(f"  Avg daily volume  : {vol.mean():,.0f} shares")
    print(f"  Files written to  : {LEAN_DAILY_DIR}")


if __name__ == "__main__":
    print(f"\n{'#'*60}")
    print(f"# WIPRO.NS DATA PREPARATION FOR LEAN BACKTEST")
    print(f"# New stock: {SYMBOL}")
    print(f"# Strategy : SMA(20) / SMA(50) Crossover")
    print(f"{'#'*60}")

    df = download_wipro()
    zip_path = export_lean_zip(df)
    verify_zip(zip_path)
    print_summary(df)

    print(f"\n{'='*60}")
    print(f"DATA PREPARATION COMPLETE")
    print(f"  WIPRO.NS is ready for LEAN backtest.")
    print(f"  Next: Run the PowerShell backtest script.")
    print(f"{'='*60}\n")
