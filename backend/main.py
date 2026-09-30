from __future__ import annotations

import sys
from pathlib import Path

# Allow `uvicorn backend.main:app` from project root
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import backtest, data, strategies

app = FastAPI(
    title="Indian Trading System API",
    description="Phase 3 orchestration layer over existing LEAN backtesting runners.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies.router)
app.include_router(data.router)
app.include_router(backtest.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "phase": 3}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "Request validation failed.",
            "details": {"errors": jsonable_encoder(exc.errors())},
        },
    )