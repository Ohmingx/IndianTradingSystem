"""Validate the small, serialized input contract consumed by LEAN adapters."""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from typing import Any


ALLOWED_SYMBOLS = {
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "WIPRO.NS",
}


def load_runtime_config(path: str, runtime_root: Path) -> dict[str, Any]:
    config_path = Path(path).resolve()
    root = runtime_root.resolve()
    if root not in config_path.parents or config_path.parent.parent != root:
        raise ValueError("Runtime config must be directly inside .runtime/<run_id>/.")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Runtime config is missing or malformed JSON.") from exc
    if not isinstance(config, dict):
        raise ValueError("Runtime config must contain a JSON object.")

    required = {
        "runId",
        "strategy",
        "symbols",
        "startDate",
        "endDate",
        "startingCapital",
        "brokerage",
        "fastPeriod",
        "slowPeriod",
        "positionWeight",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"Runtime config is missing required fields: {missing}")
    if config["runId"] != config_path.parent.name:
        raise ValueError("Runtime config runId does not match its directory.")
    if config["strategy"] not in {"sma_crossover", "wipro_sma"}:
        raise ValueError("Runtime config strategy is not supported.")

    symbols = config["symbols"]
    if not isinstance(symbols, list) or not symbols or any(
        not isinstance(symbol, str) or symbol not in ALLOWED_SYMBOLS for symbol in symbols
    ):
        raise ValueError("Runtime config contains an invalid symbol list.")
    if len(symbols) != len(set(symbols)):
        raise ValueError("Runtime config symbols must be unique.")
    if config["strategy"] == "wipro_sma" and symbols != ["WIPRO.NS"]:
        raise ValueError("Wipro runtime config requires exactly WIPRO.NS.")
    if config["strategy"] == "sma_crossover" and "WIPRO.NS" in symbols:
        raise ValueError("SMA crossover runtime config does not support WIPRO.NS.")

    try:
        start_date = date.fromisoformat(config["startDate"])
        end_date = date.fromisoformat(config["endDate"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Runtime config dates must use YYYY-MM-DD.") from exc
    if start_date.isoformat() != config["startDate"] or end_date.isoformat() != config["endDate"]:
        raise ValueError("Runtime config dates must use YYYY-MM-DD.")
    if start_date > end_date:
        raise ValueError("Runtime config startDate must not be after endDate.")

    capital = config["startingCapital"]
    weight = config["positionWeight"]
    fast = config["fastPeriod"]
    slow = config["slowPeriod"]
    if isinstance(capital, bool) or not isinstance(capital, (int, float)) or not math.isfinite(capital) or capital <= 0:
        raise ValueError("Runtime config startingCapital must be a finite positive number.")
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or not 0 < weight <= 1:
        raise ValueError("Runtime config positionWeight must be between 0 and 1.")
    if type(fast) is not int or type(slow) is not int or not 2 <= fast < slow <= 500:
        raise ValueError("Runtime config SMA periods are invalid.")
    if config["brokerage"].lower() != "zerodha":
        raise ValueError("Runtime config brokerage must be Zerodha.")
    return config