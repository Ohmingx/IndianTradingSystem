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
AddReference("QuantConnect.Indicators")

from QuantConnect import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Indicators import SimpleMovingAverage
from QuantConnect.Orders import OrderStatus


# -------------------------------------------------------------------
# LEAN behaviour verified empirically in Phase 4 + Phase 5 testing:
#
# 1. With Resolution.Daily, OnData fires at bar.EndTime (15:30 IST).
#    The bar's Close is already determined — it is the bar's *historical*
#    close price.  Placing a LimitOrder *at that close* inside OnData
#    therefore risks filling at the same bar's price, which is look-ahead.
#
# 2. SetHoldings at daily resolution submits a MarketOrder by default
#    but Zerodha BrokerageModel rejects MarketOnOpen. We use LimitOrders
#    instead (same as Phase 4).
#
# 3. To guarantee NO same-day execution:
#    - When a crossover is detected on day T, we record it in
#      self.pending_signal[symbol] but do NOT submit any order.
#    - On day T+1 (next OnData call for that symbol), we read the
#      pending signal, submit the Limit order at the new bar's Close,
#      and clear the flag.
#    - This means fill can only happen on day T+2 at the earliest
#      (next day's Open/Close), which is strictly after day T.
#
# 4. The SMA indicators are fed via self.SMA() helper, which auto-
#    updates on each bar.  IsReady returns True only after the required
#    number of bars have been consumed.
# -------------------------------------------------------------------

FAST_PERIOD = 20   # fast SMA window
SLOW_PERIOD = 50   # slow SMA window
POSITION_WEIGHT = 0.2  # equal-weight: 5 symbols × 20% = 100% max

SYMBOLS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
]


class SmaCrossoverAlgorithm(QCAlgorithm):

    def Initialize(self):
        from QuantConnect.Brokerages import BrokerageName

        # ---- Date range (overridden by runner for short/full runs) ----
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2023, 12, 29)

        # ---- Account setup (mirrors Phase 4 TradingModelAlgorithm) ----
        self.SetAccountCurrency("INR")
        self.SetCash(1000000)  # ₹10,00,000

        # ---- Brokerage (unchanged from Phase 4) ----
        self.SetBrokerageModel(BrokerageName.Zerodha, AccountType.Margin)

        # ---- Per-symbol state ----
        self._symbols = {}          # symbol_str -> LEAN Symbol object
        self._fast = {}             # symbol_str -> SMA(20) indicator
        self._slow = {}             # symbol_str -> SMA(50) indicator
        self._bar_count = {}        # symbol_str -> int: bars received
        self._pending_signal = {}   # symbol_str -> "long" | "flat" | None
        self._prev_fast = {}        # symbol_str -> previous fast SMA value
        self._prev_slow = {}        # symbol_str -> previous slow SMA value
        self._total_fills = 0

        for sym_str in SYMBOLS:
            equity = self.AddEquity(sym_str, Resolution.Daily, Market.India)
            sym = equity.Symbol

            # Assert SecurityType.Equity (sanity — mirrors Phase 4)
            if equity.Type != SecurityType.Equity:
                raise Exception(f"{sym_str}: expected SecurityType.Equity, got {equity.Type}")

            self._symbols[sym_str] = sym
            # Use LEAN's built-in SMA indicator (auto-updated per bar)
            self._fast[sym_str] = self.SMA(sym, FAST_PERIOD, Resolution.Daily)
            self._slow[sym_str] = self.SMA(sym, SLOW_PERIOD, Resolution.Daily)
            self._bar_count[sym_str] = 0
            self._pending_signal[sym_str] = None
            self._prev_fast[sym_str] = None
            self._prev_slow[sym_str] = None

        self.Debug(
            f"SmaCrossoverAlgorithm initialized: {len(SYMBOLS)} symbols, "
            f"SMA({FAST_PERIOD}/{SLOW_PERIOD}), weight={POSITION_WEIGHT}"
        )

    # ------------------------------------------------------------------
    def OnData(self, data):
        for sym_str, sym in self._symbols.items():
            if not data.ContainsKey(sym):
                continue

            bar = data[sym]
            self._bar_count[sym_str] += 1
            count = self._bar_count[sym_str]

            fast_ind = self._fast[sym_str]
            slow_ind = self._slow[sym_str]

            # -------------------------------------------------------
            # STEP A: Act on any PENDING signal from the PREVIOUS bar.
            # This is the look-ahead guard: signal from day T is only
            # executed here on day T+1.
            # -------------------------------------------------------
            pending = self._pending_signal[sym_str]
            if pending is not None:
                self._pending_signal[sym_str] = None  # consume immediately

                if pending == "long":
                    # Enter: buy to reach POSITION_WEIGHT of portfolio
                    target_value = self.Portfolio.TotalPortfolioValue * POSITION_WEIGHT
                    current_price = bar.Close
                    shares_needed = int(target_value / current_price)
                    current_qty = self.Portfolio[sym].Quantity
                    qty_to_buy = shares_needed - current_qty
                    if qty_to_buy > 0:
                        order = self.LimitOrder(sym, qty_to_buy, bar.Close)
                        self.Debug(
                            f"[{self.Time.date()}] ORDER_SUBMIT LONG {sym_str} "
                            f"qty={qty_to_buy} limit={bar.Close:.4f} "
                            f"fast={fast_ind.Current.Value:.4f} slow={slow_ind.Current.Value:.4f}"
                        )

                elif pending == "flat":
                    # Exit: liquidate position
                    current_qty = self.Portfolio[sym].Quantity
                    if current_qty > 0:
                        order = self.LimitOrder(sym, -current_qty, bar.Close)
                        self.Debug(
                            f"[{self.Time.date()}] ORDER_SUBMIT FLAT {sym_str} "
                            f"qty={-current_qty} limit={bar.Close:.4f} "
                            f"fast={fast_ind.Current.Value:.4f} slow={slow_ind.Current.Value:.4f}"
                        )

            # -------------------------------------------------------
            # STEP B: Evaluate indicators for TODAY and record any
            # new crossover signal as PENDING (not acted upon yet).
            # The order will only fire in the NEXT OnData call.
            # -------------------------------------------------------
            if not fast_ind.IsReady or not slow_ind.IsReady:
                # Not enough bars yet — log progress every 10 bars per symbol
                if count % 10 == 0:
                    self.Debug(
                        f"[{self.Time.date()}] WARMUP {sym_str} bar={count} "
                        f"fast_ready={fast_ind.IsReady} slow_ready={slow_ind.IsReady}"
                    )
                self._prev_fast[sym_str] = None
                self._prev_slow[sym_str] = None
                continue

            curr_fast = fast_ind.Current.Value
            curr_slow = slow_ind.Current.Value
            prev_fast = self._prev_fast[sym_str]
            prev_slow = self._prev_slow[sym_str]

            # Crossover detection requires at least one previous bar where
            # both indicators were ready
            if prev_fast is not None and prev_slow is not None:
                crossed_above = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
                crossed_below = (prev_fast >= prev_slow) and (curr_fast < curr_slow)

                if crossed_above:
                    self._pending_signal[sym_str] = "long"
                    self.Debug(
                        f"[{self.Time.date()}] SIGNAL LONG {sym_str} "
                        f"fast={curr_fast:.4f} slow={curr_slow:.4f} "
                        f"prev_fast={prev_fast:.4f} prev_slow={prev_slow:.4f} "
                        f"(order will fire NEXT bar)"
                    )
                elif crossed_below:
                    self._pending_signal[sym_str] = "flat"
                    self.Debug(
                        f"[{self.Time.date()}] SIGNAL FLAT {sym_str} "
                        f"fast={curr_fast:.4f} slow={curr_slow:.4f} "
                        f"prev_fast={prev_fast:.4f} prev_slow={prev_slow:.4f} "
                        f"(order will fire NEXT bar)"
                    )

            # Update previous values for next bar's crossover check
            self._prev_fast[sym_str] = curr_fast
            self._prev_slow[sym_str] = curr_slow

    # ------------------------------------------------------------------
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self._total_fills += 1
            fee_amount = orderEvent.OrderFee.Value.Amount
            fee_currency = orderEvent.OrderFee.Value.Currency

            self.Debug(
                f"[{self.Time.date()}] FILL #{self._total_fills} "
                f"qty={orderEvent.FillQuantity} @ {orderEvent.FillPrice:.4f} "
                f"fee={fee_amount:.4f} {fee_currency} "
                f"portfolio_value={self.Portfolio.TotalPortfolioValue:.2f} INR "
                f"cash={self.Portfolio.Cash:.2f} INR"
            )

            # Assert non-zero fees on every fill (Phase 4 requirement)
            if fee_amount == 0:
                raise Exception(
                    f"Fill #{self._total_fills}: fee is zero — "
                    "ZerodhaBrokerageModel should always charge fees."
                )

    # ------------------------------------------------------------------
    def OnEndOfAlgorithm(self):
        self.Debug("=" * 60)
        self.Debug("END OF ALGORITHM SUMMARY")
        self.Debug("=" * 60)

        all_received_data = True
        for sym_str in SYMBOLS:
            count = self._bar_count[sym_str]
            self.Debug(f"  {sym_str}: {count} bars received")
            if count == 0:
                all_received_data = False

        self.Debug(f"  Total fills: {self._total_fills}")
        self.Debug(
            f"  Final portfolio value: {self.Portfolio.TotalPortfolioValue:.2f} INR"
        )
        self.Debug(f"  Final cash: {self.Portfolio.Cash:.2f} INR")

        # Portfolio consistency check: cash + holdings ≈ TotalPortfolioValue
        holdings_value = sum(
            self.Portfolio[self._symbols[s]].HoldingsValue
            for s in SYMBOLS
        )
        computed_total = self.Portfolio.Cash + holdings_value
        discrepancy = abs(computed_total - self.Portfolio.TotalPortfolioValue)
        self.Debug(
            f"  Consistency check: cash({self.Portfolio.Cash:.2f}) + "
            f"holdings({holdings_value:.2f}) = {computed_total:.2f}, "
            f"TotalPortfolioValue={self.Portfolio.TotalPortfolioValue:.2f}, "
            f"discrepancy={discrepancy:.2f}"
        )
        if discrepancy > 1.0:
            self.Debug(f"  WARNING: portfolio discrepancy {discrepancy:.2f} INR > ₹1 threshold")

        if not all_received_data:
            raise Exception("One or more symbols received zero bars — check LEAN data folder and zip files.")

        self.Debug("=" * 60)
