from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


OPERATIONAL_TOPOLOGY_CONTINUITY_VERSION = "v19.89.8-S31"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_operational_topology_continuity(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    multi_workspace = payload.get("governed_multi_workspace_orchestration") if isinstance(payload.get("governed_multi_workspace_orchestration"), dict) else {}
    workspace = payload.get("governed_runtime_workspace_continuity") if isinstance(payload.get("governed_runtime_workspace_continuity"), dict) else {}
    orchestration = payload.get("governed_operational_session_orchestration") if isinstance(payload.get("governed_operational_session_orchestration"), dict) else {}
    cohesion = payload.get("multi_panel_runtime_cohesion") if isinstance(payload.get("multi_panel_runtime_cohesion"), dict) else {}
    loop = payload.get("continuous_browser_runtime_loop") if isinstance(payload.get("continuous_browser_runtime_loop"), dict) else {}

    topology_summary = multi_workspace.get("summary") if isinstance(multi_workspace.get("summary"), dict) else {}
    workspace_summary = workspace.get("summary") if isinstance(workspace.get("summary"), dict) else {}
    session_summary = orchestration.get("summary") if isinstance(orchestration.get("summary"), dict) else {}
    cohesion_summary = cohesion.get("summary") if isinstance(cohesion.get("summary"), dict) else {}
    loop_summary = loop.get("summary") if isinstance(loop.get("summary"), dict) else {}

    workspace_total = int(topology_summary.get("workspace_total", 0) or 0)
    missing_total = int(topology_summary.get("missing_panel_total", cohesion_summary.get("missing_total", 0)) or 0)
    drift_total = int(topology_summary.get("authority_drift_total", cohesion_summary.get("drift_total", 0)) or 0)

    topology_state = multi_workspace.get("topology_state", "unknown")
    workspace_state = workspace.get("workspace_state", "unknown")
    session_state = orchestration.get("session_state", "unknown")
    loop_state = loop.get("loop_state", "unknown")

    continuity_state = "continuous"
    if drift_total or topology_state == "blocked":
        continuity_state = "blocked"
    elif missing_total or topology_state == "partial":
        continuity_state = "partial"
    elif topology_state in {"degraded", "recovering"}:
        continuity_state = topology_state
    elif topology_state == "review_required" or workspace_state == "review_required" or session_state == "review_required":
        continuity_state = "review_required"
    elif topology_state == "unknown" and workspace_state == "unknown":
        continuity_state = "initializing"

    continuity_chain: List[Dict[str, Any]] = [
        {
            "layer": "multi_workspace_topology",
            "state": topology_state,
            "detail": f"{workspace_total} workspaces",
        },
        {
            "layer": "workspace_continuity",
            "state": workspace_state,
            "detail": workspace_summary.get("selected_route", "unknown"),
        },
        {
            "layer": "session_orchestration",
            "state": session_state,
            "detail": session_summary.get("selected_route", "unknown"),
        },
        {
            "layer": "panel_cohesion",
            "state": cohesion.get("cohesion_state", "unknown"),
            "detail": cohesion_summary.get("payload_propagation", "unknown"),
        },
        {
            "layer": "browser_loop",
            "state": loop_state,
            "detail": loop_summary.get("payload_freshness", "unknown"),
        },
    ]

    return {
        "version": OPERATIONAL_TOPOLOGY_CONTINUITY_VERSION,
        "status": "active",
        "continuity_state": continuity_state,
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "operator_mutation_enabled": False,
            "runtime_mutation_enabled": False,
            "workspace_mutation_enabled": False,
            "topology_mutation_enabled": False,
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "workspace_total": workspace_total,
            "selected_route": topology_summary.get("selected_route", workspace_summary.get("selected_route", "unknown")),
            "topology_state": topology_state,
            "workspace_state": workspace_state,
            "session_state": session_state,
            "loop_state": loop_state,
            "missing_panel_total": missing_total,
            "authority_drift_total": drift_total,
            "payload_propagation": topology_summary.get("payload_propagation", cohesion_summary.get("payload_propagation", "unknown")),
            "manual_review_required": bool(topology_summary.get("manual_review_required", False) or workspace_summary.get("manual_review_required", False)),
        },
        "continuity_chain": continuity_chain,
    }


def attach_operational_topology_continuity(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_operational_topology_continuity"] = build_operational_topology_continuity(payload)
    return payload
