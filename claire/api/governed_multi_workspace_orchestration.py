from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


MULTI_WORKSPACE_ORCHESTRATION_VERSION = "v19.89.8-S30"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_multi_workspace_orchestration(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    workspace = payload.get("governed_runtime_workspace_continuity") if isinstance(payload.get("governed_runtime_workspace_continuity"), dict) else {}
    orchestration = payload.get("governed_operational_session_orchestration") if isinstance(payload.get("governed_operational_session_orchestration"), dict) else {}
    cohesion = payload.get("multi_panel_runtime_cohesion") if isinstance(payload.get("multi_panel_runtime_cohesion"), dict) else {}
    overlay = payload.get("governed_route_activity_overlay") if isinstance(payload.get("governed_route_activity_overlay"), dict) else {}
    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}
    workflow = payload.get("governed_operator_workflow") if isinstance(payload.get("governed_operator_workflow"), dict) else {}

    workspace_summary = workspace.get("summary") if isinstance(workspace.get("summary"), dict) else {}
    orch_summary = orchestration.get("summary") if isinstance(orchestration.get("summary"), dict) else {}
    cohesion_summary = cohesion.get("summary") if isinstance(cohesion.get("summary"), dict) else {}
    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    workflow_summary = workflow.get("summary") if isinstance(workflow.get("summary"), dict) else {}
    routes = overlay.get("routes") if isinstance(overlay.get("routes"), list) else []

    selected_route = workspace_summary.get("selected_route") or orch_summary.get("selected_route") or "unknown"
    evidence_total = int(evidence_summary.get("evidence_total", workspace_summary.get("evidence_total", 0)) or 0)
    workflow_total = int(workflow_summary.get("workflow_total", workspace_summary.get("workflow_total", 0)) or 0)
    missing_total = int(cohesion_summary.get("missing_total", workspace_summary.get("missing_panel_total", 0)) or 0)
    drift_total = int(cohesion_summary.get("drift_total", workspace_summary.get("authority_drift_total", 0)) or 0)

    route_workspaces: List[Dict[str, Any]] = []
    for route in routes:
        if isinstance(route, dict):
            route_name = str(route.get("route", "unknown"))
            route_workspaces.append({
                "workspace_id": f"workspace:{route_name}",
                "route": route_name,
                "state": route.get("state", "unknown"),
                "selected": bool(route.get("selected", False)),
                "owned_surface_count": int(route.get("owned_surface_count", 0) or 0),
                "runtime_authority": "blocked",
                "workspace_mutation_enabled": False,
            })

    if not route_workspaces:
        route_workspaces.append({
            "workspace_id": f"workspace:{selected_route}",
            "route": selected_route,
            "state": workspace.get("workspace_state", "unknown"),
            "selected": selected_route != "unknown",
            "owned_surface_count": 0,
            "runtime_authority": "blocked",
            "workspace_mutation_enabled": False,
        })

    topology_state = "coordinated"
    if drift_total:
        topology_state = "blocked"
    elif missing_total:
        topology_state = "partial"
    elif any(item.get("state") == "degraded" for item in route_workspaces):
        topology_state = "degraded"
    elif any(item.get("state") == "recovering" for item in route_workspaces):
        topology_state = "recovering"
    elif workspace.get("workspace_state") == "review_required" or workflow_summary.get("manual_review_required", False):
        topology_state = "review_required"

    return {
        "version": MULTI_WORKSPACE_ORCHESTRATION_VERSION,
        "status": "active",
        "topology_state": topology_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "operator_mutation_enabled": False,
            "runtime_mutation_enabled": False,
            "workspace_mutation_enabled": False,
            "multi_workspace_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "workspace_total": len(route_workspaces),
            "selected_route": selected_route,
            "workflow_total": workflow_total,
            "evidence_total": evidence_total,
            "missing_panel_total": missing_total,
            "authority_drift_total": drift_total,
            "manual_review_required": bool(workflow_summary.get("manual_review_required", False)),
            "payload_propagation": cohesion_summary.get("payload_propagation", "unknown"),
            "workspace_state": workspace.get("workspace_state", "unknown"),
            "session_state": orchestration.get("session_state", "unknown"),
        },
        "workspaces": route_workspaces,
    }


def attach_multi_workspace_orchestration(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_multi_workspace_orchestration"] = build_multi_workspace_orchestration(payload)
    return payload
