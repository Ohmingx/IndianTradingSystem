"""
Shared constants and strategy/symbol whitelist for the FastAPI layer.
Paths are resolved from the IndianTradingSystem project root --- never from client input.
"""
from __future__ import annotations

import os
from pathlib import Path

# Project root = IndianTradingSystem/ (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Optional override for monorepo / deployment layouts
if os.environ.get("INDIAN_TRADING_SYSTEM_ROOT"):
    PROJECT_ROOT = Path(os.environ["INDIAN_TRADING_SYSTEM_ROOT"]).resolve()

DATA_DIR = Path(
    os.environ.get("INDIAN_TRADING_SYSTEM_DATA_DIR", PROJECT_ROOT / "data")
).resolve()

RUNTIME_ROOT = PROJECT_ROOT / ".runtime"
LEAN_ROOT = Path(os.environ.get("LEAN_ROOT", r"D:\LeanT\Lean")).resolve()
LEAN_LAUNCHER_DIR = LEAN_ROOT / "Launcher" / "bin" / "Debug"
LEAN_LAUNCHER_EXE = LEAN_LAUNCHER_DIR / "QuantConnect.Lean.Launcher.exe"
LEAN_RESULTS_DIR = LEAN_LAUNCHER_DIR / "results"
LEAN_DATA_DIR = LEAN_ROOT / "Data"

# Runtime adapter (NOT a canonical strategy --- lives under backend/)
RUNTIME_ALGORITHM_PATH = (
    PROJECT_ROOT / "backend" / "lean_runtime" / "runtime_algorithm.py"
)

LEAN_CONFIG_TEMPLATE = PROJECT_ROOT / "config" / "lean_config_template.json"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

ALLOWED_SYMBOLS: frozenset[str] = frozenset(
    {
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "WIPRO.NS",
    }
)

# Frontend strategy id --- LEAN algorithm-type-name on the runtime adapter
STRATEGY_CATALOG: dict[str, dict] = {
    "sma_crossover": {
        "id": "sma_crossover",
        "name": "SMA Dual Crossover (5 Stocks)",
        "className": "SmaCrossoverAlgorithm",
        "runtimeClassName": "RuntimeSmaCrossoverAlgorithm",
        "filePath": "src/lean_integration/sma_crossover_algorithm.py",
        "universeType": "multi-asset",
        "defaultSymbols": [
            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS",
            "HDFCBANK.NS",
            "ICICIBANK.NS",
        ],
        "description": (
            "Canonical multi-stock dual SMA crossover. Runtime adapter injects "
            "parameters without modifying the canonical source file."
        ),
        "supported": True,
    },
    "wipro_sma": {
        "id": "wipro_sma",
        "name": "WIPRO SMA (WiproSmaAlgorithm)",
        "className": "WiproSmaAlgorithm",
        "runtimeClassName": "RuntimeWiproSmaAlgorithm",
        "filePath": "src/lean_integration/wipro_sma_algorithm.py",
        "universeType": "single-asset",
        "defaultSymbols": ["WIPRO.NS"],
        "description": (
            "Separate single-stock algorithm class (WiproSmaAlgorithm). "
            "Runtime adapter injects parameters without modifying the canonical source."
        ),
        "supported": True,
    },
}

CANONICAL_STRATEGY_FILES = [
    PROJECT_ROOT / "src" / "lean_integration" / "sma_crossover_algorithm.py",
    PROJECT_ROOT / "src" / "lean_integration" / "wipro_sma_algorithm.py",
]

DEFAULT_TIMEOUT_SECONDS = 600
