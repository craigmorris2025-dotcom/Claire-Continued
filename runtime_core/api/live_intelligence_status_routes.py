from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request


router = APIRouter(prefix="/api/live-intelligence", tags=["live-intelligence"])

DEPENDENCY_PATHS = [
    "/health",
    "/dashboard/payload/status",
    "/runtime/continuous/status",
    "/api/dashboard/search/provider/status",
    "/api/feeds/live-source-catalog/status",
    "/api/feeds/live-source-catalog/health",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/status")
def live_intelligence_status(request: Request) -> dict[str, Any]:
    mounted = {getattr(route, "path", "") for route in request.app.routes}
    dependencies = {
        path: {
            "mounted": path in mounted,
            "ok": path in mounted,
        }
        for path in DEPENDENCY_PATHS
    }

    all_core_ready = all(item["ok"] for item in dependencies.values())

    return {
        "surface": "live_intelligence_status",
        "version": "19.88.4",
        "timestamp_utc": _now(),
        "status": "ready_fail_closed" if all_core_ready else "degraded",
        "ok": all_core_ready,
        "live_execution_enabled": False,
        "runtime_truth_mutation": False,
        "speculative_outputs": False,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "dependencies": dependencies,
    }
