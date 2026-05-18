from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request


router = APIRouter(tags=["cockpit-operational-proof"])

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
    "operational_proof_status": "/api/operational-proof/status",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _payload(request: Request) -> dict[str, Any]:
    mounted = {getattr(route, "path", "") for route in request.app.routes}

    surfaces = {
        name: {
            "path": path,
            "mounted": path in mounted,
            "ok": path in mounted,
        }
        for name, path in REQUIRED_SURFACES.items()
    }

    missing = [item["path"] for item in surfaces.values() if not item["mounted"]]
    ready = len(missing) == 0

    return {
        "surface": "cockpit_operational_proof_binding",
        "version": "19.88.6",
        "timestamp_utc": _now(),
        "status": "bound_ready_fail_closed" if ready else "bound_degraded",
        "ok": ready,
        "source_of_truth": "/api/operational-proof/status",
        "presentation_aliases": [
            "/api/cockpit/operational-proof",
            "/cockpit/operational-proof",
        ],
        "mounted_route_count": len(mounted),
        "required_surface_count": len(REQUIRED_SURFACES),
        "missing_required_surfaces": missing,
        "surfaces": surfaces,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "creates_new_truth": False,
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


@router.get("/api/cockpit/operational-proof")
def api_cockpit_operational_proof(request: Request) -> dict[str, Any]:
    return _payload(request)


@router.get("/cockpit/operational-proof")
def cockpit_operational_proof(request: Request) -> dict[str, Any]:
    return _payload(request)
