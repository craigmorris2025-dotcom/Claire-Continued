from __future__ import annotations

from typing import Any, Dict, List


ROUTE_OVERLAY_VERSION = "v19.89.8-S19"

CANONICAL_ROUTES = [
    "runtime",
    "discovery",
    "portfolio",
    "breakthrough",
    "design",
    "acquisition",
    "governed_search",
    "source_registry",
    "runtime_event_stream",
    "governed_runtime_timeline",
]


def _route_status(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    runtime = payload.get("runtime") if isinstance(payload.get("runtime"), dict) else {}
    timeline = payload.get("governed_runtime_timeline") if isinstance(payload.get("governed_runtime_timeline"), dict) else {}
    health = payload.get("canonical_cockpit_surface_health") if isinstance(payload.get("canonical_cockpit_surface_health"), dict) else {}
    registry = payload.get("canonical_cockpit_surface_registry") if isinstance(payload.get("canonical_cockpit_surface_registry"), dict) else {}

    selected_route = runtime.get("route") or runtime.get("selected_route") or payload.get("route") or "unknown"
    terminal_state = runtime.get("terminal_state") or payload.get("terminal_state") or "unknown"

    health_state = health.get("health", "unknown")
    issue_total = 0
    if isinstance(health.get("summary"), dict):
        issue_total = int(health["summary"].get("issue_total", 0) or 0)

    surfaces = registry.get("surfaces") if isinstance(registry.get("surfaces"), list) else []
    owned_surfaces = [
        surface for surface in surfaces
        if isinstance(surface, dict) and surface.get("route_owner") == route
    ]

    timeline_summary = timeline.get("summary") if isinstance(timeline.get("summary"), dict) else {}
    freshness = timeline_summary.get("last_payload_freshness", "unknown")
    connection_state = timeline_summary.get("last_connection_state", "unknown")

    state = "inactive"
    if route == selected_route or any(surface.get("visibility") == "active" for surface in owned_surfaces):
        state = "active"
    if health_state in {"degraded", "blocked"} or issue_total:
        state = "degraded"
    if connection_state in {"recovering", "recovered"} or freshness == "fresh":
        if state == "degraded":
            state = "recovering"

    return {
        "route": route,
        "state": state,
        "selected": route == selected_route,
        "terminal_state": terminal_state if route == selected_route else "not_selected",
        "owned_surface_count": len(owned_surfaces),
        "freshness": freshness,
        "connection_state": connection_state,
        "health": health_state,
        "issue_total": issue_total,
        "runtime_authority": "blocked",
        "presentation_only": True,
    }


def build_governed_route_activity_overlay(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    routes = [_route_status(route, payload) for route in CANONICAL_ROUTES]

    counts: Dict[str, int] = {}
    for route in routes:
        key = route["state"]
        counts[key] = counts.get(key, 0) + 1

    return {
        "version": ROUTE_OVERLAY_VERSION,
        "status": "active",
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "route_total": len(routes),
            "state_counts": counts,
            "selected_route": next((route["route"] for route in routes if route["selected"]), "unknown"),
        },
        "routes": routes,
    }


def attach_route_activity_overlay(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_route_activity_overlay"] = build_governed_route_activity_overlay(payload)
    return payload


def register_route_activity_overlay_routes(app: Any) -> None:
    try:
        from fastapi import APIRouter
    except Exception:
        return

    router = APIRouter(prefix="/api/cockpit", tags=["Governed Route Activity Overlay"])

    @router.get("/route-activity")
    def get_route_activity() -> Dict[str, Any]:
        return build_governed_route_activity_overlay({})

    @router.get("/route-activity/status")
    def get_route_activity_status() -> Dict[str, Any]:
        overlay = build_governed_route_activity_overlay({})
        return {
            "version": overlay["version"],
            "status": overlay["status"],
            "runtime_authority": "blocked",
            "presentation_only": True,
            "route_total": overlay["summary"]["route_total"],
            "selected_route": overlay["summary"]["selected_route"],
        }

    app.include_router(router)
