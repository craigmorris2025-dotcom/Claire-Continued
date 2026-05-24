from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


BROWSER_LOOP_VERSION = "v19.89.8-S24"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_continuous_browser_runtime_loop(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    continuity = payload.get("runtime_continuity_visualization") if isinstance(payload.get("runtime_continuity_visualization"), dict) else {}
    presence = payload.get("continuous_runtime_presence") if isinstance(payload.get("continuous_runtime_presence"), dict) else {}
    search = payload.get("governed_search_session") if isinstance(payload.get("governed_search_session"), dict) else {}

    continuity_summary = continuity.get("summary") if isinstance(continuity.get("summary"), dict) else {}
    presence_summary = presence.get("summary") if isinstance(presence.get("summary"), dict) else {}
    search_summary = search.get("summary") if isinstance(search.get("summary"), dict) else {}

    continuity_state = continuity.get("continuity_state", "unknown")
    presence_state = presence.get("presence_state", "unknown")
    search_state = search.get("session_state", "unknown")

    loop_state = "observing"
    if continuity_state == "degraded" or presence_state == "degraded" or search_state == "degraded":
        loop_state = "degraded_observation"
    elif continuity_state == "recovering" or presence_state == "recovering" or search_state == "recovering":
        loop_state = "recovery_observation"
    elif continuity_state == "continuous" and presence_state in {"active", "present"}:
        loop_state = "continuous_observation"

    return {
        "version": BROWSER_LOOP_VERSION,
        "status": "active",
        "loop_state": loop_state,
        "observed_at_utc": _utc_now(),
        "polling": {
            "canonical_payload_interval_ms": 10000,
            "mode": "observe_only",
            "writes_enabled": False,
            "runtime_mutation_enabled": False,
        },
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
            "browser_execution_authority": "blocked",
        },
        "summary": {
            "continuity_state": continuity_state,
            "presence_state": presence_state,
            "search_session_state": search_state,
            "selected_route": continuity_summary.get("selected_route", search_summary.get("selected_route", "unknown")),
            "payload_freshness": continuity_summary.get("payload_freshness", presence_summary.get("last_payload_freshness", "unknown")),
            "evidence_total": continuity_summary.get("evidence_total", 0),
        },
    }


def attach_continuous_browser_runtime_loop(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["continuous_browser_runtime_loop"] = build_continuous_browser_runtime_loop(payload)
    return payload
