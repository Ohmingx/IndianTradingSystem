import os
import sys
import yaml
import argparse
import logging
from pathlib import Path

from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from data_pipeline.downloader.yfinance_downloader import YFinanceDownloader
from data_pipeline.normalization.normalizer import Normalizer
from data_pipeline.validation.validators import Validator
from data_pipeline.storage.local_storage import LocalStorage

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description="Download and process Indian stock market data.")
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to configuration file')
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / args.config
    
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        sys.exit(1)

    config = load_config(str(config_path))
    
    symbols = config.get('symbols', [])
    start_date = config.get('start_date')
    end_date = config.get('end_date')
    resolution = config.get('resolution', 'daily')
    auto_adjust = config.get('auto_adjust', False)
    invalid_row_behavior = config.get('invalid_row_behavior', 'exclude')
    overwrite_existing = config.get('overwrite_existing', False)
    
    if not symbols or not start_date or not end_date:
        logger.error("Config must contain symbols, start_date, and end_date.")
        sys.exit(1)

    # Initialize components
    storage = LocalStorage(base_dir=str(project_root / 'data'))
    downloader = YFinanceDownloader(resolution=resolution, auto_adjust=auto_adjust)
    normalizer = Normalizer()
    validator = Validator(invalid_row_behavior=invalid_row_behavior)

    for symbol in symbols:
        logger.info(f"--- Processing {symbol} ---")
        
        # 1. Check if raw data exists
        if not overwrite_existing and storage.raw_data_exists(symbol):
            logger.info(f"Raw data for {symbol} already exists. Skipping download.")
            raw_df = storage.load_raw_data(symbol)
        else:
            # 2. Download
            raw_df = downloader.download(symbol, start_date, end_date)
            if raw_df is None or raw_df.empty:
                logger.error(f"Could not retrieve data for {symbol}. Moving to next symbol.")
                continue
            
            # Save raw data
            storage.save_raw_data(symbol, raw_df)
            logger.info(f"Saved raw data for {symbol} ({len(raw_df)} rows)")

        # 3. Normalize
        try:
            norm_df = normalizer.normalize(raw_df, symbol)
            logger.info(f"Normalized data for {symbol}")
        except Exception as e:
            logger.error(f"Normalization failed for {symbol}: {e}")
            continue

        # 4. Validate
        try:
            valid_df, report = validator.validate_and_report(norm_df, symbol)
            logger.info(f"Validation complete for {symbol}. Report: {report}")
            
            # Combine provenance and validation report
            provenance = {
                "symbol": symbol,
                "source": "yfinance",
                "download_timestamp": datetime.utcnow().isoformat() + "Z",
                "start_date": start_date,
                "end_date": end_date,
                "resolution": resolution,
                "auto_adjust": auto_adjust,
                "timezone": "Asia/Kolkata",
                "row_count": len(valid_df),
                "validation_status": "passed" if report["invalid_ohlc_rows"] == 0 else "warnings/errors_detected",
                "validation_report": report
            }
            
            # Save report
            storage.save_metadata(symbol, provenance)
            
            # Save normalized data
            storage.save_normalized_data(symbol, valid_df)
            logger.info(f"Saved normalized data for {symbol} ({len(valid_df)} rows)")
            
        except Exception as e:
            logger.error(f"Validation failed for {symbol}: {e}")

    logger.info("Pipeline execution finished.")

if __name__ == "__main__":
    main()
