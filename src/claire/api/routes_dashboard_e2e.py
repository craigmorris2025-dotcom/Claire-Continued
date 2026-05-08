"""FastAPI routes for v17.51 dashboard end-to-end first-use verification."""
from __future__ import annotations

from typing import Any, Dict

try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - tests can import module without FastAPI installed
    APIRouter = None  # type: ignore

from claire.runtime.dashboard_e2e_first_use import (
    dashboard_e2e_capability_manifest,
    read_latest_dashboard_e2e_result,
    run_dashboard_e2e_first_use,
)

if APIRouter is not None:
    router = APIRouter(prefix="/dashboard/e2e", tags=["dashboard-e2e"])

    @router.get("/first-use/manifest")
    def get_dashboard_e2e_manifest() -> Dict[str, Any]:
        return dashboard_e2e_capability_manifest()

    @router.get("/first-use/latest")
    def get_dashboard_e2e_latest() -> Dict[str, Any]:
        return read_latest_dashboard_e2e_result()

    @router.post("/first-use/run")
    def post_dashboard_e2e_run(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return run_dashboard_e2e_first_use(payload or {}).to_dict()
else:
    router = None
