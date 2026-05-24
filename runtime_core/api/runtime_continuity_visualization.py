from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


RUNTIME_CONTINUITY_VERSION = "v19.89.8-S23"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_runtime_continuity(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    timeline = payload.get("governed_runtime_timeline") if isinstance(payload.get("governed_runtime_timeline"), dict) else {}
    overlay = payload.get("governed_route_activity_overlay") if isinstance(payload.get("governed_route_activity_overlay"), dict) else {}
    presence = payload.get("continuous_runtime_presence") if isinstance(payload.get("continuous_runtime_presence"), dict) else {}
    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}

    timeline_summary = timeline.get("summary") if isinstance(timeline.get("summary"), dict) else {}
    overlay_summary = overlay.get("summary") if isinstance(overlay.get("summary"), dict) else {}
    presence_summary = presence.get("summary") if isinstance(presence.get("summary"), dict) else {}
    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}

    events = timeline.get("events") if isinstance(timeline.get("events"), list) else []
    route_counts = overlay_summary.get("state_counts") if isinstance(overlay_summary.get("state_counts"), dict) else {}

    degraded_routes = int(route_counts.get("degraded", 0) or 0)
    recovering_routes = int(route_counts.get("recovering", 0) or 0)
    evidence_total = int(evidence_summary.get("evidence_total", 0) or 0)

    continuity_state = "continuous"
    if degraded_routes:
        continuity_state = "degraded"
    elif recovering_routes:
        continuity_state = "recovering"
    elif not events and evidence_total == 0:
        continuity_state = "initializing"

    chain = [
        {
            "node": "timeline",
            "state": "available" if timeline else "missing",
            "detail": timeline_summary.get("last_terminal_state", "unknown"),
        },
        {
            "node": "route_activity",
            "state": "available" if overlay else "missing",
            "detail": overlay_summary.get("selected_route", "unknown"),
        },
        {
            "node": "presence",
            "state": presence.get("presence_state", "missing") if presence else "missing",
            "detail": presence_summary.get("last_payload_freshness", "unknown"),
        },
        {
            "node": "evidence",
            "state": "available" if evidence else "missing",
            "detail": f"{evidence_total} items",
        },
    ]

    return {
        "version": RUNTIME_CONTINUITY_VERSION,
        "status": "active",
        "continuity_state": continuity_state,
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
            "terminal_state": timeline_summary.get("last_terminal_state", "unknown"),
            "presence_state": presence.get("presence_state", "unknown"),
            "timeline_event_total": len(events),
            "evidence_total": evidence_total,
            "degraded_routes": degraded_routes,
            "recovering_routes": recovering_routes,
            "payload_freshness": timeline_summary.get("last_payload_freshness", presence_summary.get("last_payload_freshness", "unknown")),
        },
        "continuity_chain": chain,
    }


def attach_runtime_continuity(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["runtime_continuity_visualization"] = build_runtime_continuity(payload)
    return payload
