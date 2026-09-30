import os
from datetime import datetime, timedelta

from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Common")
from System import DateTime
from QuantConnect import SubscriptionTransportMedium
from QuantConnect.Data import SubscriptionDataSource
from QuantConnect.Python import PythonData


class IndianEquityData(PythonData):
    """
    Custom LEAN Data adapter for normalized Indian equity CSVs.
    Schema: timestamp,symbol,open,high,low,close,volume
    """

    def GetSource(self, config, date, isLive):
        # We rely on LEAN_ROOT or INDIAN_TRADING_SYSTEM_DATA_DIR 
        # to locate the data directory flexibly.
        data_dir = os.environ.get("INDIAN_TRADING_SYSTEM_DATA_DIR")
        if not data_dir:
            # Fallback for local testing if env var isn't set
            data_dir = os.path.join(os.getcwd(), "data")

        # Map the LEAN Symbol.Value to the CSV filename
        file_path = os.path.join(data_dir, "normalized", f"{config.Symbol.Value}.csv")
        return SubscriptionDataSource(file_path, SubscriptionTransportMedium.LocalFile)

    def get_source(self, config, date, isLive):
        return self.GetSource(config, date, isLive)

    def RequiresMapping(self):
        return False

    def IsSparseData(self):
        return False

    def DefaultResolution(self):
        from QuantConnect import Resolution
        return Resolution.Daily

    def SupportedResolutions(self):
        from QuantConnect import Resolution
        return [Resolution.Daily]

    def Reader(self, config, line, date, isLive):
        if not line or not line.strip():
            return None

        parts = line.split(',')
        if len(parts) < 7:
            return None
            
        if parts[0] == "timestamp":
            return None  # Header row

        try:
            # Parse timestamp: "2015-01-01 00:00:00+05:30"
            # LEAN's DataTimeZone dictates the timezone. We strip the offset
            # to feed LEAN a clean local datetime.
            dt_str = parts[0]
            if "+" in dt_str:
                dt_str = dt_str.split("+")[0]
            
            dt_str = dt_str[:19].strip() # '2015-01-01 00:00:00'
            parsed_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

            custom = IndianEquityData()
            custom.Symbol = config.Symbol
            custom.Time = parsed_time
            # For daily bars, LEAN convention implies EndTime is Time + 1 day
            custom.EndTime = parsed_time + timedelta(days=1)
            
            # Map values
            custom.Value = float(parts[5]) # close
            custom["Open"] = float(parts[2])
            custom["High"] = float(parts[3])
            custom["Low"] = float(parts[4])
            custom["Close"] = float(parts[5])
            custom["Volume"] = float(parts[6])
            
            return custom
        except Exception:
            return None

    def reader(self, config, line, date, isLive):
        return self.Reader(config, line, date, isLive)
