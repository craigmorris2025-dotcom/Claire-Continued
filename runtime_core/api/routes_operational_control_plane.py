from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from runtime_core.dashboard.operational_control_plane import (
    build_operational_control_plane,
    lifecycle_registry_payload,
    route_health,
    source_lineage_status,
    threshold_provenance_payload,
    update_plan,
    update_status,
)
from runtime_core.platform.intelligence_modes import build_intelligence_mode_state
from runtime_core.platform.operational_readiness import build_operational_readiness
from runtime_core.api.routes_continuous_runtime import read_json, CONTINUOUS_DIR


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


@router.get("/api/intelligence/modes")
def api_intelligence_modes() -> dict[str, Any]:
    return build_intelligence_mode_state()


@router.get("/api/operational/readiness")
def api_operational_readiness() -> dict[str, Any]:
    return build_operational_readiness()


@router.get("/api/governed/runtime-spine")
def api_governed_runtime_spine() -> dict[str, Any]:
    current = read_json(CONTINUOUS_DIR / "current_run.json", {})
    return {
        "schema_version": "claire_governed_runtime_spine_v1",
        "status": "ready" if current else "empty",
        "runtime_truth_write": "blocked",
        "operator_review_required": True,
        "run_id": current.get("run_id"),
        "route_selected": current.get("route_selected"),
        "stage_count": len(current.get("stage_status", [])) if isinstance(current.get("stage_status"), list) else 0,
        "quality_gate": current.get("quality_gate", {}),
        "authority": current.get("authority", {}),
        "current_run": current,
    }


@router.get("/api/update/status")
def api_update_status() -> dict[str, Any]:
    return update_status()


@router.get("/api/platform/update/plan")
def api_platform_update_plan() -> dict[str, Any]:
    return update_plan()


def include_operational_control_plane_routes(app: Any) -> None:
    app.include_router(router)
