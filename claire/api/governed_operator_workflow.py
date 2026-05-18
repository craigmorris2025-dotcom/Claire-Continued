from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


OPERATOR_WORKFLOW_VERSION = "v19.89.8-S25"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _workflow_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    evidence = payload.get("governed_evidence_basket") if isinstance(payload.get("governed_evidence_basket"), dict) else {}
    continuity = payload.get("runtime_continuity_visualization") if isinstance(payload.get("runtime_continuity_visualization"), dict) else {}
    search = payload.get("governed_search_session") if isinstance(payload.get("governed_search_session"), dict) else {}
    overlay = payload.get("governed_route_activity_overlay") if isinstance(payload.get("governed_route_activity_overlay"), dict) else {}

    evidence_summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    continuity_summary = continuity.get("summary") if isinstance(continuity.get("summary"), dict) else {}
    search_controls = search.get("session_controls") if isinstance(search.get("session_controls"), dict) else {}
    routes = overlay.get("routes") if isinstance(overlay.get("routes"), list) else []

    evidence_total = int(evidence_summary.get("evidence_total", 0) or 0)
    if evidence_total:
        items.append({
            "workflow_id": "evidence_review",
            "label": "Evidence Review",
            "state": "review_required",
            "count": evidence_total,
            "operator_action": "review_only",
            "runtime_authority": "blocked",
        })

    if search_controls.get("manual_review_required", True):
        items.append({
            "workflow_id": "search_review",
            "label": "Governed Search Review",
            "state": "manual_review_required",
            "count": 1,
            "operator_action": "acknowledge_only",
            "runtime_authority": "blocked",
        })

    if continuity.get("continuity_state") in {"degraded", "recovering"}:
        items.append({
            "workflow_id": "continuity_watch",
            "label": "Continuity Watch",
            "state": continuity.get("continuity_state", "unknown"),
            "count": int(continuity_summary.get("degraded_routes", 0) or 0) + int(continuity_summary.get("recovering_routes", 0) or 0),
            "operator_action": "observe_recovery",
            "runtime_authority": "blocked",
        })

    for route in routes:
        if isinstance(route, dict) and route.get("state") in {"degraded", "recovering"}:
            items.append({
                "workflow_id": f"route_{route.get('route', 'unknown')}",
                "label": f"Route: {route.get('route', 'unknown')}",
                "state": route.get("state", "unknown"),
                "count": int(route.get("issue_total", 0) or 0),
                "operator_action": "observe_route",
                "runtime_authority": "blocked",
            })

    if not items:
        items.append({
            "workflow_id": "normal_observation",
            "label": "Normal Observation",
            "state": "no_operator_action_required",
            "count": 0,
            "operator_action": "observe_only",
            "runtime_authority": "blocked",
        })

    return items[-16:]


def build_governed_operator_workflow(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    items = _workflow_items(payload)

    counts: Dict[str, int] = {}
    for item in items:
        state = str(item.get("state", "unknown"))
        counts[state] = counts.get(state, 0) + 1

    return {
        "version": OPERATOR_WORKFLOW_VERSION,
        "status": "active",
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "operator_actions": "review_acknowledge_observe_only",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "workflow_total": len(items),
            "state_counts": counts,
            "operator_mutation_enabled": False,
            "manual_review_required": any(item.get("state") in {"review_required", "manual_review_required"} for item in items),
        },
        "items": items,
    }


def attach_governed_operator_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_operator_workflow"] = build_governed_operator_workflow(payload)
    return payload
