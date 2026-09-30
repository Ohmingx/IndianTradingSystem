import pandas as pd

class Normalizer:
    """Normalizes DataFrame schema and types."""

    def normalize(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Normalizes columns and data types.
        Assumes yfinance output where Date/Datetime is the index, and columns might be 
        Open, High, Low, Close, Adj Close, Volume.
        """
        if df.empty:
            return pd.DataFrame(columns=['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume'])

        # Handle unnamed DatetimeIndex (like default yfinance or tests)
        if df.index.name is None and pd.api.types.is_datetime64_any_dtype(df.index):
            df.index.name = 'Date'
            
        # Reset index to get Date/Datetime as a column
        df = df.reset_index()
    
        # Find the time column
        time_col = None
        for col in df.columns:
            if col.lower() in ['date', 'datetime', 'timestamp']:
                time_col = col
                break

        if not time_col:
            raise ValueError(f"Could not find a time column in data for {symbol}. Columns: {df.columns}")

        # Map columns to lowercase and handle standard yfinance output
        # If 'Close' and 'Adj Close' both exist, we'll keep 'Close' as close, 
        # but yfinance sometimes only returns 'Close'.
        col_mapping = {
            time_col: 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        
        # Rename only the matched columns
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})

        # Ensure all required columns exist
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns for {symbol} after normalization: {missing}")

        # Add symbol column
        df['symbol'] = symbol

        # Filter down to just the columns we want
        df = df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']].copy()

        # Convert types
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        # Convert to Asia/Kolkata
        df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
        
        df['open'] = df['open'].astype('float64')
        df['high'] = df['high'].astype('float64')
        df['low'] = df['low'].astype('float64')
        df['close'] = df['close'].astype('float64')
        df['volume'] = df['volume'].astype('int64')

        # Sort chronologically
        df = df.sort_values('timestamp').reset_index(drop=True)

        return df
