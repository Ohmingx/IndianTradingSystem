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
# Single-Stock SMA Crossover Algorithm — WIPRO.NS
#
# Uses the SAME crossover logic as SmaCrossoverAlgorithm but with
# a single new stock: WIPRO (Wipro Ltd, NSE).
#
# Rules (identical to the original 5-stock strategy):
#   - Signal on day T is PENDING; order fires on day T+1 bar close
#   - LimitOrder at close price of T+1 bar (no same-bar look-ahead)
#   - Position size = 100% of portfolio (single stock, weight=1.0)
#   - Zerodha brokerage model, INR account
# -------------------------------------------------------------------

FAST_PERIOD = 20     # fast SMA window (same as multi-stock strategy)
SLOW_PERIOD = 50     # slow SMA window (same as multi-stock strategy)
POSITION_WEIGHT = 1.0  # single stock → use 100% of portfolio

SYMBOL_STR = "WIPRO.NS"


class WiproSmaAlgorithm(QCAlgorithm):

    def Initialize(self):
        from QuantConnect.Brokerages import BrokerageName

        # ---- Date range ----
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2023, 12, 29)

        # ---- Account (same as original) ----
        self.SetAccountCurrency("INR")
        self.SetCash(1_000_000)  # Rs 10,00,000

        # ---- Brokerage ----
        self.SetBrokerageModel(BrokerageName.Zerodha, AccountType.Margin)

        # ---- Add WIPRO.NS ----
        equity = self.AddEquity(SYMBOL_STR, Resolution.Daily, Market.India)
        self._sym = equity.Symbol

        if equity.Type != SecurityType.Equity:
            raise Exception(f"{SYMBOL_STR}: expected SecurityType.Equity, got {equity.Type}")

        # ---- Indicators ----
        self._fast = self.SMA(self._sym, FAST_PERIOD, Resolution.Daily)
        self._slow = self.SMA(self._sym, SLOW_PERIOD, Resolution.Daily)

        # ---- State ----
        self._bar_count = 0
        self._pending_signal = None   # "long" | "flat" | None
        self._prev_fast = None
        self._prev_slow = None
        self._total_fills = 0
        self._trades = []             # list of (date, side, qty, price, fee)

        self.Debug(
            f"WiproSmaAlgorithm initialized: symbol={SYMBOL_STR}, "
            f"SMA({FAST_PERIOD}/{SLOW_PERIOD}), weight={POSITION_WEIGHT}, "
            f"cash=Rs1,000,000"
        )

    # ------------------------------------------------------------------
    def OnData(self, data):
        if not data.ContainsKey(self._sym):
            return

        bar = data[self._sym]
        self._bar_count += 1
        count = self._bar_count

        fast_ind = self._fast
        slow_ind = self._slow

        # -------------------------------------------------------
        # STEP A: Act on PENDING signal from previous bar (T → T+1).
        # This is the look-ahead guard.
        # -------------------------------------------------------
        pending = self._pending_signal
        if pending is not None:
            self._pending_signal = None  # consume

            if pending == "long":
                target_value = self.Portfolio.TotalPortfolioValue * POSITION_WEIGHT
                current_price = bar.Close
                shares_needed = int(target_value / current_price)
                current_qty = self.Portfolio[self._sym].Quantity
                qty_to_buy = shares_needed - current_qty

                if qty_to_buy > 0:
                    self.LimitOrder(self._sym, qty_to_buy, bar.Close)
                    self.Debug(
                        f"[{self.Time.date()}] ORDER_SUBMIT LONG {SYMBOL_STR} "
                        f"qty={qty_to_buy} limit={bar.Close:.4f} "
                        f"fast={fast_ind.Current.Value:.4f} slow={slow_ind.Current.Value:.4f}"
                    )

            elif pending == "flat":
                current_qty = self.Portfolio[self._sym].Quantity
                if current_qty > 0:
                    self.LimitOrder(self._sym, -current_qty, bar.Close)
                    self.Debug(
                        f"[{self.Time.date()}] ORDER_SUBMIT FLAT {SYMBOL_STR} "
                        f"qty={-current_qty} limit={bar.Close:.4f} "
                        f"fast={fast_ind.Current.Value:.4f} slow={slow_ind.Current.Value:.4f}"
                    )

        # -------------------------------------------------------
        # STEP B: Evaluate indicators and record crossover signal.
        # -------------------------------------------------------
        if not fast_ind.IsReady or not slow_ind.IsReady:
            if count % 10 == 0:
                self.Debug(
                    f"[{self.Time.date()}] WARMUP {SYMBOL_STR} bar={count} "
                    f"fast_ready={fast_ind.IsReady} slow_ready={slow_ind.IsReady}"
                )
            self._prev_fast = None
            self._prev_slow = None
            return

        curr_fast = fast_ind.Current.Value
        curr_slow = slow_ind.Current.Value
        prev_fast = self._prev_fast
        prev_slow = self._prev_slow

        if prev_fast is not None and prev_slow is not None:
            crossed_above = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
            crossed_below = (prev_fast >= prev_slow) and (curr_fast < curr_slow)

            if crossed_above:
                self._pending_signal = "long"
                self.Debug(
                    f"[{self.Time.date()}] SIGNAL LONG {SYMBOL_STR} "
                    f"fast={curr_fast:.4f} slow={curr_slow:.4f} "
                    f"prev_fast={prev_fast:.4f} prev_slow={prev_slow:.4f} "
                    f"(order will fire NEXT bar)"
                )
            elif crossed_below:
                self._pending_signal = "flat"
                self.Debug(
                    f"[{self.Time.date()}] SIGNAL FLAT {SYMBOL_STR} "
                    f"fast={curr_fast:.4f} slow={curr_slow:.4f} "
                    f"prev_fast={prev_fast:.4f} prev_slow={prev_slow:.4f} "
                    f"(order will fire NEXT bar)"
                )

        self._prev_fast = curr_fast
        self._prev_slow = curr_slow

    # ------------------------------------------------------------------
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self._total_fills += 1
            fee_amount = orderEvent.OrderFee.Value.Amount
            fee_currency = orderEvent.OrderFee.Value.Currency
            side = "BUY" if orderEvent.FillQuantity > 0 else "SELL"

            self._trades.append({
                "fill": self._total_fills,
                "date": str(self.Time.date()),
                "side": side,
                "qty": abs(orderEvent.FillQuantity),
                "price": orderEvent.FillPrice,
                "fee": fee_amount,
            })

            self.Debug(
                f"[{self.Time.date()}] FILL #{self._total_fills} {side} "
                f"qty={orderEvent.FillQuantity} @ {orderEvent.FillPrice:.4f} "
                f"fee={fee_amount:.4f} {fee_currency} "
                f"portfolio_value={self.Portfolio.TotalPortfolioValue:.2f} INR "
                f"cash={self.Portfolio.Cash:.2f} INR"
            )

            if fee_amount == 0:
                raise Exception(
                    f"Fill #{self._total_fills}: fee is zero — "
                    "ZerodhaBrokerageModel should always charge fees."
                )

    # ------------------------------------------------------------------
    def OnEndOfAlgorithm(self):
        self.Debug("=" * 60)
        self.Debug("END OF ALGORITHM SUMMARY — WIPRO.NS SMA CROSSOVER")
        self.Debug("=" * 60)
        self.Debug(f"  Symbol        : {SYMBOL_STR}")
        self.Debug(f"  SMA periods   : fast={FAST_PERIOD}, slow={SLOW_PERIOD}")
        self.Debug(f"  Total bars    : {self._bar_count}")
        self.Debug(f"  Total fills   : {self._total_fills}")
        self.Debug(f"  Start capital : Rs 1,000,000")
        self.Debug(
            f"  Final portfolio: {self.Portfolio.TotalPortfolioValue:.2f} INR"
        )
        self.Debug(f"  Final cash    : {self.Portfolio.Cash:.2f} INR")

        pnl = self.Portfolio.TotalPortfolioValue - 1_000_000
        pnl_pct = (self.Portfolio.TotalPortfolioValue / 1_000_000 - 1) * 100
        self.Debug(f"  Total P&L     : {pnl:+.2f} INR ({pnl_pct:+.2f}%)")

        # Holdings check
        wipro_holding = self.Portfolio[self._sym]
        self.Debug(f"  Final WIPRO qty held: {wipro_holding.Quantity}")

        # Trade list
        self.Debug(f"\n  Trade log ({len(self._trades)} fills):")
        for t in self._trades:
            self.Debug(
                f"    Fill#{t['fill']} {t['date']} {t['side']} "
                f"qty={t['qty']} @ {t['price']:.2f} fee={t['fee']:.2f}"
            )

        # Consistency check
        holdings_value = wipro_holding.HoldingsValue
        computed_total = self.Portfolio.Cash + holdings_value
        discrepancy = abs(computed_total - self.Portfolio.TotalPortfolioValue)
        self.Debug(
            f"\n  Consistency: cash({self.Portfolio.Cash:.2f}) + "
            f"holdings({holdings_value:.2f}) = {computed_total:.2f}, "
            f"TotalPortfolioValue={self.Portfolio.TotalPortfolioValue:.2f}, "
            f"discrepancy={discrepancy:.2f}"
        )
        if discrepancy > 1.0:
            self.Debug(f"  WARNING: portfolio discrepancy {discrepancy:.2f} INR > Rs1 threshold")

        if self._bar_count == 0:
            raise Exception(f"{SYMBOL_STR}: received zero bars — check LEAN data folder.")

        self.Debug("=" * 60)
