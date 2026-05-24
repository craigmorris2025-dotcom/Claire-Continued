"""
Claire Syntalion v19.32-v19.36 Runtime Quality Proof Pack.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

try:
    from runtime_core.web.web_to_pipeline_launch_candidate import execute_web_to_pipeline_launch_candidate
except Exception:
    execute_web_to_pipeline_launch_candidate = None  # type: ignore


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {}


@dataclass(frozen=True)
class DashboardPanelReadiness:
    panel_name: str
    ready: bool
    required_fields: List[str]
    missing_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"panel_name": self.panel_name, "ready": self.ready, "required_fields": list(self.required_fields), "missing_fields": list(self.missing_fields)}


@dataclass(frozen=True)
class TerminalRuntimeOutput:
    terminal_state: str
    selected_route: str
    summary: str
    evidence_count: int
    accepted_evidence_count: int
    operator_review_required: bool
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terminal_state": self.terminal_state,
            "selected_route": self.selected_route,
            "summary": self.summary,
            "evidence_count": self.evidence_count,
            "accepted_evidence_count": self.accepted_evidence_count,
            "operator_review_required": self.operator_review_required,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class OperatorReviewQueueItem:
    review_id: str
    query: str
    terminal_state: str
    selected_route: str
    priority: str
    status: str
    payload: Dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "query": self.query,
            "terminal_state": self.terminal_state,
            "selected_route": self.selected_route,
            "priority": self.priority,
            "status": self.status,
            "payload": dict(self.payload),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RuntimeQualityProof:
    passed: bool
    status: str
    checks: Dict[str, bool]
    panel_readiness: List[DashboardPanelReadiness]
    terminal_output: TerminalRuntimeOutput
    review_queue_item: OperatorReviewQueueItem
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status,
            "checks": dict(self.checks),
            "panel_readiness": [item.to_dict() for item in self.panel_readiness],
            "terminal_output": self.terminal_output.to_dict(),
            "review_queue_item": self.review_queue_item.to_dict(),
            "created_at": self.created_at,
        }


def evaluate_dashboard_panel_readiness(dashboard: Mapping[str, Any]) -> List[DashboardPanelReadiness]:
    panels = _as_dict(dashboard.get("panels")) if isinstance(dashboard, Mapping) else {}
    requirements = {
        "main_result": ["terminal_state", "selected_route", "summary"],
        "search": ["query", "intent", "status"],
        "evidence": ["total", "accepted", "rejected"],
        "pipeline": ["ingestion_status", "signals", "entities"],
        "route": ["selected_route", "terminal_state", "route_confidence"],
    }
    readiness: List[DashboardPanelReadiness] = []
    for panel_name, required in requirements.items():
        panel = _as_dict(panels.get(panel_name))
        missing = [field for field in required if field not in panel]
        readiness.append(DashboardPanelReadiness(panel_name=panel_name, ready=not missing, required_fields=required, missing_fields=missing))
    return readiness


def build_terminal_runtime_output(candidate: Mapping[str, Any]) -> TerminalRuntimeOutput:
    route = _as_dict(candidate.get("route"))
    dashboard = _as_dict(candidate.get("dashboard"))
    panels = _as_dict(dashboard.get("panels"))
    main_result = _as_dict(panels.get("main_result"))
    pipeline = _as_dict(candidate.get("pipeline"))
    return TerminalRuntimeOutput(
        terminal_state=str(route.get("terminal_state") or main_result.get("terminal_state") or "unknown"),
        selected_route=str(route.get("selected_route") or main_result.get("selected_route") or "unknown"),
        summary=str(main_result.get("summary") or route.get("reason") or "No summary available."),
        evidence_count=int(pipeline.get("evidence_count") or 0),
        accepted_evidence_count=int(pipeline.get("accepted_evidence_count") or 0),
        operator_review_required=True,
    )


def build_operator_review_queue_item(query: str, terminal: TerminalRuntimeOutput, candidate: Mapping[str, Any]) -> OperatorReviewQueueItem:
    priority = "high" if terminal.terminal_state in {"portfolio_action_ready", "trend_thesis_ready"} else "normal"
    review_id_seed = f"{query}|{terminal.selected_route}|{terminal.terminal_state}"
    review_id = "review-" + str(abs(hash(review_id_seed)))[:10]
    return OperatorReviewQueueItem(
        review_id=review_id,
        query=query,
        terminal_state=terminal.terminal_state,
        selected_route=terminal.selected_route,
        priority=priority,
        status="awaiting_operator_review",
        payload={"terminal_output": terminal.to_dict(), "quality_gate": _as_dict(candidate.get("quality_gate")), "version_pack": candidate.get("version_pack", "unknown")},
    )


def run_runtime_quality_proof(candidate: Mapping[str, Any]) -> RuntimeQualityProof:
    contract = _as_dict(candidate.get("contract"))
    dashboard = _as_dict(candidate.get("dashboard"))
    quality_gate = _as_dict(candidate.get("quality_gate"))
    panel_readiness = evaluate_dashboard_panel_readiness(dashboard)
    terminal = build_terminal_runtime_output(candidate)
    queue_item = build_operator_review_queue_item(str(contract.get("query") or ""), terminal, candidate)
    checks = {
        "candidate_quality_gate_passed": bool(quality_gate.get("passed")),
        "all_required_dashboard_panels_ready": all(item.ready for item in panel_readiness),
        "terminal_state_is_actionable": terminal.terminal_state not in {"", "unknown", "failed"},
        "review_queue_item_created": queue_item.status == "awaiting_operator_review" and queue_item.review_id.startswith("review-"),
        "temporary_dashboard_role_preserved": dashboard.get("dashboard_role") == "temporary_proof_dev_operator_cockpit",
    }
    passed = all(checks.values())
    return RuntimeQualityProof(passed=passed, status="runtime_quality_proof_passed" if passed else "runtime_quality_proof_blocked", checks=checks, panel_readiness=panel_readiness, terminal_output=terminal, review_queue_item=queue_item)


def execute_runtime_quality_proof(query: str, live_results: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    if execute_web_to_pipeline_launch_candidate is None:
        raise RuntimeError("v19.26-v19.31 launch candidate module is not installed or importable")
    candidate = execute_web_to_pipeline_launch_candidate(query=query, live_results=live_results)
    proof = run_runtime_quality_proof(candidate)
    return {"version_pack": "v19.32-v19.36", "candidate": candidate, "runtime_quality_proof": proof.to_dict(), "dashboard_role": "temporary_proof_dev_operator_cockpit", "next_pack": "v19.37-v19.41"}


build_dashboard_panel_readiness = evaluate_dashboard_panel_readiness
build_review_queue_item = build_operator_review_queue_item
run_quality_proof = run_runtime_quality_proof
