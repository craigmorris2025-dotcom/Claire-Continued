from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

LOCKED_AUTHORITY = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "fail_closed_governance": True,
    "runtime_authority_blocked": True,
    "browser_execution_blocked": True,
    "javascript_execution_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "autonomous_execution_blocked": True,
    "automatic_updates_blocked": True,
    "evidence_quarantine_required": True,
    "manual_promotion_required": True,
    "continuous_live_crawling_blocked": True,
}

Decision = Literal["approved_for_future_controlled_promotion", "rejected", "needs_revision"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(data: Any) -> str:
    return sha256_text(stable_json(data))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return path


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root else Path.cwd().resolve()


def _load_latest_json(folder: Path, glob_pattern: str = "*.json") -> tuple[Path, dict[str, Any]]:
    candidates = sorted(folder.glob(glob_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No JSON artifacts found in {folder}")
    path = candidates[0]
    return path, read_json(path)


def build_promotion_review_gate(root: str | Path | None = None, package_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    package_file, package = (Path(package_path), read_json(Path(package_path))) if package_path else _load_latest_json(root_path / "output" / "manual_promotion_packages")
    candidate_id = str(package.get("candidate_id") or "unknown-candidate")
    blocked_reasons = list(package.get("blocked_reasons") or [])
    checklist = list(package.get("approval_checklist") or [])
    ready = not blocked_reasons and package.get("runtime_truth_mutated") is False and package.get("automatic_update_performed") is False
    gate = {
        "schema_version": "s39r1.promotion_review_gate.v1",
        "created_at": utc_now_iso(),
        "phase": "S39R1",
        "candidate_id": candidate_id,
        "status": "review_gate_created",
        "gate_state": "operator_decision_allowed" if ready else "operator_decision_blocked",
        "manual_promotion_required": True,
        "operator_decision_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "promotion_state": "not_promoted",
        "blocked_reasons": blocked_reasons,
        "approval_checklist": checklist,
        "source_package_path": str(package_file),
        "source_package_sha256": sha256_json(package),
        "locked_authority": dict(LOCKED_AUTHORITY),
        "governance_warnings": [
            "review gate only",
            "operator approval may only create an approval record",
            "approval record does not mutate runtime truth",
            "future controlled promotion requires a separate gated phase",
        ],
    }
    gate["review_gate_sha256"] = sha256_json(gate)
    write_json(root_path / "output" / "promotion_review_gates" / f"{candidate_id}.review_gate.json", gate)
    return gate


def create_operator_decision_record(root: str | Path | None = None, gate_path: str | Path | None = None, decision: Decision = "needs_revision", operator_ack: str = "NO", operator_id: str = "operator", rationale: str = "") -> dict[str, Any]:
    root_path = _project_root(root)
    gate_file, gate = (Path(gate_path), read_json(Path(gate_path))) if gate_path else _load_latest_json(root_path / "output" / "promotion_review_gates")
    candidate_id = str(gate.get("candidate_id") or "unknown-candidate")
    valid_decisions = {"approved_for_future_controlled_promotion", "rejected", "needs_revision"}
    if decision not in valid_decisions:
        raise ValueError(f"Unsupported operator decision: {decision}")
    ack_ok = operator_ack == "YES"
    blocked_reasons = list(gate.get("blocked_reasons") or [])
    gate_allows = gate.get("gate_state") == "operator_decision_allowed"
    effective_decision = decision
    decision_state = "recorded"
    if decision == "approved_for_future_controlled_promotion" and (not ack_ok or not gate_allows):
        effective_decision = "needs_revision"
        decision_state = "approval_downgraded_fail_closed"
        if not ack_ok:
            blocked_reasons.append("explicit operator_ack YES required for approval")
        if not gate_allows:
            blocked_reasons.append("review gate is blocked")
    record = {
        "schema_version": "s39r2.operator_decision_record.v1",
        "created_at": utc_now_iso(),
        "phase": "S39R2",
        "candidate_id": candidate_id,
        "status": "operator_decision_record_created",
        "decision_state": decision_state,
        "requested_decision": decision,
        "effective_decision": effective_decision,
        "operator_id": operator_id,
        "operator_ack": operator_ack,
        "rationale": rationale,
        "manual_promotion_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "promotion_state": "not_promoted",
        "blocked_reasons": sorted(set(blocked_reasons)),
        "source_review_gate_path": str(gate_file),
        "source_review_gate_sha256": sha256_json(gate),
        "locked_authority": dict(LOCKED_AUTHORITY),
    }
    record["decision_record_sha256"] = sha256_json(record)
    write_json(root_path / "output" / "operator_decision_records" / f"{candidate_id}.operator_decision_record.json", record)
    return record


def seal_manual_promotion_candidate(root: str | Path | None = None, decision_record_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    record_file, record = (Path(decision_record_path), read_json(Path(decision_record_path))) if decision_record_path else _load_latest_json(root_path / "output" / "operator_decision_records")
    candidate_id = str(record.get("candidate_id") or "unknown-candidate")
    approved = record.get("effective_decision") == "approved_for_future_controlled_promotion"
    sealed = {
        "schema_version": "s39r3.sealed_manual_promotion_candidate.v1",
        "created_at": utc_now_iso(),
        "phase": "S39R3",
        "candidate_id": candidate_id,
        "status": "sealed_candidate_created",
        "sealed_state": "approved_proposal_sealed" if approved else "non_approved_proposal_sealed",
        "effective_decision": record.get("effective_decision"),
        "future_controlled_promotion_candidate": bool(approved),
        "manual_promotion_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "promotion_state": "not_promoted",
        "source_decision_record_path": str(record_file),
        "source_decision_record_sha256": sha256_json(record),
        "immutability_note": "This seal captures an operator-reviewed proposal only; it is not a runtime truth write.",
        "locked_authority": dict(LOCKED_AUTHORITY),
        "forbidden_actions_preserved": ["runtime truth mutation", "automatic update", "autonomous loop", "browser execution", "JavaScript execution", "continuous live crawling"],
    }
    sealed["sealed_candidate_sha256"] = sha256_json(sealed)
    write_json(root_path / "output" / "sealed_manual_promotion_candidates" / f"{candidate_id}.sealed_candidate.json", sealed)
    return sealed


def build_promotion_status_index(root: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    gates = sorted((root_path / "output" / "promotion_review_gates").glob("*.json"))
    decisions = sorted((root_path / "output" / "operator_decision_records").glob("*.json"))
    sealed_files = sorted((root_path / "output" / "sealed_manual_promotion_candidates").glob("*.json"))
    sealed = [read_json(path) for path in sealed_files]
    approved = [item for item in sealed if item.get("future_controlled_promotion_candidate") is True]
    index = {
        "schema_version": "s39r4.promotion_status_index.v1",
        "created_at": utc_now_iso(),
        "phase": "S39R4",
        "status": "promotion_status_index_created",
        "manual_promotion_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "promotion_state": "not_promoted",
        "counts": {"review_gates": len(gates), "operator_decision_records": len(decisions), "sealed_candidates": len(sealed_files), "approved_future_controlled_promotion_candidates": len(approved)},
        "sealed_candidates": [{"candidate_id": item.get("candidate_id"), "sealed_state": item.get("sealed_state"), "effective_decision": item.get("effective_decision"), "future_controlled_promotion_candidate": item.get("future_controlled_promotion_candidate"), "sealed_candidate_sha256": item.get("sealed_candidate_sha256")} for item in sealed],
        "locked_authority": dict(LOCKED_AUTHORITY),
        "dashboard_surface_ready": True,
        "dashboard_note": "Backend truth summary only; cockpit remains presentation-only.",
    }
    index["promotion_status_index_sha256"] = sha256_json(index)
    write_json(root_path / "output" / "promotion_status_index" / "promotion_status_index.json", index)
    return index


def run_s39r1_r4_pipeline(root: str | Path | None = None, decision: Decision = "needs_revision", operator_ack: str = "NO", operator_id: str = "operator", rationale: str = "") -> dict[str, Any]:
    root_path = _project_root(root)
    gate = build_promotion_review_gate(root_path)
    record = create_operator_decision_record(root_path, decision=decision, operator_ack=operator_ack, operator_id=operator_id, rationale=rationale)
    sealed = seal_manual_promotion_candidate(root_path)
    index = build_promotion_status_index(root_path)
    return {"schema_version": "s39r1_r4.pipeline_result.v1", "created_at": utc_now_iso(), "phase": "S39R1-R4", "status": "promotion_review_gate_pipeline_complete", "candidate_id": gate.get("candidate_id"), "runtime_truth_mutated": False, "automatic_update_performed": False, "manual_promotion_required": True, "outputs": {"promotion_review_gate": gate, "operator_decision_record": record, "sealed_manual_promotion_candidate": sealed, "promotion_status_index": index}, "locked_authority": dict(LOCKED_AUTHORITY)}
