import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

from data_pipeline.validation.validators import Validator

@pytest.fixture
def valid_df():
    data = {
        'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'open': [100.0, 105.0, 102.0],
        'high': [105.0, 108.0, 104.0],
        'low': [99.0, 103.0, 100.0],
        'close': [104.0, 104.5, 101.0],
        'volume': [1000, 1500, 1200]
    }
    return pd.DataFrame(data)

def test_valid_ohlc_row(valid_df):
    validator = Validator(invalid_row_behavior="fail")
    df, report = validator.validate_and_report(valid_df, "TEST")
    
    assert report["invalid_ohlc_rows"] == 0
    assert report["final_rows"] == 3
    assert len(df) == 3

def test_invalid_ohlc_relationship(valid_df):
    # Make high < open
    invalid_df = valid_df.copy()
    invalid_df.loc[0, 'high'] = 98.0
    
    validator = Validator(invalid_row_behavior="exclude")
    df, report = validator.validate_and_report(invalid_df, "TEST")
    
    assert report["invalid_ohlc_rows"] == 1
    assert report["final_rows"] == 2
    assert len(df) == 2
    
def test_negative_volume(valid_df):
    invalid_df = valid_df.copy()
    invalid_df.loc[1, 'volume'] = -500
    
    validator = Validator(invalid_row_behavior="exclude")
    df, report = validator.validate_and_report(invalid_df, "TEST")
    
    assert report["negative_volume_rows"] == 1
    assert report["final_rows"] == 2
    
def test_duplicate_timestamp(valid_df):
    # Add a duplicate row
    invalid_df = pd.concat([valid_df, valid_df.iloc[[1]]], ignore_index=True)
    
    validator = Validator(invalid_row_behavior="exclude")
    df, report = validator.validate_and_report(invalid_df, "TEST")
    
    assert report["duplicate_timestamps"] == 1
    # original length was 3, +1 = 4. one dup excluded -> 3
    assert report["final_rows"] == 3
    
def test_missing_values(valid_df):
    invalid_df = valid_df.copy()
    invalid_df.loc[0, 'close'] = np.nan
    
    validator = Validator(invalid_row_behavior="exclude")
    df, report = validator.validate_and_report(invalid_df, "TEST")
    
    assert report["missing_ohlc_values"] == 1
    assert report["final_rows"] == 2
