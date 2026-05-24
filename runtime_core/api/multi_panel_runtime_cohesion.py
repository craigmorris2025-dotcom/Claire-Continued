from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


COHESION_VERSION = "v19.89.8-S27"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


PANEL_KEYS = [
    ("governed_runtime_timeline", "timeline"),
    ("governed_route_activity_overlay", "route_activity"),
    ("continuous_runtime_presence", "presence"),
    ("governed_search_session", "search_session"),
    ("governed_evidence_basket", "evidence_basket"),
    ("runtime_continuity_visualization", "runtime_continuity"),
    ("continuous_browser_runtime_loop", "browser_loop"),
    ("governed_operator_workflow", "operator_workflow"),
    ("canonical_browser_session_persistence", "browser_session"),
]


def _panel_state(key: str, label: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    value = payload.get(key)
    available = isinstance(value, dict)

    authority = value.get("authority") if available and isinstance(value.get("authority"), dict) else {}
    summary = value.get("summary") if available and isinstance(value.get("summary"), dict) else {}

    runtime_authority = authority.get("runtime_authority", "blocked")
    autonomous_expansion = authority.get("autonomous_execution_expansion", False)

    state = "available" if available else "missing"
    if available and runtime_authority != "blocked":
        state = "authority_drift"
    elif available and autonomous_expansion is not False:
        state = "expansion_drift"

    return {
        "key": key,
        "label": label,
        "state": state,
        "available": available,
        "runtime_authority": runtime_authority,
        "autonomous_execution_expansion": autonomous_expansion,
        "selected_route": summary.get("selected_route", "unknown"),
        "payload_freshness": summary.get("payload_freshness", summary.get("last_payload_freshness", "unknown")),
    }


def build_multi_panel_runtime_cohesion(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    panels: List[Dict[str, Any]] = [_panel_state(key, label, payload) for key, label in PANEL_KEYS]

    missing = [panel for panel in panels if panel["state"] == "missing"]
    drift = [panel for panel in panels if panel["state"] in {"authority_drift", "expansion_drift"}]
    available = [panel for panel in panels if panel["available"]]

    selected_routes = sorted({
        panel.get("selected_route")
        for panel in panels
        if panel.get("selected_route") not in {None, "", "unknown"}
    })

    cohesion_state = "cohesive"
    if drift:
        cohesion_state = "blocked"
    elif missing:
        cohesion_state = "partial"
    elif len(selected_routes) > 1:
        cohesion_state = "route_inconsistent"

    return {
        "version": COHESION_VERSION,
        "status": "active",
        "cohesion_state": cohesion_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "runtime_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "panel_total": len(panels),
            "available_total": len(available),
            "missing_total": len(missing),
            "drift_total": len(drift),
            "selected_routes": selected_routes,
            "payload_propagation": "complete" if not missing else "partial",
            "runtime_cohesion": cohesion_state,
        },
        "panels": panels,
    }


def attach_multi_panel_runtime_cohesion(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["multi_panel_runtime_cohesion"] = build_multi_panel_runtime_cohesion(payload)
    return payload
