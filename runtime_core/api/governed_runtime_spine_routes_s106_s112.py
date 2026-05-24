from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from runtime_core.api.governed_runtime_spine_s106_s112 import (
    build_canonical_runtime_spine,
    build_lifecycle_authority_map,
    build_evidence_to_lifecycle_bridge,
    build_cockpit_operations_fetch_map,
    build_operator_control_read_model,
    build_governed_search_control_read_model,
    build_dashboard_managed_demo,
)

router = APIRouter(prefix="/api/governed/runtime-spine", tags=["governed-runtime-spine-s106-s112"])

@router.get("")
def get_runtime_spine() -> Dict[str, Any]:
    return build_canonical_runtime_spine()

@router.get("/authority-map")
def get_authority_map() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_lifecycle_authority_map(spine)

@router.get("/evidence-bridge")
def get_evidence_bridge() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_evidence_to_lifecycle_bridge(spine)

@router.get("/fetch-map")
def get_spine_fetch_map() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_cockpit_operations_fetch_map(spine)

@router.get("/operator-control")
def get_operator_control() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_operator_control_read_model(spine)

@router.get("/search-control")
def get_search_control() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_governed_search_control_read_model(spine)

@router.get("/dashboard-demo")
def get_dashboard_managed_demo() -> Dict[str, Any]:
    spine = build_canonical_runtime_spine()
    return build_dashboard_managed_demo(spine)

def include_governed_runtime_spine_routes(app: Any) -> Any:
    marker = "governed_runtime_spine_s106_s112_routes_included"
    if getattr(app.state, marker, False):
        return app
    app.include_router(router)
    setattr(app.state, marker, True)
    return app
