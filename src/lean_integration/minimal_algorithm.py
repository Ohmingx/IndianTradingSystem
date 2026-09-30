import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.environ.get("INDIAN_TRADING_SYSTEM_ROOT", os.getcwd()),
        "src"
    )
)

from clr import AddReference

AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from QuantConnect import *
from QuantConnect.Algorithm import QCAlgorithm

from lean_integration.indian_data_adapter import IndianEquityData


class MinimalIndianAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2015, 1, 31)
        self.SetCash(100000)

        self.indian_symbol = self.AddData(
            IndianEquityData,
            "RELIANCE.NS",
            Resolution.Daily,
            TimeZones.Kolkata
        ).Symbol

        self.data_count = 0

    def OnData(self, data):

        if not data.ContainsKey(self.indian_symbol):
            return

        bar = data[self.indian_symbol]

        if self.data_count == 0:
            self.Debug(
                f"FIRST DATA -> "
                f"Local Time: {bar.Time}, "
                f"End Time: {bar.EndTime}, "
                f"O: {bar.GetProperty('Open')}, "
                f"H: {bar.GetProperty('High')}, "
                f"L: {bar.GetProperty('Low')}, "
                f"C: {bar.GetProperty('Close')}, "
                f"V: {bar.GetProperty('Volume')}"
            )

        self.data_count += 1

    def OnEndOfAlgorithm(self):
        self.Debug(
            f"Total Indian data points received: {self.data_count}"
        )

        if self.data_count == 0:
            raise Exception(
                "Failed to receive any custom Indian data points!"
            )