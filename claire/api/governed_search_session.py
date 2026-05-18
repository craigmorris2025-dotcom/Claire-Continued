from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


SEARCH_SESSION_VERSION = "v19.89.8-S21"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_governed_search_session(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    route_overlay = payload.get("governed_route_activity_overlay") if isinstance(payload.get("governed_route_activity_overlay"), dict) else {}
    presence = payload.get("continuous_runtime_presence") if isinstance(payload.get("continuous_runtime_presence"), dict) else {}

    overlay_summary = route_overlay.get("summary") if isinstance(route_overlay.get("summary"), dict) else {}
    presence_summary = presence.get("summary") if isinstance(presence.get("summary"), dict) else {}

    routes = route_overlay.get("routes") if isinstance(route_overlay.get("routes"), list) else []
    search_route = next(
        (route for route in routes if isinstance(route, dict) and route.get("route") == "governed_search"),
        {},
    )

    search_state = search_route.get("state", "inactive")
    if search_state == "degraded":
        session_state = "degraded"
    elif search_state in {"active", "recovering"}:
        session_state = search_state
    else:
        session_state = "available"

    return {
        "version": SEARCH_SESSION_VERSION,
        "status": "active",
        "session_state": session_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
            "live_search_execution": "blocked_from_cockpit",
        },
        "summary": {
            "selected_route": overlay_summary.get("selected_route", "unknown"),
            "presence_state": presence.get("presence_state", "unknown"),
            "active_routes": presence_summary.get("active_routes", 0),
            "search_route_state": search_state,
            "search_owned_surfaces": search_route.get("owned_surface_count", 0),
            "last_payload_freshness": presence_summary.get("last_payload_freshness", "unknown"),
        },
        "session_controls": {
            "query_entry_visible": True,
            "execution_authority": "blocked",
            "manual_review_required": True,
            "evidence_promotion_required": True,
            "automatic_runtime_mutation": False,
        },
    }


def attach_governed_search_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_search_session"] = build_governed_search_session(payload)
    return payload
