from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.schemas import BacktestConfigRequest, BacktestRunResponse
from backend.services.backtest_runner import BacktestRunner, BacktestRunnerError

router = APIRouter(prefix="/api/backtest", tags=["backtest"])
_runner = BacktestRunner()


@router.post("/run", response_model=BacktestRunResponse)
def run_backtest(payload: BacktestConfigRequest) -> BacktestRunResponse:
    """
    Synchronously execute a backtest via the existing LEAN launcher.
    Phase 4 will add async job monitoring on top of the same runner.
    """
    try:
        return _runner.run_sync(payload)
    except BacktestRunnerError as exc:
        raise HTTPException(
            status_code=409 if exc.code == "runner_busy" else 400,
            detail={"code": exc.code, "message": exc.message, "details": exc.details},
        ) from exc