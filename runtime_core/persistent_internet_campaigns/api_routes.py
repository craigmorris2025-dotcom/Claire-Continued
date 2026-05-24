from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import PersistentInternetCampaignService


router = APIRouter(prefix="/internet/campaigns", tags=["Persistent Internet Campaigns"])


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    urls: Optional[List[str]] = None
    cadence: str = "manual"
    max_results: int = Field(default=5, ge=1, le=20)
    notes: Optional[List[str]] = None


@router.post("")
def create_campaign(request: CreateCampaignRequest):
    service = PersistentInternetCampaignService()
    try:
        return service.create_campaign(
            name=request.name,
            query=request.query,
            urls=request.urls,
            cadence=request.cadence,
            max_results=request.max_results,
            notes=request.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("")
def list_campaigns():
    service = PersistentInternetCampaignService()
    return {"campaigns": service.list_campaigns()}


@router.post("/{campaign_id}/refresh")
async def refresh_campaign(campaign_id: str):
    service = PersistentInternetCampaignService()
    try:
        return await service.refresh_campaign(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{campaign_id}/reports")
def list_campaign_reports(campaign_id: str):
    service = PersistentInternetCampaignService()
    return {"reports": service.list_reports(campaign_id=campaign_id)}
