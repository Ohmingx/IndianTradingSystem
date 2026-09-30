"""
Non-mutating runtime adapters for LEAN.

Canonical strategy sources are imported and left untouched on disk.
Module-level constants are patched in-memory for this process only, then
Initialize() applies dates / cash / symbols from INDIAN_TRADING_RUNTIME_CONFIG.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

# Ensure project src/ is importable (same pattern as canonical algorithms)
_ROOT = os.environ.get("INDIAN_TRADING_SYSTEM_ROOT", os.getcwd())
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "src"))

from clr import AddReference  # noqa: E402

AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")
AddReference("QuantConnect.Indicators")

from QuantConnect import *  # noqa: E402,F401,F403
from QuantConnect.Algorithm import QCAlgorithm  # noqa: E402
from QuantConnect.Orders import OrderStatus  # noqa: E402,F401
from backend.lean_runtime.runtime_config import load_runtime_config  # noqa: E402

from lean_integration import sma_crossover_algorithm as sma_mod  # noqa: E402
from lean_integration import wipro_sma_algorithm as wipro_mod  # noqa: E402
from lean_integration.sma_crossover_algorithm import SmaCrossoverAlgorithm  # noqa: E402
from lean_integration.wipro_sma_algorithm import WiproSmaAlgorithm  # noqa: E402


def _load_runtime_config() -> dict:
    path = os.environ.get("INDIAN_TRADING_RUNTIME_CONFIG")
    if not path:
        raise Exception(
            "INDIAN_TRADING_RUNTIME_CONFIG is not set. "
            "The API runner must point at an isolated .runtime/<run_id>/runtime_config.json."
        )
    if not os.path.isfile(path):
        raise Exception(f"Runtime config file not found: {path}")
    return load_runtime_config(path, os.path.join(_ROOT, ".runtime"))


def _parse_ymd(value: str) -> tuple[int, int, int]:
    dt = datetime.strptime(value, "%Y-%m-%d")
    return dt.year, dt.month, dt.day


class RuntimeSmaCrossoverAlgorithm(SmaCrossoverAlgorithm):
    """
    Thin subclass of the canonical SmaCrossoverAlgorithm.
    Does not rewrite sma_crossover_algorithm.py on disk.
    """

    def Initialize(self):
        from QuantConnect.Brokerages import BrokerageName

        cfg = _load_runtime_config()
        if cfg.get("strategy") != "sma_crossover":
            raise Exception(
                f"RuntimeSmaCrossoverAlgorithm received strategy={cfg.get('strategy')}"
            )

        # In-memory overrides - canonical file on disk remains unchanged
        sma_mod.FAST_PERIOD = int(cfg["fastPeriod"])
        sma_mod.SLOW_PERIOD = int(cfg["slowPeriod"])
        sma_mod.POSITION_WEIGHT = float(cfg["positionWeight"])
        sma_mod.SYMBOLS = list(cfg["symbols"])

        sy, sm, sd = _parse_ymd(cfg["startDate"])
        ey, em, ed = _parse_ymd(cfg["endDate"])
        self.SetStartDate(sy, sm, sd)
        self.SetEndDate(ey, em, ed)

        self.SetAccountCurrency("INR")
        self.SetCash(float(cfg["startingCapital"]))
        self.SetBrokerageModel(BrokerageName.Zerodha, AccountType.Margin)

        self._symbols = {}
        self._fast = {}
        self._slow = {}
        self._bar_count = {}
        self._pending_signal = {}
        self._prev_fast = {}
        self._prev_slow = {}
        self._total_fills = 0

        for sym_str in sma_mod.SYMBOLS:
            equity = self.AddEquity(sym_str, Resolution.Daily, Market.India)
            sym = equity.Symbol
            if equity.Type != SecurityType.Equity:
                raise Exception(
                    f"{sym_str}: expected SecurityType.Equity, got {equity.Type}"
                )
            self._symbols[sym_str] = sym
            self._fast[sym_str] = self.SMA(sym, sma_mod.FAST_PERIOD, Resolution.Daily)
            self._slow[sym_str] = self.SMA(sym, sma_mod.SLOW_PERIOD, Resolution.Daily)
            self._bar_count[sym_str] = 0
            self._pending_signal[sym_str] = None
            self._prev_fast[sym_str] = None
            self._prev_slow[sym_str] = None

        self.Debug(
            "RuntimeSmaCrossoverAlgorithm initialized from isolated runtime config: "
            f"{len(sma_mod.SYMBOLS)} symbols, "
            f"SMA({sma_mod.FAST_PERIOD}/{sma_mod.SLOW_PERIOD}), "
            f"weight={sma_mod.POSITION_WEIGHT}, cash={cfg['startingCapital']}"
        )


class RuntimeWiproSmaAlgorithm(WiproSmaAlgorithm):
    """
    Thin subclass of the canonical WiproSmaAlgorithm.
    Does not rewrite wipro_sma_algorithm.py on disk.
    """

    def Initialize(self):
        from QuantConnect.Brokerages import BrokerageName

        cfg = _load_runtime_config()
        if cfg.get("strategy") != "wipro_sma":
            raise Exception(
                f"RuntimeWiproSmaAlgorithm received strategy={cfg.get('strategy')}"
            )

        symbols = list(cfg["symbols"])
        if len(symbols) != 1 or symbols[0] != "WIPRO.NS":
            # Keep honest: canonical single-stock algorithm is WIPRO-only
            raise Exception(
                "WiproSmaAlgorithm runtime adapter requires symbols=['WIPRO.NS'] only."
            )

        wipro_mod.FAST_PERIOD = int(cfg["fastPeriod"])
        wipro_mod.SLOW_PERIOD = int(cfg["slowPeriod"])
        wipro_mod.POSITION_WEIGHT = float(cfg["positionWeight"])
        wipro_mod.SYMBOL_STR = "WIPRO.NS"

        sy, sm, sd = _parse_ymd(cfg["startDate"])
        ey, em, ed = _parse_ymd(cfg["endDate"])
        self.SetStartDate(sy, sm, sd)
        self.SetEndDate(ey, em, ed)

        self.SetAccountCurrency("INR")
        self.SetCash(float(cfg["startingCapital"]))
        self.SetBrokerageModel(BrokerageName.Zerodha, AccountType.Margin)

        equity = self.AddEquity(wipro_mod.SYMBOL_STR, Resolution.Daily, Market.India)
        self._sym = equity.Symbol
        if equity.Type != SecurityType.Equity:
            raise Exception(
                f"{wipro_mod.SYMBOL_STR}: expected SecurityType.Equity, got {equity.Type}"
            )

        self._fast = self.SMA(self._sym, wipro_mod.FAST_PERIOD, Resolution.Daily)
        self._slow = self.SMA(self._sym, wipro_mod.SLOW_PERIOD, Resolution.Daily)
        self._bar_count = 0
        self._pending_signal = None
        self._prev_fast = None
        self._prev_slow = None
        self._total_fills = 0
        self._trades = []

        self.Debug(
            "RuntimeWiproSmaAlgorithm initialized from isolated runtime config: "
            f"symbol={wipro_mod.SYMBOL_STR}, "
            f"SMA({wipro_mod.FAST_PERIOD}/{wipro_mod.SLOW_PERIOD}), "
            f"weight={wipro_mod.POSITION_WEIGHT}, cash={cfg['startingCapital']}"
        )
