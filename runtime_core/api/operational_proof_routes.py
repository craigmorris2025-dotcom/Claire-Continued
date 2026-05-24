from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request


router = APIRouter(prefix="/api/operational-proof", tags=["operational-proof"])

REQUIRED_SURFACES = {
    "core_health": "/health",
    "openapi": "/openapi.json",
    "dashboard_payload": "/dashboard/payload",
    "dashboard_payload_status": "/dashboard/payload/status",
    "continuous_runtime_status": "/runtime/continuous/status",
    "continuous_runtime_start": "/runtime/continuous/start",
    "continuous_review_queue": "/runtime/continuous/review-queue",
    "governed_search_provider_status": "/api/dashboard/search/provider/status",
    "governed_search_provider_probe": "/api/dashboard/search/provider/probe",
    "governed_search_live": "/api/dashboard/search/live",
    "governed_search_google_smoke": "/api/dashboard/search/smoke/google",
    "cockpit_operational_status": "/api/cockpit/operational-status",
    "live_source_catalog_status": "/api/feeds/live-source-catalog/status",
    "live_source_catalog_health": "/api/feeds/live-source-catalog/health",
    "live_intelligence_status": "/api/live-intelligence/status",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/status")
def operational_proof_status(request: Request) -> dict[str, Any]:
    mounted = {getattr(route, "path", "") for route in request.app.routes}

    surfaces = {
        name: {
            "path": path,
            "mounted": path in mounted,
            "ok": path in mounted,
        }
        for name, path in REQUIRED_SURFACES.items()
    }

    missing = [
        item["path"]
        for item in surfaces.values()
        if not item["mounted"]
    ]

    plateau_ready = len(missing) == 0

    return {
        "surface": "operational_proof_status",
        "version": "19.88.5",
        "timestamp_utc": _now(),
        "status": "plateau_ready_fail_closed" if plateau_ready else "degraded",
        "ok": plateau_ready,
        "mounted_route_count": len(mounted),
        "required_surface_count": len(REQUIRED_SURFACES),
        "missing_required_surfaces": missing,
        "surfaces": surfaces,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_over_ui_assumptions": True,
        "speculative_outputs": False,
        "runtime_truth_mutation": False,
        "uncontrolled_browsing_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "governance": {
            "fail_closed": True,
            "operator_review_required": True,
            "manual_probe_enable_required": True,
            "status_only": True,
        },
    }
