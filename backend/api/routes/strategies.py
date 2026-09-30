from __future__ import annotations

from fastapi import APIRouter

from backend.config import STRATEGY_CATALOG
from backend.models.schemas import StrategyInfo

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyInfo])
def list_strategies() -> list[StrategyInfo]:
    return [StrategyInfo(**meta) for meta in STRATEGY_CATALOG.values()]