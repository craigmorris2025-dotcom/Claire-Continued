from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .service import InternetOperationsDashboardService
from .static_page import DASHBOARD_HTML


router = APIRouter(prefix="/internet/ops", tags=["Internet Operations Dashboard"])


@router.get("/snapshot")
def snapshot():
    service = InternetOperationsDashboardService()
    return service.snapshot()


@router.post("/run-due")
async def run_due(limit: Optional[int] = None):
    service = InternetOperationsDashboardService()
    return await service.run_due_and_snapshot(limit=limit)


@router.post("/campaigns/{campaign_id}/refresh")
async def refresh_campaign(campaign_id: str):
    service = InternetOperationsDashboardService()
    return await service.refresh_campaign_and_snapshot(campaign_id)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return DASHBOARD_HTML
