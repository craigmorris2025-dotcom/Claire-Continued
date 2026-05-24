from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


BROWSER_SESSION_VERSION = "v19.89.8-S26"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_browser_session_persistence(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    loop = payload.get("continuous_browser_runtime_loop") if isinstance(payload.get("continuous_browser_runtime_loop"), dict) else {}
    continuity = payload.get("runtime_continuity_visualization") if isinstance(payload.get("runtime_continuity_visualization"), dict) else {}
    workflow = payload.get("governed_operator_workflow") if isinstance(payload.get("governed_operator_workflow"), dict) else {}
    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}

    loop_summary = loop.get("summary") if isinstance(loop.get("summary"), dict) else {}
    continuity_summary = continuity.get("summary") if isinstance(continuity.get("summary"), dict) else {}
    workflow_summary = workflow.get("summary") if isinstance(workflow.get("summary"), dict) else {}
    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}

    selected_route = (
        loop_summary.get("selected_route")
        or continuity_summary.get("selected_route")
        or "unknown"
    )

    return {
        "version": BROWSER_SESSION_VERSION,
        "status": "active",
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "browser_storage": "presentation_state_only",
            "runtime_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "session_snapshot": {
            "selected_route": selected_route,
            "loop_state": loop.get("loop_state", "unknown"),
            "continuity_state": continuity.get("continuity_state", "unknown"),
            "workflow_total": workflow_summary.get("workflow_total", 0),
            "manual_review_required": workflow_summary.get("manual_review_required", False),
            "evidence_total": evidence_summary.get("evidence_total", 0),
            "payload_freshness": loop_summary.get("payload_freshness", continuity_summary.get("payload_freshness", "unknown")),
        },
        "persistence_policy": {
            "storage_scope": "browser_local_storage",
            "contains_runtime_truth": False,
            "contains_credentials": False,
            "contains_live_execution_state": False,
            "restore_behavior": "display_last_observed_session_only",
            "write_back_to_runtime": False,
        },
    }


def attach_browser_session_persistence(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["canonical_browser_session_persistence"] = build_browser_session_persistence(payload)
    return payload
