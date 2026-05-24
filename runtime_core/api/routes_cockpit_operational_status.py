from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Request


router = APIRouter(tags=["Cockpit Operational Status"])


CANONICAL_ENDPOINTS = {
    "backend": "/health",
    "payload": "/dashboard/payload/status",
    "continuous_runtime": "/runtime/continuous/status",
    "governed_search": "/api/dashboard/search/provider/status",
}


def _mounted_paths(request: Request) -> set[str]:
    paths: set[str] = set()
    for route in getattr(request.app, "routes", []):
        path = getattr(route, "path", None)
        if path:
            paths.add(str(path))
    return paths


def build_operational_status(request: Request) -> Dict[str, Any]:
    mounted = _mounted_paths(request)
    services: Dict[str, Any] = {}

    for name, path in CANONICAL_ENDPOINTS.items():
        services[name] = {
            "status": "online" if path in mounted else "unavailable",
            "canonical_endpoint": path,
            "mounted": path in mounted,
            "source": "backend_route_mount_truth",
        }

    all_online = all(item["mounted"] for item in services.values())

    return {
        "status": "online" if all_online else "degraded",
        "all_required_mounted": all_online,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "runtime_truth_mutated": False,
        "live_internet_enabled": False,
        "services": services,
    }


@router.get("/api/cockpit/operational-status")
def api_cockpit_operational_status(request: Request) -> Dict[str, Any]:
    return build_operational_status(request)


@router.get("/cockpit/operational-status")
def cockpit_operational_status(request: Request) -> Dict[str, Any]:
    return build_operational_status(request)
