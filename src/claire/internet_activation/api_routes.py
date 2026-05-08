from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import InternetResearchService

router = APIRouter(prefix="/research", tags=["Internet Research"])


class InternetResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    urls: Optional[List[str]] = None
    max_results: Optional[int] = Field(default=None, ge=1, le=20)


@router.post("/internet")
async def research_internet(request: InternetResearchRequest):
    service = InternetResearchService()
    try:
        return await service.research(request.query, request.urls, request.max_results)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/internet/evidence")
def list_internet_evidence(limit: int = 50):
    return {"evidence": InternetResearchService().list_evidence(limit)}


@router.get("/internet/evidence/{evidence_id}")
def get_internet_evidence(evidence_id: str):
    record = InternetResearchService().get_evidence(evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return record
