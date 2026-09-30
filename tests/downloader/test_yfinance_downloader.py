import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

from data_pipeline.downloader.yfinance_downloader import YFinanceDownloader

@patch('data_pipeline.downloader.yfinance_downloader.yf.download')
def test_yfinance_auto_adjust_passed(mock_yf_download):
    # Setup mock to return an empty dataframe just to complete the call
    mock_yf_download.return_value = pd.DataFrame()
    
    downloader = YFinanceDownloader(resolution="daily", auto_adjust=True)
    downloader.download("RELIANCE.NS", "2023-01-01", "2023-01-10")
    
    mock_yf_download.assert_called_once()
    _, kwargs = mock_yf_download.call_args
    assert kwargs.get("auto_adjust") is True
    
@patch('data_pipeline.downloader.yfinance_downloader.yf.download')
def test_yfinance_auto_adjust_false(mock_yf_download):
    mock_yf_download.return_value = pd.DataFrame()
    
    downloader = YFinanceDownloader(resolution="daily", auto_adjust=False)
    downloader.download("RELIANCE.NS", "2023-01-01", "2023-01-10")
    
    mock_yf_download.assert_called_once()
    _, kwargs = mock_yf_download.call_args
    assert kwargs.get("auto_adjust") is False
