"""
FastAPI routes for browsing Claire export runs.

Manual registration option in your FastAPI app:

    from backend.routes.export_browser import router as export_browser_router
    app.include_router(export_browser_router)

These routes are intentionally thin wrappers around Claire runtime modules.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from claire.runtime.export_browser import ExportBrowser
from claire.runtime.run_history import RunHistory


router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/summary")
def export_summary():
    return ExportBrowser().summary()


@router.get("/runs")
def list_export_runs(limit: int = Query(50, ge=1, le=500), rescan_if_empty: bool = True):
    return ExportBrowser().list_runs(limit=limit, rescan_if_empty=rescan_if_empty)


@router.post("/runs/rescan")
def rescan_export_runs():
    return RunHistory().rescan_exports("exports")


@router.get("/runs/{run_id}")
def get_export_run(run_id: str):
    result = ExportBrowser().get_run(run_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result)
    return result


@router.get("/runs/{run_id}/files")
def list_export_files(run_id: str):
    result = ExportBrowser().list_files(run_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result)
    return result


@router.get("/runs/{run_id}/files/{filename}", response_class=PlainTextResponse)
def read_export_file(run_id: str, filename: str, max_chars: int = Query(0, ge=0, le=2000000)):
    result = ExportBrowser().read_file(run_id, filename, max_chars=max_chars or None)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result)
    return result.get("content", "")
