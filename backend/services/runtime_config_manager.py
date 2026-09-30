"""
Isolated per-run configuration under .runtime/<run_id>/.

Never writes into config/config.yaml or canonical strategy source files.
"""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from backend.config import PROJECT_ROOT, RUNTIME_ROOT
from backend.models.schemas import BacktestConfigRequest


class RuntimeConfigManager:
    def __init__(self, runtime_root: Optional[Path] = None) -> None:
        self.runtime_root = Path(runtime_root or RUNTIME_ROOT)
        self.runtime_root.mkdir(parents=True, exist_ok=True)

    def create_run(self, config: BacktestConfigRequest) -> tuple[str, Path]:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
        run_dir = self.runtime_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        payload = config.model_dump()
        payload["runId"] = run_id
        payload["createdAt"] = datetime.now(timezone.utc).isoformat()

        try:
            (run_dir / "runtime_config.json").write_text(
                json.dumps(payload, indent=2, allow_nan=False),
                encoding="utf-8",
            )
            (run_dir / "status.json").write_text(
                json.dumps(
                    {
                        "runId": run_id,
                        "status": "queued",
                        "createdAt": payload["createdAt"],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            shutil.rmtree(run_dir, ignore_errors=True)
            raise

        return run_id, run_dir

    def write_execution_config(self, run_dir: Path, lean_config: dict[str, Any]) -> Path:
        run_dir = self.assert_path_inside_runtime(run_dir, self.runtime_root)
        if run_dir.parent != self.runtime_root.resolve() or run_dir.name == "archive":
            raise ValueError("Execution config must belong to a direct runtime run directory")
        path = run_dir / "execution_config.json"
        path.write_text(json.dumps(lean_config, indent=2, allow_nan=False), encoding="utf-8")
        return path

    def update_status(self, run_dir: Path, **fields: Any) -> Path:
        status_path = run_dir / "status.json"
        current: dict[str, Any] = {}
        if status_path.exists():
            current = json.loads(status_path.read_text(encoding="utf-8"))
        current.update(fields)
        current["updatedAt"] = datetime.now(timezone.utc).isoformat()
        status_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return status_path

    def archive_run(self, run_dir: Path) -> Path:
        """Move finished run folder under .runtime/archive/."""
        run_dir = self.assert_path_inside_runtime(run_dir, self.runtime_root)
        if run_dir.parent != self.runtime_root.resolve() or run_dir.name == "archive":
            raise ValueError("Only direct runtime run directories can be archived")
        archive_root = self.runtime_root / "archive"
        archive_root.mkdir(parents=True, exist_ok=True)
        dest = archive_root / run_dir.name
        if dest.exists():
            raise FileExistsError(f"Archived run already exists: {dest}")
        shutil.move(str(run_dir), str(dest))
        return dest

    def cleanup_failed_partial(self, run_dir: Path, keep_logs: bool = True) -> None:
        """On failure keep status + configs; drop transient LEAN copies only."""
        if not keep_logs:
            run_dir = self.assert_path_inside_runtime(run_dir, self.runtime_root)
            if run_dir.parent != self.runtime_root.resolve() or run_dir.name == "archive":
                raise ValueError("Only direct runtime run directories can be cleaned up")
            shutil.rmtree(run_dir, ignore_errors=True)

    @staticmethod
    def assert_path_inside_runtime(path: Path, runtime_root: Path) -> Path:
        resolved = path.resolve()
        root = runtime_root.resolve()
        if root not in resolved.parents and resolved != root:
            raise ValueError(f"Path escapes runtime root: {resolved}")
        return resolved

    @staticmethod
    def project_relative(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(PROJECT_ROOT))
        except ValueError:
            return str(path.resolve())
