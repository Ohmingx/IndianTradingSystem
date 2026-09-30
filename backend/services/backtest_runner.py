"""Invoke the existing PowerShell runner with isolated per-run configuration."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from backend.config import (
    ALLOWED_SYMBOLS,
    DATA_DIR,
    DEFAULT_TIMEOUT_SECONDS,
    LEAN_CONFIG_TEMPLATE,
    LEAN_DATA_DIR,
    LEAN_LAUNCHER_EXE,
    LEAN_RESULTS_DIR,
    LEAN_ROOT,
    PROJECT_ROOT,
    RUNTIME_ALGORITHM_PATH,
    STRATEGY_CATALOG,
    VENV_PYTHON,
)
from backend.models.schemas import ApiError, BacktestConfigRequest, BacktestRunResponse
from backend.services.runtime_config_manager import RuntimeConfigManager


class BacktestRunnerError(Exception):
    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


_LEAN_RUN_LOCK = threading.Lock()


class BacktestRunner:
    def __init__(self, runtime_manager: Optional[RuntimeConfigManager] = None) -> None:
        self.runtime = runtime_manager or RuntimeConfigManager()

    def validate_request(self, config: BacktestConfigRequest) -> dict[str, Any]:
        if config.strategy not in STRATEGY_CATALOG:
            raise BacktestRunnerError(
                "invalid_strategy",
                f"Strategy '{config.strategy}' is not in the whitelist.",
                {"allowed": list(STRATEGY_CATALOG.keys())},
            )

        if config.brokerage.lower() != "zerodha":
            raise BacktestRunnerError(
                "invalid_brokerage",
                "Only the verified Zerodha brokerage model is supported.",
                {"received": config.brokerage},
            )

        unknown = [s for s in config.symbols if s not in ALLOWED_SYMBOLS]
        if unknown:
            raise BacktestRunnerError(
                "invalid_symbol",
                f"Unknown or unsupported symbol(s): {', '.join(unknown)}",
                {"allowed": sorted(ALLOWED_SYMBOLS)},
            )

        # Ensure LEAN ZIP files exist for requested symbols
        daily = DATA_DIR / "equity" / "india" / "daily"
        missing_zips: list[str] = []
        for sym in config.symbols:
            zip_name = sym.lower() + ".zip"
            if not (daily / zip_name).is_file():
                missing_zips.append(zip_name)
        if missing_zips:
            raise BacktestRunnerError(
                "missing_data",
                "LEAN-format daily ZIP data is missing for one or more symbols.",
                {"missing": missing_zips, "expectedDir": str(daily)},
            )

        runner_script = PROJECT_ROOT / "scripts" / (
            "run_wipro_sma.ps1" if config.strategy == "wipro_sma" else "run_lean_backtest_sma.ps1"
        )
        if not runner_script.is_file():
            raise BacktestRunnerError("missing_runner", f"Existing runner is missing: {runner_script}")
        if not LEAN_LAUNCHER_EXE.is_file():
            raise BacktestRunnerError(
                "missing_lean_binary",
                f"LEAN launcher not found at {LEAN_LAUNCHER_EXE}",
            )
        if not LEAN_DATA_DIR.is_dir():
            raise BacktestRunnerError(
                "missing_lean_data",
                f"LEAN reference data directory not found at {LEAN_DATA_DIR}",
            )

        powershell = self._resolve_powershell()
        if not powershell:
            raise BacktestRunnerError(
                "missing_powershell",
                "Windows PowerShell is required to invoke the existing LEAN runner.",
            )

        if not VENV_PYTHON.is_file():
            raise BacktestRunnerError(
                "missing_python",
                f"Project virtualenv Python not found at {VENV_PYTHON}",
            )

        python_dll = self._resolve_python_dll()
        if not python_dll or not Path(python_dll).is_file():
            raise BacktestRunnerError(
                "missing_python_dll",
                "PYTHONNET_PYDLL / Python DLL could not be resolved.",
                {"python": str(VENV_PYTHON)},
            )

        if not RUNTIME_ALGORITHM_PATH.is_file():
            raise BacktestRunnerError(
                "missing_runtime_adapter",
                f"Runtime adapter missing: {RUNTIME_ALGORITHM_PATH}",
            )

        if not LEAN_CONFIG_TEMPLATE.is_file():
            raise BacktestRunnerError(
                "missing_lean_template",
                f"LEAN config template missing: {LEAN_CONFIG_TEMPLATE}",
            )
        try:
            template = json.loads(LEAN_CONFIG_TEMPLATE.read_text(encoding="utf-8"))
            if not isinstance(template, dict):
                raise ValueError("LEAN template must contain a JSON object")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise BacktestRunnerError(
                "invalid_lean_template",
                "LEAN config template is malformed or unreadable.",
            ) from exc

        strategy_meta = STRATEGY_CATALOG[config.strategy]
        return {
            "pythonDll": python_dll,
            "strategyMeta": strategy_meta,
            "runnerScript": runner_script,
            "powershell": powershell,
        }

    @staticmethod
    def _resolve_powershell() -> Optional[str]:
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        candidate = system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        if candidate.is_file():
            return str(candidate)
        return shutil.which("powershell.exe")

    def _resolve_python_dll(self) -> Optional[str]:
        try:
            out = subprocess.check_output(
                [
                    str(VENV_PYTHON),
                    "-c",
                    (
                        "import sys, os; "
                        "print(os.path.join(sys.base_prefix, "
                        "f'python{sys.version_info.major}{sys.version_info.minor}.dll'))"
                    ),
                ],
                text=True,
                timeout=30,
            )
            return out.strip()
        except (subprocess.SubprocessError, OSError):
            return None

    def _build_lean_config(self, strategy_meta: dict[str, Any]) -> dict[str, Any]:
        template = json.loads(LEAN_CONFIG_TEMPLATE.read_text(encoding="utf-8"))
        template["algorithm-location"] = str(RUNTIME_ALGORITHM_PATH.resolve())
        template["algorithm-type-name"] = strategy_meta["runtimeClassName"]
        template["algorithm-language"] = "Python"
        template["data-folder"] = str(DATA_DIR.resolve())
        template["results-destination-folder"] = "results"
        template["environment"] = "backtesting"
        return template

    def _read_summary(
        self, class_name: str, previous_mtime: Optional[float]
    ) -> tuple[Optional[Path], Optional[dict]]:
        path = LEAN_RESULTS_DIR / f"{class_name}-summary.json"
        if not path.is_file() or (
            previous_mtime is not None and path.stat().st_mtime <= previous_mtime
        ):
            return None, None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return path, data.get("statistics")
        except (OSError, json.JSONDecodeError):
            return path, None

    def run_sync(
        self,
        config: BacktestConfigRequest,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> BacktestRunResponse:
        if not _LEAN_RUN_LOCK.acquire(blocking=False):
            raise BacktestRunnerError(
                "runner_busy",
                "Another backtest is using the shared LEAN launcher. Try again when it finishes.",
            )
        try:
            return self._run_sync_locked(config, timeout_seconds)
        finally:
            _LEAN_RUN_LOCK.release()

    def _run_sync_locked(
        self,
        config: BacktestConfigRequest,
        timeout_seconds: int,
    ) -> BacktestRunResponse:
        validation = self.validate_request(config)
        strategy_meta = validation["strategyMeta"]
        python_dll = validation["pythonDll"]
        runner_script = validation["runnerScript"]
        powershell = validation["powershell"]

        run_id, run_dir = self.runtime.create_run(config)
        started_at = datetime.now(timezone.utc)
        self.runtime.update_status(
            run_dir,
            status="running",
            startedAt=started_at.isoformat(),
            strategy=config.strategy,
        )

        try:
            lean_config = self._build_lean_config(strategy_meta)
            execution_config_path = self.runtime.write_execution_config(run_dir, lean_config)
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            self.runtime.update_status(
                run_dir,
                status="failed",
                completedAt=completed_at.isoformat(),
                error={"code": "invalid_runtime_config", "message": str(exc)},
            )
            archived = self.runtime.archive_run(run_dir)
            return BacktestRunResponse(
                runId=run_id,
                status="failed",
                strategy=config.strategy,
                message="Could not create the isolated execution configuration.",
                startedAt=started_at.isoformat(),
                completedAt=completed_at.isoformat(),
                error=ApiError(
                    code="invalid_runtime_config",
                    message="The generated LEAN execution configuration was invalid.",
                ),
                runtimeConfigPath=str(archived / "runtime_config.json"),
            )
        runtime_config_path = run_dir / "runtime_config.json"

        process: Optional[subprocess.Popen] = None
        stdout_log = run_dir / "runner_stdout.txt"
        stderr_log = run_dir / "runner_stderr.txt"
        summary_candidate = LEAN_RESULTS_DIR / f"{strategy_meta['runtimeClassName']}-summary.json"
        previous_summary_mtime = (
            summary_candidate.stat().st_mtime if summary_candidate.is_file() else None
        )

        try:
            env = os.environ.copy()
            env["INDIAN_TRADING_SYSTEM_ROOT"] = str(PROJECT_ROOT)
            env["INDIAN_TRADING_SYSTEM_DATA_DIR"] = str(DATA_DIR)
            env["INDIAN_TRADING_RUNTIME_CONFIG"] = str(runtime_config_path.resolve())
            env["PYTHONNET_PYDLL"] = python_dll

            command = [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(runner_script),
                "-LeanRoot",
                str(LEAN_ROOT),
                "-TimeoutSeconds",
                str(timeout_seconds),
                "-RuntimeConfigPath",
                str(runtime_config_path.resolve()),
                "-ExecutionConfigPath",
                str(execution_config_path.resolve()),
                "-RunnerTranscriptPath",
                str(stdout_log.resolve()),
                "-RunnerErrorPath",
                str(stderr_log.resolve()),
            ]
            process = subprocess.Popen(
                command,
                cwd=str(PROJECT_ROOT),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
            )
            runner_pid = process.pid
            self.runtime.update_status(run_dir, runnerProcessId=runner_pid)
            try:
                exit_code = process.wait(timeout=timeout_seconds + 60)
            except subprocess.TimeoutExpired:
                taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
                if process.poll() is None:
                    if taskkill.is_file():
                        subprocess.run(
                            [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                            capture_output=True,
                            check=False,
                        )
                    else:
                        process.kill()
                    process.wait(timeout=10)
                exit_code = process.returncode

            if not stdout_log.exists():
                stdout_log.write_text("", encoding="utf-8")
            if not stderr_log.exists():
                stderr_log.write_text("", encoding="utf-8")

            completed_at = datetime.now(timezone.utc)
            duration = (completed_at - started_at).total_seconds()
            process_record_path = run_dir / "lean_process.json"
            lean_pid = process.pid if process else None
            if process_record_path.is_file():
                try:
                    process_record = json.loads(process_record_path.read_text(encoding="utf-8-sig"))
                    lean_pid = int(process_record.get("processId", lean_pid))
                except (OSError, ValueError, json.JSONDecodeError):
                    pass

            if exit_code != 0:
                stderr_text = stderr_log.read_text(encoding="utf-8", errors="replace")
                stdout_text = stdout_log.read_text(encoding="utf-8", errors="replace")
                failure_reason = (stderr_text or stdout_text).strip()[-2000:]
                self.runtime.update_status(
                    run_dir,
                    status="failed",
                    completedAt=completed_at.isoformat(),
                    exitCode=exit_code,
                    error={"code": "runner_failure", "message": failure_reason or "Existing runner exited unsuccessfully."},
                )
                archived = self.runtime.archive_run(run_dir)
                return BacktestRunResponse(
                    runId=run_id,
                    status="failed",
                    strategy=config.strategy,
                    message="Existing LEAN runner failed.",
                    startedAt=started_at.isoformat(),
                    completedAt=completed_at.isoformat(),
                    durationSeconds=duration,
                    processId=lean_pid,
                    exitCode=exit_code,
                    error=ApiError(
                        code="runner_failure",
                        message="The existing runner failed. See the archived stdout/stderr for diagnostics.",
                        details={"logsPath": str(archived)},
                    ),
                    runtimeConfigPath=str(archived / "runtime_config.json"),
                )

            summary_path, statistics = self._read_summary(
                strategy_meta["runtimeClassName"], previous_summary_mtime
            )
            if summary_path is None:
                self.runtime.update_status(
                    run_dir,
                    status="failed",
                    completedAt=completed_at.isoformat(),
                    exitCode=exit_code,
                    error={"code": "missing_result", "message": "Runner completed without a fresh summary."},
                )
                archived = self.runtime.archive_run(run_dir)
                return BacktestRunResponse(
                    runId=run_id,
                    status="failed",
                    strategy=config.strategy,
                    message="LEAN runner returned success but did not produce a fresh summary.",
                    startedAt=started_at.isoformat(),
                    completedAt=completed_at.isoformat(),
                    durationSeconds=duration,
                    processId=lean_pid,
                    exitCode=exit_code,
                    error=ApiError(
                        code="missing_result",
                        message="No new summary file was produced for this backtest.",
                    ),
                    runtimeConfigPath=str(archived / "runtime_config.json"),
                )

            # Copy key results into the run archive for Phase 4/5
            results_copy = run_dir / "results"
            results_copy.mkdir(exist_ok=True)
            if summary_path and summary_path.exists():
                shutil.copy2(summary_path, results_copy / summary_path.name)
            for pattern in (
                f"{strategy_meta['runtimeClassName']}-log.txt",
                f"{strategy_meta['runtimeClassName']}-order-events.json",
                "log.txt",
            ):
                src = LEAN_RESULTS_DIR / pattern
                if src.exists():
                    shutil.copy2(src, results_copy / src.name)

            self.runtime.update_status(
                run_dir,
                status="completed",
                completedAt=completed_at.isoformat(),
                exitCode=exit_code,
                resultLocation=str(LEAN_RESULTS_DIR),
                summaryPath=str(summary_path) if summary_path else None,
                statistics=statistics,
            )
            archived = self.runtime.archive_run(run_dir)

            return BacktestRunResponse(
                runId=run_id,
                status="completed",
                strategy=config.strategy,
                message="Backtest completed successfully via existing LEAN launcher.",
                startedAt=started_at.isoformat(),
                completedAt=completed_at.isoformat(),
                durationSeconds=duration,
                processId=lean_pid,
                exitCode=exit_code,
                resultLocation=str(LEAN_RESULTS_DIR),
                summaryPath=str(summary_path) if summary_path else None,
                statistics=statistics,
                runtimeConfigPath=str(archived / "runtime_config.json"),
            )

        except BacktestRunnerError:
            raise
        except Exception as exc:  # noqa: BLE001 - surface as structured API error
            completed_at = datetime.now(timezone.utc)
            self.runtime.update_status(
                run_dir,
                status="failed",
                completedAt=completed_at.isoformat(),
                error={"code": "runner_failure", "message": str(exc)},
            )
            try:
                archived = self.runtime.archive_run(run_dir)
                runtime_path = str(archived / "runtime_config.json")
            except Exception:
                runtime_path = str(runtime_config_path)

            return BacktestRunResponse(
                runId=run_id,
                status="failed",
                strategy=config.strategy,
                message="Backtest runner failed.",
                startedAt=started_at.isoformat(),
                completedAt=completed_at.isoformat(),
                durationSeconds=(completed_at - started_at).total_seconds(),
                processId=process.pid if process else None,
                exitCode=process.returncode if process else None,
                error=ApiError(code="runner_failure", message=str(exc)),
                runtimeConfigPath=runtime_path,
            )
        finally:
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=5)
                except Exception:
                    pass
