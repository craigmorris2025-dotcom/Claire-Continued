from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


RUNTIME_WORKSPACE_CONTINUITY_VERSION = "v19.89.8-S29"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_runtime_workspace_continuity(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    orchestration = payload.get("governed_operational_session_orchestration") if isinstance(payload.get("governed_operational_session_orchestration"), dict) else {}
    browser_session = payload.get("canonical_browser_session_persistence") if isinstance(payload.get("canonical_browser_session_persistence"), dict) else {}
    workflow = payload.get("governed_operator_workflow") if isinstance(payload.get("governed_operator_workflow"), dict) else {}
    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}
    cohesion = payload.get("multi_panel_runtime_cohesion") if isinstance(payload.get("multi_panel_runtime_cohesion"), dict) else {}
    continuity = payload.get("runtime_continuity_visualization") if isinstance(payload.get("runtime_continuity_visualization"), dict) else {}

    orch_summary = orchestration.get("summary") if isinstance(orchestration.get("summary"), dict) else {}
    session_snapshot = browser_session.get("session_snapshot") if isinstance(browser_session.get("session_snapshot"), dict) else {}
    workflow_summary = workflow.get("summary") if isinstance(workflow.get("summary"), dict) else {}
    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    cohesion_summary = cohesion.get("summary") if isinstance(cohesion.get("summary"), dict) else {}
    continuity_summary = continuity.get("summary") if isinstance(continuity.get("summary"), dict) else {}

    selected_route = (
        orch_summary.get("selected_route")
        or session_snapshot.get("selected_route")
        or continuity_summary.get("selected_route")
        or "unknown"
    )

    workspace_id = f"workspace:{selected_route}"
    missing_panels = int(cohesion_summary.get("missing_total", orch_summary.get("missing_panel_total", 0)) or 0)
    drift_total = int(cohesion_summary.get("drift_total", orch_summary.get("authority_drift_total", 0)) or 0)
    workflow_total = int(workflow_summary.get("workflow_total", orch_summary.get("workflow_total", 0)) or 0)
    evidence_total = int(evidence_summary.get("evidence_total", orch_summary.get("evidence_total", 0)) or 0)

    workspace_state = "continuous"
    if drift_total:
        workspace_state = "blocked"
    elif missing_panels:
        workspace_state = "partial"
    elif orchestration.get("session_state") == "review_required" or workflow_summary.get("manual_review_required", False):
        workspace_state = "review_required"
    elif continuity.get("continuity_state") in {"degraded", "recovering"}:
        workspace_state = continuity.get("continuity_state")

    dimensions: List[Dict[str, Any]] = [
        {
            "dimension": "route_workspace",
            "state": "bound" if selected_route != "unknown" else "unbound",
            "detail": selected_route,
        },
        {
            "dimension": "session_workspace",
            "state": orchestration.get("session_state", "unknown"),
            "detail": f"{len(orchestration.get('session_bindings', [])) if isinstance(orchestration.get('session_bindings'), list) else 0} bindings",
        },
        {
            "dimension": "workflow_workspace",
            "state": "active" if workflow_total else "idle",
            "detail": f"{workflow_total} workflow items",
        },
        {
            "dimension": "evidence_workspace",
            "state": "active" if evidence_total else "empty",
            "detail": f"{evidence_total} evidence items",
        },
        {
            "dimension": "cohesion_workspace",
            "state": cohesion.get("cohesion_state", "unknown"),
            "detail": cohesion_summary.get("payload_propagation", "unknown"),
        },
    ]

    return {
        "version": RUNTIME_WORKSPACE_CONTINUITY_VERSION,
        "status": "active",
        "workspace_id": workspace_id,
        "workspace_state": workspace_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "operator_mutation_enabled": False,
            "runtime_mutation_enabled": False,
            "workspace_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "selected_route": selected_route,
            "workflow_total": workflow_total,
            "evidence_total": evidence_total,
            "missing_panel_total": missing_panels,
            "authority_drift_total": drift_total,
            "manual_review_required": bool(workflow_summary.get("manual_review_required", False)),
            "payload_freshness": session_snapshot.get("payload_freshness", continuity_summary.get("payload_freshness", "unknown")),
            "continuity_state": continuity.get("continuity_state", "unknown"),
            "session_state": orchestration.get("session_state", "unknown"),
        },
        "workspace_dimensions": dimensions,
    }


def attach_runtime_workspace_continuity(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_runtime_workspace_continuity"] = build_runtime_workspace_continuity(payload)
    return payload
