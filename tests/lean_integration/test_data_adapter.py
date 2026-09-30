import pytest
from datetime import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

from lean_integration.indian_data_adapter import IndianEquityData

class MockConfig:
    def __init__(self, symbol_value):
        self.Symbol = MockSymbol(symbol_value)

class MockSymbol:
    def __init__(self, value):
        self.Value = value

def test_get_source_path_resolution():
    os.environ["INDIAN_TRADING_SYSTEM_DATA_DIR"] = "/mock/data/dir"
    adapter = IndianEquityData()
    config = MockConfig("RELIANCE.NS")
    
    source = adapter.get_source(config, datetime.now(), False)
    
    # Python doesn't normalize backslashes vs forward slashes in os.path.join perfectly if we force strings
    # so we'll just check if parts are in the path.
    assert "RELIANCE.NS.csv" in source.path
    assert "normalized" in source.path
    assert "/mock/data/dir" in source.path.replace('\\', '/')

def test_reader_parses_valid_row():
    adapter = IndianEquityData()
    config = MockConfig("RELIANCE.NS")
    line = "2015-01-01 00:00:00+05:30,RELIANCE.NS,100.5,102.0,99.0,101.0,1500000"
    
    custom_data = adapter.reader(config, line, datetime.now(), False)
    
    assert custom_data is not None
    assert custom_data.Symbol.Value == "RELIANCE.NS"
    assert custom_data.Time == datetime(2015, 1, 1, 0, 0, 0)
    assert custom_data.EndTime == datetime(2015, 1, 2, 0, 0, 0)
    
    assert custom_data.Value == 101.0
    assert custom_data["Open"] == 100.5
    assert custom_data["High"] == 102.0
    assert custom_data["Low"] == 99.0
    assert custom_data["Close"] == 101.0
    assert custom_data["Volume"] == 1500000.0

def test_reader_ignores_header():
    adapter = IndianEquityData()
    config = MockConfig("RELIANCE.NS")
    line = "timestamp,symbol,open,high,low,close,volume"
    
    custom_data = adapter.reader(config, line, datetime.now(), False)
    assert custom_data is None

def test_reader_handles_invalid_row():
    adapter = IndianEquityData()
    config = MockConfig("RELIANCE.NS")
    line = "2015-01-01 00:00:00+05:30,RELIANCE.NS,INVALID,102.0,99.0,101.0,1500000"
    
    custom_data = adapter.reader(config, line, datetime.now(), False)
    assert custom_data is None

def test_timezone_conversion_logic():
    # Verify that the offset is stripped to give a local datetime
    adapter = IndianEquityData()
    config = MockConfig("RELIANCE.NS")
    line = "2023-10-15 15:30:00+05:30,RELIANCE.NS,10,10,10,10,100"
    
    custom_data = adapter.reader(config, line, datetime.now(), False)
    # The datetime should match the local representation exactly, discarding +05:30
    assert custom_data.Time == datetime(2023, 10, 15, 15, 30, 0)
