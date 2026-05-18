from __future__ import annotations

from typing import Any, Dict, List


SURFACE_REGISTRY_VERSION = "v19.89.8-S17"


CANONICAL_COCKPIT_SURFACES: List[Dict[str, Any]] = [
    {
        "surface_id": "main_result",
        "label": "Main Result",
        "payload_owner": "dashboard_payload",
        "route_owner": "runtime",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "canonical_runtime_telemetry",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "runtime_surface",
        "label": "Runtime Surface",
        "payload_owner": "canonical_runtime_surface_model",
        "route_owner": "runtime",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "canonical_runtime_telemetry",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "operator_timeline",
        "label": "Governed Timeline",
        "payload_owner": "governed_runtime_timeline",
        "route_owner": "governed_runtime_timeline",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "governed_monitoring",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "event_stream",
        "label": "Runtime Event Stream",
        "payload_owner": "canonical_runtime_event_stream",
        "route_owner": "runtime_event_stream",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "governed_runtime_telemetry",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "source_surfaces",
        "label": "Source Surfaces",
        "payload_owner": "file_origin_canonical_api_bridge",
        "route_owner": "source_registry",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "source_lineage",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "search_surface",
        "label": "Governed Search Surface",
        "payload_owner": "governed_search_payload",
        "route_owner": "governed_search",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "governed_web_telemetry",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "portfolio_surface",
        "label": "Portfolio Intelligence",
        "payload_owner": "route_specific_outputs",
        "route_owner": "portfolio",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "runtime_route_telemetry",
        "visibility": "available",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "breakthrough_surface",
        "label": "Breakthrough Escalation",
        "payload_owner": "route_specific_outputs",
        "route_owner": "breakthrough",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "runtime_route_telemetry",
        "visibility": "available",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "design_surface",
        "label": "Design Portal",
        "payload_owner": "route_specific_outputs",
        "route_owner": "design",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "runtime_route_telemetry",
        "visibility": "available",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
    {
        "surface_id": "acquisition_surface",
        "label": "Acquisition Package",
        "payload_owner": "route_specific_outputs",
        "route_owner": "acquisition",
        "sidebar_owner": "canonical_sidebar",
        "telemetry_owner": "runtime_route_telemetry",
        "visibility": "available",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    },
]


def build_cockpit_surface_registry() -> Dict[str, Any]:
    ids = [item["surface_id"] for item in CANONICAL_COCKPIT_SURFACES]
    duplicates = sorted({surface_id for surface_id in ids if ids.count(surface_id) > 1})
    missing_authority_locks = [
        item["surface_id"]
        for item in CANONICAL_COCKPIT_SURFACES
        if item.get("runtime_authority") != "blocked"
    ]

    return {
        "version": SURFACE_REGISTRY_VERSION,
        "status": "active",
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "surface_total": len(CANONICAL_COCKPIT_SURFACES),
            "duplicate_surface_ids": duplicates,
            "missing_authority_locks": missing_authority_locks,
            "registry_health": "healthy" if not duplicates and not missing_authority_locks else "degraded",
        },
        "surfaces": CANONICAL_COCKPIT_SURFACES,
    }


def attach_cockpit_surface_registry(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["canonical_cockpit_surface_registry"] = build_cockpit_surface_registry()
    return payload


def register_cockpit_surface_registry_routes(app: Any) -> None:
    try:
        from fastapi import APIRouter
    except Exception:
        return

    router = APIRouter(prefix="/api/cockpit", tags=["Canonical Cockpit Surface Registry"])

    @router.get("/surface-registry")
    def get_surface_registry() -> Dict[str, Any]:
        return build_cockpit_surface_registry()

    @router.get("/surface-registry/status")
    def get_surface_registry_status() -> Dict[str, Any]:
        registry = build_cockpit_surface_registry()
        return {
            "version": registry["version"],
            "status": registry["status"],
            "runtime_authority": "blocked",
            "presentation_only": True,
            "surface_total": registry["summary"]["surface_total"],
            "registry_health": registry["summary"]["registry_health"],
            "duplicate_surface_ids": registry["summary"]["duplicate_surface_ids"],
        }

    app.include_router(router)
