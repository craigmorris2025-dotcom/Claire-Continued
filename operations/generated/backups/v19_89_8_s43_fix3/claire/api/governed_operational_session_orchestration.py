from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


OPERATIONAL_SESSION_ORCHESTRATION_VERSION = "v19.89.8-S28"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_operational_session_orchestration(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    cohesion = payload.get("multi_panel_runtime_cohesion") if isinstance(payload.get("multi_panel_runtime_cohesion"), dict) else {}
    browser_session = payload.get("canonical_browser_session_persistence") if isinstance(payload.get("canonical_browser_session_persistence"), dict) else {}
    workflow = payload.get("governed_operator_workflow") if isinstance(payload.get("governed_operator_workflow"), dict) else {}
    continuity = payload.get("runtime_continuity_visualization") if isinstance(payload.get("runtime_continuity_visualization"), dict) else {}
    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}
    loop = payload.get("continuous_browser_runtime_loop") if isinstance(payload.get("continuous_browser_runtime_loop"), dict) else {}

    cohesion_summary = cohesion.get("summary") if isinstance(cohesion.get("summary"), dict) else {}
    session_snapshot = browser_session.get("session_snapshot") if isinstance(browser_session.get("session_snapshot"), dict) else {}
    workflow_summary = workflow.get("summary") if isinstance(workflow.get("summary"), dict) else {}
    continuity_summary = continuity.get("summary") if isinstance(continuity.get("summary"), dict) else {}
    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    loop_summary = loop.get("summary") if isinstance(loop.get("summary"), dict) else {}

    selected_route = (
        session_snapshot.get("selected_route")
        or continuity_summary.get("selected_route")
        or loop_summary.get("selected_route")
        or "unknown"
    )

    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)
    workflow_total = int(workflow_summary.get("workflow_total", 0) or 0)
    evidence_total = int(evidence_summary.get("evidence_total", session_snapshot.get("evidence_total", 0)) or 0)

    session_state = "orchestrated"
    if drift_total:
        session_state = "blocked"
    elif missing_total:
        session_state = "partial"
    elif workflow_summary.get("manual_review_required", False):
        session_state = "review_required"

    bindings: List[Dict[str, Any]] = [
        {"binding": "route_session", "state": "bound" if selected_route != "unknown" else "unbound", "detail": selected_route},
        {"binding": "workflow_session", "state": "active" if workflow_total else "idle", "detail": f"{workflow_total} workflow items"},
        {"binding": "evidence_session", "state": "active" if evidence_total else "empty", "detail": f"{evidence_total} evidence items"},
        {"binding": "cohesion_session", "state": cohesion.get("cohesion_state", "unknown"), "detail": cohesion_summary.get("payload_propagation", "unknown")},
        {"binding": "browser_loop_session", "state": loop.get("loop_state", "unknown"), "detail": loop_summary.get("payload_freshness", "unknown")},
    ]

    return {
        "version": OPERATIONAL_SESSION_ORCHESTRATION_VERSION,
        "status": "active",
        "session_state": session_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "operator_mutation_enabled": False,
            "runtime_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "selected_route": selected_route,
            "workflow_total": workflow_total,
            "evidence_total": evidence_total,
            "missing_panel_total": missing_total,
            "authority_drift_total": drift_total,
            "manual_review_required": bool(workflow_summary.get("manual_review_required", False)),
            "payload_propagation": cohesion_summary.get("payload_propagation", "unknown"),
            "continuity_state": continuity.get("continuity_state", "unknown"),
            "loop_state": loop.get("loop_state", "unknown"),
        },
        "session_bindings": bindings,
    }


def attach_operational_session_orchestration(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_operational_session_orchestration"] = build_operational_session_orchestration(payload)
    return payload
