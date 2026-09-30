import pandas as pd
from typing import Tuple, Dict, Any

class Validator:
    """Validates OHLCV data."""

    def __init__(self, invalid_row_behavior: str = "exclude"):
        self.invalid_row_behavior = invalid_row_behavior.lower()

    def validate_and_report(self, df: pd.DataFrame, symbol: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates the DataFrame and generates a Data Quality Report.
        Assumes the DataFrame has standard columns: timestamp, open, high, low, close, volume.
        """
        report = {
            "symbol": symbol,
            "first_timestamp": None,
            "last_timestamp": None,
            "initial_rows": len(df),
            "missing_ohlc_values": 0,
            "duplicate_timestamps": 0,
            "invalid_ohlc_rows": 0,
            "negative_volume_rows": 0,
            "min_price": None,
            "max_price": None,
            "total_volume": None,
            "detected_gaps": 0, # Difficult to accurately calculate without a calendar, set to 0 for now
            "final_rows": 0
        }

        if df.empty:
            return df, report

        report["first_timestamp"] = df['timestamp'].min()
        report["last_timestamp"] = df['timestamp'].max()

        # Check for missing values in OHLCV
        missing_mask = df[['open', 'high', 'low', 'close', 'volume']].isnull().any(axis=1)
        report["missing_ohlc_values"] = int(missing_mask.sum())

        # Check for duplicates
        duplicate_mask = df.duplicated(subset=['timestamp'])
        report["duplicate_timestamps"] = int(duplicate_mask.sum())

        # OHLC Relationships
        # high >= open, high >= close, high >= low
        # low <= open, low <= close
        invalid_ohlc_mask = (
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['high'] < df['low']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )
        report["invalid_ohlc_rows"] = int(invalid_ohlc_mask.sum())

        # Volume >= 0
        negative_vol_mask = df['volume'] < 0
        report["negative_volume_rows"] = int(negative_vol_mask.sum())

        # Aggregate metrics for report (using valid-ish data)
        report["min_price"] = float(df[['open', 'high', 'low', 'close']].min().min())
        report["max_price"] = float(df[['open', 'high', 'low', 'close']].max().max())
        report["total_volume"] = float(df['volume'].sum())

        # Combine bad rows mask
        bad_rows_mask = missing_mask | duplicate_mask | invalid_ohlc_mask | negative_vol_mask

        if bad_rows_mask.any():
            if self.invalid_row_behavior == "fail":
                raise ValueError(f"Validation failed for {symbol}. Invalid rows detected.")
            elif self.invalid_row_behavior == "warn":
                print(f"WARNING: {symbol} has {bad_rows_mask.sum()} invalid rows. Keeping them as per configuration.")
                valid_df = df
            else: # exclude
                valid_df = df[~bad_rows_mask].copy()
        else:
            valid_df = df

        report["final_rows"] = len(valid_df)

        return valid_df, report
