import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

from data_pipeline.normalization.normalizer import Normalizer

@pytest.fixture
def yf_raw_df():
    data = {
        'Open': [100.0, 105.0],
        'High': [105.0, 108.0],
        'Low': [99.0, 103.0],
        'Close': [104.0, 104.5],
        'Adj Close': [104.0, 104.5],
        'Volume': [1000, 1500]
    }
    index = pd.to_datetime(['2023-01-02', '2023-01-01']) # Deliberately unsorted
    return pd.DataFrame(data, index=index)

def test_normalization_schema_and_types(yf_raw_df):
    normalizer = Normalizer()
    df = normalizer.normalize(yf_raw_df, "TEST")
    
    expected_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    assert list(df.columns) == expected_cols
    
    assert df['timestamp'].dt.tz.zone == 'Asia/Kolkata'
    assert df['open'].dtype == 'float64'
    assert df['volume'].dtype == 'int64'
    
def test_chronological_sorting(yf_raw_df):
    normalizer = Normalizer()
    df = normalizer.normalize(yf_raw_df, "TEST")
    
    # 2023-01-01 should be first
    assert df.iloc[0]['timestamp'].strftime('%Y-%m-%d') == '2023-01-01'
    assert df.iloc[1]['timestamp'].strftime('%Y-%m-%d') == '2023-01-02'
    
def test_missing_time_col():
    df = pd.DataFrame({'Open': [10], 'High': [15]})
    normalizer = Normalizer()
    with pytest.raises(ValueError, match="Could not find a time column"):
        normalizer.normalize(df, "TEST")
