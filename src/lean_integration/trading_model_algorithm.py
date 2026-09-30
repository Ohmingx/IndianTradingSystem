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
from QuantConnect.Orders import OrderStatus


class TradingModelAlgorithm(QCAlgorithm):
    def Initialize(self):
        from QuantConnect.Brokerages import BrokerageName
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2015, 1, 31)
        self.SetAccountCurrency("INR")
        self.SetCash(1000000) # 10L INR
        
        # We use ZerodhaBrokerageModel to get full Indian market mechanics
        self.SetBrokerageModel(BrokerageName.Zerodha, AccountType.Margin)

        # Note: We must use 'RELIANCE.NS' (matching the zip file) and specify Market.India
        self.equity = self.AddEquity("RELIANCE.NS", Resolution.Daily, Market.India)
        self.symbol = self.equity.Symbol
        
        # Assertions to verify correct LEAN semantics
        if self.equity.Type != SecurityType.Equity:
            raise Exception(f"Expected SecurityType.Equity, got {self.equity.Type}")
            
        if self.symbol.ID.Market != Market.India:
            raise Exception(f"Expected Market.India, got {self.symbol.ID.Market}")
            
        tz_id = self.equity.Exchange.TimeZone.Id
        if tz_id != "Asia/Kolkata":
            raise Exception(f"Expected Asia/Kolkata timezone, got {tz_id}")
            
        # Get normal market hours for a weekday (e.g. Wednesday)
        import System
        wednesday = System.DayOfWeek.Wednesday
        market_hours = self.equity.Exchange.Hours.MarketHours[wednesday]
        
        # Verify Market Hours 09:15 - 15:30
        open_time = market_hours.GetMarketOpen(System.TimeSpan.Zero, False)
        close_time = market_hours.GetMarketClose(System.TimeSpan.Zero, False)
        
        if open_time is not None and close_time is not None:
            # open_time and close_time are timedelta objects in Python
            # They have days, seconds, microseconds attributes
            o_h = open_time.seconds // 3600
            o_m = (open_time.seconds % 3600) // 60
            
            c_h = close_time.seconds // 3600
            c_m = (close_time.seconds % 3600) // 60
            
            if not (o_h == 9 and o_m == 15):
                raise Exception(f"Expected open time 09:15, got {o_h}:{o_m}")
            if not (c_h == 15 and c_m == 30):
                raise Exception(f"Expected close time 15:30, got {c_h}:{c_m}")
        else:
            raise Exception("Market hours are missing open or close times.")
            
        self.data_count = 0
        self.ordered = False
        
        self.Debug("Initialization and assertions passed successfully.")

    def OnData(self, data):
        if not data.ContainsKey(self.symbol):
            return
            
        bar = data[self.symbol]
        
        if self.data_count == 0:
            self.Debug(f"FIRST DATA -> Time: {bar.Time}, EndTime: {bar.EndTime}, O: {bar.Open}, H: {bar.High}, L: {bar.Low}, C: {bar.Close}, V: {bar.Volume}")
            # The normalized CSV for 2015-01-01 was: 202.59327697753906, 203.8961944580078, 201.98751831054688, 202.95899963378906, 2963643.0
            # Rounded to 4 decimal places inside LEAN due to scaling
            if abs(bar.Close - 202.9590) > 0.01:
                raise Exception(f"First bar close price mismatch. Expected ~202.9590, got {bar.Close}")
        
        self.data_count += 1
        
        # Deterministic Order on second day
        if self.data_count == 2 and not self.ordered:
            # Buy 100 shares using Limit order at bar close price to avoid MarketOnOpen restriction in Zerodha
            self.LimitOrder(self.symbol, 100, bar.Close)
            self.ordered = True

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug(f"ORDER FILLED -> {orderEvent.FillQuantity} @ {orderEvent.FillPrice}, Fee: {orderEvent.OrderFee}")
            
            if orderEvent.OrderFee.Value.Amount == 0:
                raise Exception("Order fee is zero! Brokerage model is not applying fees.")
            
            # Print Portfolio values
            self.Debug(f"PORTFOLIO -> Cash: {self.Portfolio.Cash}, Total Value: {self.Portfolio.TotalPortfolioValue}")
            
    def OnEndOfAlgorithm(self):
        self.Debug(f"Total bars received: {self.data_count}")
        if self.data_count == 0:
            raise Exception("No data received for the equity!")
        if self.Portfolio.TotalPortfolioValue == 100000:
            raise Exception("Portfolio value did not change, meaning no fees were deducted or order failed.")
