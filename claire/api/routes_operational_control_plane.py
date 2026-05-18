from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from claire.dashboard.operational_control_plane import (
    build_operational_control_plane,
    lifecycle_registry_payload,
    route_health,
    source_lineage_status,
    threshold_provenance_payload,
    update_plan,
    update_status,
)


router = APIRouter(tags=["Operational Control Plane"])


@router.get("/api/operational/control-plane")
def api_operational_control_plane(request: Request) -> dict[str, Any]:
    return build_operational_control_plane(request.app.routes)


@router.get("/api/operational/route-health")
def api_operational_route_health(request: Request) -> dict[str, Any]:
    return route_health(request.app.routes)


@router.get("/api/lifecycle/stage-registry")
def api_lifecycle_stage_registry() -> dict[str, Any]:
    return lifecycle_registry_payload()


@router.get("/api/lifecycle/threshold-provenance")
def api_lifecycle_threshold_provenance() -> dict[str, Any]:
    return threshold_provenance_payload()


@router.get("/api/source-lineage/status")
def api_source_lineage_status() -> dict[str, Any]:
    return source_lineage_status()


@router.get("/api/update/status")
def api_update_status() -> dict[str, Any]:
    return update_status()


@router.get("/api/platform/update/plan")
def api_platform_update_plan() -> dict[str, Any]:
    return update_plan()


def include_operational_control_plane_routes(app: Any) -> None:
    app.include_router(router)
