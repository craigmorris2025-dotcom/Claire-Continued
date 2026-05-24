from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import GovernedCampaignSchedulerService


router = APIRouter(prefix="/internet/scheduler", tags=["Governed Campaign Scheduler"])


class SetScheduleRequest(BaseModel):
    campaign_id: str = Field(..., min_length=1)
    cadence_minutes: int = Field(default=1440, ge=1)
    enabled: bool = True
    max_results: Optional[int] = None


@router.post("/schedule")
def set_schedule(request: SetScheduleRequest):
    service = GovernedCampaignSchedulerService()
    try:
        return service.set_schedule(
            campaign_id=request.campaign_id,
            cadence_minutes=request.cadence_minutes,
            enabled=request.enabled,
            max_results=request.max_results,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/schedules")
def list_schedules():
    service = GovernedCampaignSchedulerService()
    return {"schedules": service.list_schedules()}


@router.post("/run-due")
async def run_due(limit: Optional[int] = None):
    service = GovernedCampaignSchedulerService()
    return await service.run_due_once(limit=limit)


@router.get("/reports")
def list_reports(limit: int = 25):
    service = GovernedCampaignSchedulerService()
    return {"reports": service.list_reports(limit=limit)}


@router.get("/lock")
def lock_status():
    service = GovernedCampaignSchedulerService()
    return service.lock_status()
