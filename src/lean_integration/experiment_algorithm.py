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

class ExperimentAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2015, 1, 31)
        self.SetCash(100000)

        # 1. Native Equity
        self.equity = self.AddEquity("RELIANCE.NS", Resolution.Daily, Market.India)
        
        # 2. Custom Data linked to the equity symbol
        self.custom_symbol = self.AddData(IndianEquityData, self.equity.Symbol, Resolution.Daily, TimeZones.Kolkata).Symbol

        self.data_count = 0

    def OnData(self, data):
        if not data.ContainsKey(self.custom_symbol):
            return

        custom_data = data[self.custom_symbol]
        
        # Check native equity price
        native_price = self.Securities[self.equity.Symbol].Price
        
        if self.data_count == 0:
            self.Debug(f"EXPERIMENT -> Custom Data Price: {custom_data.Close}, Native Equity Price: {native_price}")
            
        self.data_count += 1
        
    def OnEndOfAlgorithm(self):
        self.Debug(f"Total Indian data points received: {self.data_count}")
        if self.data_count == 0:
            raise Exception("Failed to receive any custom Indian data points!")
