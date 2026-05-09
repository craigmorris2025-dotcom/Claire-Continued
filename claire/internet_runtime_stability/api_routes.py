from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from .service import InternetRuntimeStabilityService


router = APIRouter(prefix="/internet/stability", tags=["Internet Runtime Stability"])


@router.get("/health")
def health():
    service = InternetRuntimeStabilityService()
    return service.health()


@router.post("/campaigns/{campaign_id}/refresh")
async def refresh_campaign_with_recovery(campaign_id: str):
    service = InternetRuntimeStabilityService()
    return await service.refresh_campaign_with_recovery(campaign_id)


@router.post("/scheduler/run-due")
async def run_scheduler_due_with_recovery(limit: Optional[int] = None):
    service = InternetRuntimeStabilityService()
    return await service.run_scheduler_due_with_recovery(limit=limit)


@router.get("/failures")
def failures(limit: int = 50):
    service = InternetRuntimeStabilityService()
    return {"failures": service.list_failures(limit=limit)}


@router.get("/reports")
def reports(limit: int = 25):
    service = InternetRuntimeStabilityService()
    return {"reports": service.list_reports(limit=limit)}
