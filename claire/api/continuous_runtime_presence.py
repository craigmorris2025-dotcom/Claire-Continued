from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


PRESENCE_VERSION = "v19.89.8-S20"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _value(payload: Dict[str, Any], *keys: str, default: str = "unknown") -> str:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    if current is None or current == "":
        return default
    return str(current)


def build_continuous_runtime_presence(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    timeline = payload.get("governed_runtime_timeline") if isinstance(payload.get("governed_runtime_timeline"), dict) else {}
    route_overlay = payload.get("governed_route_activity_overlay") if isinstance(payload.get("governed_route_activity_overlay"), dict) else {}
    surface_health = payload.get("canonical_cockpit_surface_health") if isinstance(payload.get("canonical_cockpit_surface_health"), dict) else {}

    timeline_summary = timeline.get("summary") if isinstance(timeline.get("summary"), dict) else {}
    overlay_summary = route_overlay.get("summary") if isinstance(route_overlay.get("summary"), dict) else {}
    health_summary = surface_health.get("summary") if isinstance(surface_health.get("summary"), dict) else {}

    route_state_counts = overlay_summary.get("state_counts") if isinstance(overlay_summary.get("state_counts"), dict) else {}

    issue_total = int(health_summary.get("issue_total", 0) or 0)
    degraded_routes = int(route_state_counts.get("degraded", 0) or 0)
    recovering_routes = int(route_state_counts.get("recovering", 0) or 0)
    active_routes = int(route_state_counts.get("active", 0) or 0)

    presence_state = "present"
    if issue_total or degraded_routes:
        presence_state = "degraded"
    elif recovering_routes:
        presence_state = "recovering"
    elif active_routes:
        presence_state = "active"

    return {
        "version": PRESENCE_VERSION,
        "status": "active",
        "presence_state": presence_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "selected_route": overlay_summary.get("selected_route", "unknown"),
            "active_routes": active_routes,
            "degraded_routes": degraded_routes,
            "recovering_routes": recovering_routes,
            "surface_issue_total": issue_total,
            "last_payload_freshness": timeline_summary.get("last_payload_freshness", "unknown"),
            "last_connection_state": timeline_summary.get("last_connection_state", "unknown"),
        },
        "signals": {
            "timeline_available": bool(timeline),
            "route_overlay_available": bool(route_overlay),
            "surface_health_available": bool(surface_health),
        },
    }


def attach_continuous_runtime_presence(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["continuous_runtime_presence"] = build_continuous_runtime_presence(payload)
    return payload
