"""Pydantic request/response models for the Phase 3 API."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class BacktestConfigRequest(BaseModel):
    strategy: str
    symbols: list[str] = Field(min_length=1)
    startDate: str
    endDate: str
    startingCapital: float = Field(gt=0)
    brokerage: str = "zerodha"
    fastPeriod: int = Field(ge=2, le=250)
    slowPeriod: int = Field(ge=3, le=500)
    positionWeight: float = Field(gt=0, le=1.0)

    @field_validator("startDate", "endDate")
    @classmethod
    def validate_iso_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"Date must be YYYY-MM-DD, got '{v}'") from exc
        return v

    @model_validator(mode="after")
    def validate_ranges(self) -> "BacktestConfigRequest":
        if self.startDate > self.endDate:
            raise ValueError("startDate must be on or before endDate")
        if self.fastPeriod >= self.slowPeriod:
            raise ValueError("fastPeriod must be strictly less than slowPeriod")
        if len(self.symbols) != len(set(self.symbols)):
            raise ValueError("symbols must not contain duplicates")
        if not math.isfinite(self.startingCapital) or not math.isfinite(self.positionWeight):
            raise ValueError("startingCapital and positionWeight must be finite numbers")
        if self.strategy == "wipro_sma" and self.symbols != ["WIPRO.NS"]:
            raise ValueError("wipro_sma requires exactly the WIPRO.NS symbol")
        if self.strategy == "sma_crossover" and "WIPRO.NS" in self.symbols:
            raise ValueError("sma_crossover does not support WIPRO.NS")
        return self


class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class StrategyInfo(BaseModel):
    id: str
    name: str
    className: str
    filePath: str
    universeType: str
    defaultSymbols: list[str]
    description: str
    supported: bool


class SymbolInfo(BaseModel):
    symbol: str
    ticker: str
    inLeanFormat: bool
    zipPath: Optional[str] = None


class BacktestRunResponse(BaseModel):
    runId: str
    status: Literal[
        "queued",
        "running",
        "completed",
        "failed",
        "timeout",
    ]
    strategy: str
    message: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    durationSeconds: Optional[float] = None
    processId: Optional[int] = None
    exitCode: Optional[int] = None
    resultLocation: Optional[str] = None
    summaryPath: Optional[str] = None
    statistics: Optional[dict[str, str]] = None
    error: Optional[ApiError] = None
    runtimeConfigPath: Optional[str] = None


class BacktestStatusResponse(BacktestRunResponse):
    """Phase-4-ready status shape (also returned after sync run)."""
    pass
