import os
import json
import pandas as pd
from pathlib import Path

class LocalStorage:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.normalized_dir = self.base_dir / "normalized"
        self.metadata_dir = self.base_dir / "metadata"

        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def raw_data_exists(self, symbol: str) -> bool:
        """Check if raw data for a symbol already exists."""
        return (self.raw_dir / f"{symbol}.csv").exists()

    def save_raw_data(self, symbol: str, df: pd.DataFrame):
        """Save raw downloaded data to CSV."""
        filepath = self.raw_dir / f"{symbol}.csv"
        df.to_csv(filepath)

    def load_raw_data(self, symbol: str) -> pd.DataFrame:
        """Load raw downloaded data from CSV."""
        filepath = self.raw_dir / f"{symbol}.csv"
        if filepath.exists():
            # Read first row to determine index column name dynamically or just read_csv and let it be
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        raise FileNotFoundError(f"Raw data for {symbol} not found at {filepath}")

    def save_normalized_data(self, symbol: str, df: pd.DataFrame):
        """Save normalized data to CSV."""
        filepath = self.normalized_dir / f"{symbol}.csv"
        df.to_csv(filepath, index=False)

    def save_metadata(self, symbol: str, report: dict):
        """Save data quality report to JSON."""
        filepath = self.metadata_dir / f"{symbol}_report.json"
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=4, default=str)
