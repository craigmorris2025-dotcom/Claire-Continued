"""
Acquirer Routes — GET /acquirers, GET /acquirers/{ticker}
"""

from fastapi import APIRouter, HTTPException

# ✅ FIXED IMPORTS
from claire.api.schemas import AcquirersResponse, AcquirerProfile
from claire.core.data_engine import DataEngine


router = APIRouter(tags=["acquirers"])
engine = DataEngine()


@router.get("/acquirers", response_model=AcquirersResponse)
async def list_acquirers(sector: str = None):
    """List all strategic acquirer profiles, optionally filtered by sector."""

    profiles = engine.query(sector=sector)
    acquirers = []

    for p in profiles:
        acquirers.append(
            AcquirerProfile(
                name=p.get("name", ""),
                ticker=p.get("ticker", ""),
                sector=p.get("sector", ""),
                fit=p.get("fit", 0),
                capacity=p.get("capacity", 0),
                strategy_alignment=p.get("strategy_alignment", 0),
                tech_alignment=p.get("tech_alignment", 0),
                focus=p.get("focus", []),
            )
        )

    return AcquirersResponse(
        acquirers=acquirers,
        count=len(acquirers)
    )


@router.get("/acquirers/{ticker}")
async def get_acquirer(ticker: str):
    """Get a single acquirer profile by ticker."""

    profiles = engine.query()

    match = [
        p for p in profiles
        if p.get("ticker", "").upper() == ticker.upper()
    ]

    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Acquirer {ticker} not found"
        )

    return match[0]
