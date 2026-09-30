import logging
from typing import Optional

import pandas as pd
import yfinance as yf


class YFinanceDownloader:
    """Handles downloading historical data from Yahoo Finance."""

    def __init__(self, resolution: str = "daily", auto_adjust: bool = False):
        self.resolution = resolution
        self.auto_adjust = auto_adjust

        if resolution == "daily":
            self.interval = "1d"
        else:
            raise ValueError(
                f"Unsupported resolution: {resolution}. "
                "Currently only 'daily' is supported."
            )

        self.logger = logging.getLogger(__name__)

    def download(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Download historical data for a single symbol from Yahoo Finance.

        Returns:
            pandas.DataFrame if data is successfully retrieved.
            None if no data is available or the download fails.
        """

        self.logger.info(
            f"Downloading {symbol} from {start_date} to {end_date} "
            f"(interval: {self.interval}, auto_adjust: {self.auto_adjust})"
        )

        try:
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=self.interval,
                auto_adjust=self.auto_adjust,
                progress=False,
            )

            if df.empty:
                self.logger.warning(
                    f"No data found for {symbol} between "
                    f"{start_date} and {end_date}"
                )
                return None

            # yfinance can return MultiIndex columns even for a single ticker.
            # Flatten them to the normal OHLCV column names.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            self.logger.info(
                f"Successfully downloaded {len(df)} rows for {symbol}"
            )

            return df

        except Exception:
            self.logger.exception(
                f"Failed to download {symbol}"
            )
            return None

