from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.config import ALLOWED_SYMBOLS, CANONICAL_STRATEGY_FILES, PROJECT_ROOT, STRATEGY_CATALOG
from backend.main import app
from backend.models.schemas import BacktestConfigRequest
from backend.lean_runtime.runtime_config import load_runtime_config
from backend.services.runtime_config_manager import RuntimeConfigManager
from backend.services.backtest_runner import BacktestRunner, BacktestRunnerError
import backend.services.backtest_runner as runner_module

client = TestClient(app)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_list_strategies():
    resp = client.get("/api/strategies")
    assert resp.status_code == 200
    data = resp.json()
    ids = {item["id"] for item in data}
    assert ids == {"sma_crossover", "wipro_sma"}
    by_id = {item["id"]: item for item in data}
    assert by_id["sma_crossover"]["className"] == "SmaCrossoverAlgorithm"
    assert by_id["wipro_sma"]["className"] == "WiproSmaAlgorithm"


def test_list_symbols():
    resp = client.get("/api/data/symbols")
    assert resp.status_code == 200
    symbols = {item["symbol"] for item in resp.json()}
    assert symbols == set(ALLOWED_SYMBOLS)
    assert len(symbols) == 6


def test_validation_rejects_bad_strategy():
    payload = {
        "strategy": "not_a_real_strategy",
        "symbols": ["RELIANCE.NS"],
        "startDate": "2015-01-01",
        "endDate": "2023-12-31",
        "startingCapital": 1000000,
        "brokerage": "zerodha",
        "fastPeriod": 20,
        "slowPeriod": 50,
        "positionWeight": 0.2,
    }
    resp = client.post("/api/backtest/run", json=payload)
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "invalid_strategy"


def test_validation_rejects_bad_symbol():
    runner = BacktestRunner()
    cfg = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=["FAKE.NS"],
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )
    with pytest.raises(BacktestRunnerError) as exc:
        runner.validate_request(cfg)
    assert exc.value.code == "invalid_symbol"


def test_validation_rejects_inverted_dates():
    with pytest.raises(Exception):
        BacktestConfigRequest(
            strategy="sma_crossover",
            symbols=["RELIANCE.NS"],
            startDate="2023-12-31",
            endDate="2015-01-01",
            startingCapital=1000000,
            brokerage="zerodha",
            fastPeriod=20,
            slowPeriod=50,
            positionWeight=0.2,
        )


def test_api_validation_errors_are_frontend_consumable():
    payload = {
        "strategy": "sma_crossover",
        "symbols": ["RELIANCE.NS"],
        "startDate": "2015-01-01",
        "endDate": "2023-12-31",
        "startingCapital": 0,
        "brokerage": "zerodha",
        "fastPeriod": 20,
        "slowPeriod": 50,
        "positionWeight": 0.2,
    }
    response = client.post("/api/backtest/run", json=payload)
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["message"]
    assert response.json()["details"]["errors"]


def test_runtime_config_generation_and_archive(tmp_path: Path):
    mgr = RuntimeConfigManager(runtime_root=tmp_path)
    cfg = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )
    run_id, run_dir = mgr.create_run(cfg)
    assert (run_dir / "runtime_config.json").exists()
    payload = json.loads((run_dir / "runtime_config.json").read_text(encoding="utf-8"))
    assert payload["runId"] == run_id
    assert payload["strategy"] == "sma_crossover"
    mgr.write_execution_config(run_dir, {"algorithm-type-name": "RuntimeSmaCrossoverAlgorithm"})
    archived = mgr.archive_run(run_dir)
    assert archived.exists()
    assert not run_dir.exists()
    assert (archived / "runtime_config.json").exists()


def test_runtime_config_loader_validates_scope_and_parameters(tmp_path: Path):
    runtime_root = tmp_path / ".runtime"
    manager = RuntimeConfigManager(runtime_root=runtime_root)
    cfg = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=list(STRATEGY_CATALOG["sma_crossover"]["defaultSymbols"]),
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )
    run_id, run_dir = manager.create_run(cfg)
    loaded = load_runtime_config(
        str(run_dir / "runtime_config.json"),
        runtime_root,
    )
    assert loaded["runId"] == run_id
    assert loaded["symbols"] == cfg.symbols
    assert loaded["startingCapital"] == cfg.startingCapital
    with pytest.raises(ValueError, match="directly inside"):
        load_runtime_config(str(run_dir.parent / "runtime_config.json"), runtime_root)


def test_runtime_archive_refuses_to_replace_existing_run(tmp_path: Path):
    manager = RuntimeConfigManager(runtime_root=tmp_path)
    cfg = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=["RELIANCE.NS"],
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )
    run_id, run_dir = manager.create_run(cfg)
    archive = manager.archive_run(run_dir)
    duplicate_dir = tmp_path / run_id
    duplicate_dir.mkdir()
    with pytest.raises(FileExistsError):
        manager.archive_run(duplicate_dir)


def test_canonical_strategy_immutability_hashes(tmp_path: Path):
    before = {str(p): _sha256(p) for p in CANONICAL_STRATEGY_FILES}
    mgr = RuntimeConfigManager(runtime_root=tmp_path / ".runtime")
    cfg = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=list(STRATEGY_CATALOG["sma_crossover"]["defaultSymbols"]),
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )
    _, run_dir = mgr.create_run(cfg)
    after = {str(p): _sha256(p) for p in CANONICAL_STRATEGY_FILES}
    assert before == after


EXPECTED_SMA_HASH = "784db8709aa06408dede69497cb3022b27918561f7f6690996ad716b204a453f"
EXPECTED_WIPRO_HASH = "1144e976b00c3df1fa520373a21574b0fd79af7ffb497825e5005baa1bd22d10"


def test_canonical_files_match_pre_phase3_hashes():
    sma = PROJECT_ROOT / "src" / "lean_integration" / "sma_crossover_algorithm.py"
    wipro = PROJECT_ROOT / "src" / "lean_integration" / "wipro_sma_algorithm.py"
    assert _sha256(sma) == EXPECTED_SMA_HASH
    assert _sha256(wipro) == EXPECTED_WIPRO_HASH


def test_runner_handoff_archives_config_and_preserves_strategies(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "data"
    daily_dir = data_dir / "equity" / "india" / "daily"
    daily_dir.mkdir(parents=True)
    for symbol in STRATEGY_CATALOG["sma_crossover"]["defaultSymbols"]:
        (daily_dir / f"{symbol.lower()}.zip").touch()

    lean_root = tmp_path / "Lean"
    launcher = lean_root / "Launcher" / "bin" / "Debug" / "QuantConnect.Lean.Launcher.exe"
    launcher.parent.mkdir(parents=True)
    launcher.touch()
    lean_data = lean_root / "Data"
    lean_data.mkdir()
    results = launcher.parent / "results"
    results.mkdir()
    dll = tmp_path / "python.dll"
    dll.touch()

    monkeypatch.setattr(runner_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(runner_module, "LEAN_ROOT", lean_root)
    monkeypatch.setattr(runner_module, "LEAN_LAUNCHER_EXE", launcher)
    monkeypatch.setattr(runner_module, "LEAN_DATA_DIR", lean_data)
    monkeypatch.setattr(runner_module, "LEAN_RESULTS_DIR", results)

    class FakeProcess:
        pid = 4567

        def __init__(self, command, cwd, env, stdout, stderr, shell):
            self.returncode = None
            run_dir = Path(env["INDIAN_TRADING_RUNTIME_CONFIG"]).parent
            (run_dir / "lean_process.json").write_text(
                json.dumps({"processId": 7654}),
                encoding="utf-8",
            )
            (results / "RuntimeSmaCrossoverAlgorithm-summary.json").write_text(
                json.dumps({"statistics": {"CAGR": "7.583%"}}),
                encoding="utf-8",
            )

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

        def poll(self):
            return self.returncode

    monkeypatch.setattr(runner_module.subprocess, "Popen", FakeProcess)
    runner = BacktestRunner(RuntimeConfigManager(runtime_root=tmp_path / ".runtime"))
    monkeypatch.setattr(runner, "_resolve_python_dll", lambda: str(dll))
    monkeypatch.setattr(runner, "_resolve_powershell", lambda: "powershell.exe")

    hashes_before = {path: _sha256(path) for path in CANONICAL_STRATEGY_FILES}
    config = BacktestConfigRequest(
        strategy="sma_crossover",
        symbols=list(STRATEGY_CATALOG["sma_crossover"]["defaultSymbols"]),
        startDate="2015-01-01",
        endDate="2023-12-31",
        startingCapital=1000000,
        brokerage="zerodha",
        fastPeriod=20,
        slowPeriod=50,
        positionWeight=0.2,
    )

    response = runner.run_sync(config)

    assert response.status == "completed"
    assert response.processId == 7654
    assert response.statistics == {"CAGR": "7.583%"}
    archived_dir = Path(response.runtimeConfigPath).parent
    runtime_payload = json.loads((archived_dir / "runtime_config.json").read_text(encoding="utf-8"))
    execution_payload = json.loads((archived_dir / "execution_config.json").read_text(encoding="utf-8"))
    assert runtime_payload["symbols"] == config.symbols
    assert runtime_payload["fastPeriod"] == 20
    assert runtime_payload["slowPeriod"] == 50
    assert runtime_payload["startingCapital"] == 1000000
    assert execution_payload["algorithm-type-name"] == "RuntimeSmaCrossoverAlgorithm"
    assert (archived_dir / "runner_stdout.txt").exists()
    assert (archived_dir / "runner_stderr.txt").exists()
    assert hashes_before == {path: _sha256(path) for path in CANONICAL_STRATEGY_FILES}