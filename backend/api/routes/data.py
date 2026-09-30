from __future__ import annotations

from fastapi import APIRouter

from backend.config import ALLOWED_SYMBOLS, DATA_DIR
from backend.models.schemas import SymbolInfo

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/symbols", response_model=list[SymbolInfo])
def list_symbols() -> list[SymbolInfo]:
    daily = DATA_DIR / "equity" / "india" / "daily"
    items: list[SymbolInfo] = []
    for symbol in sorted(ALLOWED_SYMBOLS):
        zip_path = daily / f"{symbol.lower()}.zip"
        items.append(
            SymbolInfo(
                symbol=symbol,
                ticker=symbol.replace(".NS", ""),
                inLeanFormat=zip_path.is_file(),
                zipPath=str(zip_path) if zip_path.is_file() else None,
            )
        )
    return items