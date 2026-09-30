import pytest
import os
import sys
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

# We will run the main script logically by importing its components or testing the metadata logic
from data_pipeline.storage.local_storage import LocalStorage

def test_provenance_metadata_contains_adjustment_policy(tmp_path):
    # tmp_path is a pytest fixture for a temporary directory
    storage = LocalStorage(base_dir=str(tmp_path / 'data'))
    
    symbol = "TEST_SYM"
    provenance = {
        "symbol": symbol,
        "source": "yfinance",
        "download_timestamp": datetime.utcnow().isoformat() + "Z",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "resolution": "daily",
        "auto_adjust": False,
        "timezone": "Asia/Kolkata",
        "row_count": 5,
        "validation_status": "passed",
        "validation_report": {"invalid_ohlc_rows": 0}
    }
    
    storage.save_metadata(symbol, provenance)
    
    # Read it back and verify
    file_path = tmp_path / 'data' / 'metadata' / f"{symbol}_report.json"
    assert file_path.exists()
    
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    assert "auto_adjust" in data
    assert data["auto_adjust"] is False
    assert data["source"] == "yfinance"
    assert data["symbol"] == "TEST_SYM"
