from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memory_record import MemoryRecord, build_memory_id, utc_now


PASS_STATUSES = {"pass", "passed", "valid", "verified", "true"}
VALID_TERMINALS_FOR_MEMORY = {
    "trend_thesis_ready",
    "portfolio_action_ready",
    "portfolio_optimization_ready",
    "discovery_ready",
    "breakthrough_classified",
    "advancement_path_selected",
    "design_output_ready",
    "acquisition_package_ready",
    "acquisition_ready",
    "final_package_ready",
}


def _first_present(mapping: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _section(mapping: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = mapping.get(key)
    return value if isinstance(value, dict) else {}


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in PASS_STATUSES


def _validation_passed(validation_report: Dict[str, Any], runtime_truth: Dict[str, Any]) -> bool:
    if validation_report:
        status = validation_report.get("validation_authority_status")
        explicit = validation_report.get("validation_passed")
        return str(status).lower() == "pass" and _boolish(explicit)

    validation_truth = _section(runtime_truth, "validation_truth")
    return _boolish(_first_present(validation_truth, ["validation_passed", "passed", "is_valid"], False))


def _run_id(validation_report: Dict[str, Any], runtime_truth: Dict[str, Any]) -> str:
    run_truth = _section(runtime_truth, "run_truth")
    return str(
        validation_report.get("run_id")
        or _first_present(run_truth, ["run_id", "id"], None)
        or runtime_truth.get("run_id")
        or "unknown"
    )


def _route(validation_report: Dict[str, Any], runtime_truth: Dict[str, Any]) -> str:
    route_truth = _section(runtime_truth, "route_truth")
    run_truth = _section(runtime_truth, "run_truth")
    return str(
        validation_report.get("route_selected")
        or _first_present(route_truth, ["route_selected", "selected_route", "route"], None)
        or _first_present(run_truth, ["selected_route", "route_selected", "route"], None)
        or runtime_truth.get("route_selected")
        or "unknown"
    )


def _terminal(validation_report: Dict[str, Any], runtime_truth: Dict[str, Any]) -> str:
    terminal_truth = _section(runtime_truth, "terminal_truth")
    run_truth = _section(runtime_truth, "run_truth")
    return str(
        validation_report.get("terminal_state")
        or _first_present(terminal_truth, ["terminal_state", "state"], None)
        or _first_present(run_truth, ["terminal_state"], None)
        or runtime_truth.get("terminal_state")
        or "missing"
    )


def _evidence_count(validation_report: Dict[str, Any], runtime_truth: Dict[str, Any]) -> int:
    summary = validation_report.get("evidence_summary") if isinstance(validation_report.get("evidence_summary"), dict) else {}
    if summary.get("evidence_count") is not None:
        try:
            return int(summary.get("evidence_count"))
        except Exception:
            return 0

    evidence_truth = _section(runtime_truth, "evidence_truth")
    for key in ("evidence_count", "count"):
        if evidence_truth.get(key) is not None:
            try:
                return int(evidence_truth.get(key))
            except Exception:
                pass
    evidence = evidence_truth.get("evidence") or evidence_truth.get("evidence_chain") or runtime_truth.get("evidence_chain") or []
    return len(evidence) if isinstance(evidence, list) else 0


class MemoryGate:
    """Decide whether a Claire output may enter verified memory."""

    contract_version = "claire.verified_memory_gate.v17.61"

    def evaluate(
        self,
        runtime_truth: Dict[str, Any],
        validation_report: Optional[Dict[str, Any]] = None,
        source_output_path: str = "",
    ) -> Dict[str, Any]:
        validation_report = validation_report or {}
        run_id = _run_id(validation_report, runtime_truth)
        route_selected = _route(validation_report, runtime_truth)
        terminal_state = _terminal(validation_report, runtime_truth)
        evidence_count = _evidence_count(validation_report, runtime_truth)

        validation_passed = _validation_passed(validation_report, runtime_truth)
        validation_status = validation_report.get("validation_authority_status") or _section(runtime_truth, "validation_truth").get("validation_status") or "unknown"
        validation_score = int(validation_report.get("validation_score") or 0)

        reasons: List[str] = []
        blockers: List[str] = []

        if not validation_passed:
            blockers.append("validation_authority_not_passed")
            reasons.append("Validation authority has not passed; output cannot enter verified memory.")

        if terminal_state not in VALID_TERMINALS_FOR_MEMORY:
            blockers.append("terminal_state_not_memory_eligible")
            reasons.append(f"Terminal state '{terminal_state}' is not eligible for verified memory.")

        if evidence_count <= 0:
            blockers.append("no_evidence_traceability")
            reasons.append("No evidence traceability was found; memory storage is blocked.")

        if run_id == "unknown":
            blockers.append("missing_run_id")
            reasons.append("Run ID is missing; memory record cannot be tied to a source run.")

        memory_eligible = len(blockers) == 0
        memory_status = "eligible" if memory_eligible else "blocked"

        memory_record = None
        if memory_eligible:
            memory_record = MemoryRecord(
                memory_id=build_memory_id(run_id, route_selected, terminal_state),
                run_id=run_id,
                route_selected=route_selected,
                terminal_state=terminal_state,
                validation_score=validation_score,
                source_output_path=source_output_path,
                evidence_count=evidence_count,
                created_at=utc_now(),
                tags=[
                    "verified_output",
                    f"route:{route_selected}",
                    f"terminal:{terminal_state}",
                ],
            ).to_dict()

        return {
            "schema": "claire.verified_memory_gate_report.v1",
            "contract_version": self.contract_version,
            "generated_at": utc_now(),
            "run_id": run_id,
            "route_selected": route_selected,
            "terminal_state": terminal_state,
            "validation_status": validation_status,
            "validation_passed": validation_passed,
            "validation_score": validation_score,
            "evidence_count": evidence_count,
            "memory_status": memory_status,
            "memory_eligible": memory_eligible,
            "memory_blockers": blockers,
            "memory_reasons": reasons or ["Validation passed, evidence exists, terminal state is eligible, and run ID is present."],
            "memory_record": memory_record,
            "storage_mode": "gated_report_only",
            "storage_note": "v17.61 does not autonomously write long-term memory. It produces a verified memory eligibility report and record payload for a future storage layer.",
        }


def build_memory_gate_report(
    runtime_truth: Dict[str, Any],
    validation_report: Optional[Dict[str, Any]] = None,
    source_output_path: str = "",
) -> Dict[str, Any]:
    return MemoryGate().evaluate(runtime_truth, validation_report, source_output_path)
