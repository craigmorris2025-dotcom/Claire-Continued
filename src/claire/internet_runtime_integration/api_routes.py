from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .integration_service import InternetRuntimeIntegrationService


router = APIRouter(prefix="/runtime/internet", tags=["Internet Runtime Integration"])


class RuntimeInternetRequest(BaseModel):
    query: str = Field(..., min_length=1)
    run_id: str = Field(..., min_length=1)
    lifecycle_stage: str = "research"
    urls: Optional[List[str]] = None
    max_results: Optional[int] = Field(default=None, ge=1, le=20)
    core_output_path: Optional[str] = None


@router.post("/enrich")
async def enrich_runtime_with_internet(request: RuntimeInternetRequest):
    service = InternetRuntimeIntegrationService()
    try:
        path = Path(request.core_output_path) if request.core_output_path else None
        return await service.run_and_build_dashboard(query=request.query, run_id=request.run_id, lifecycle_stage=request.lifecycle_stage, urls=request.urls, max_results=request.max_results, core_output_path=path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dashboard")
async def build_runtime_internet_dashboard(request: RuntimeInternetRequest):
    service = InternetRuntimeIntegrationService()
    result = await service.run_and_build_dashboard(query=request.query, run_id=request.run_id, lifecycle_stage=request.lifecycle_stage, urls=request.urls, max_results=request.max_results)
    return result["dashboard_payload"]
