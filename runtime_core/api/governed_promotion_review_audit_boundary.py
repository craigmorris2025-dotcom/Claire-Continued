from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def summarize_review_status(proposal_package: Mapping[str, Any]) -> Dict[str, Any]:
    review = dict(proposal_package.get("operator_review", {}) or {})
    warnings = _as_list(proposal_package.get("governance_warnings"))
    contradictions = _as_list(proposal_package.get("contradictions"))
    checklist = _as_list(proposal_package.get("approval_checklist"))

    approved_items = [
        item for item in checklist
        if isinstance(item, Mapping) and str(item.get("status", "")).lower() in {"pass", "passed", "complete", "completed", "approved"}
    ]
    blocked_items = [
        item for item in checklist
        if isinstance(item, Mapping) and str(item.get("status", "")).lower() in {"fail", "failed", "blocked", "missing"}
    ]

    ready_for_operator_review = bool(proposal_package.get("candidate_id")) and not blocked_items

    return {
        "candidate_id": proposal_package.get("candidate_id"),
        "proposal_id": proposal_package.get("proposal_id"),
        "status": "ready_for_manual_review" if ready_for_operator_review else "review_blocked",
        "manual_approval_required": True,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "reviewer": review.get("reviewer"),
        "review_decision": review.get("decision", "unreviewed"),
        "approval_checklist_total": len(checklist),
        "approval_checklist_completed": len(approved_items),
        "approval_checklist_blocked": len(blocked_items),
        "governance_warning_count": len(warnings),
        "contradiction_count": len(contradictions),
        "generated_at": _utc_now(),
    }


def build_approval_record_shell(
    proposal_package: Mapping[str, Any],
    *,
    operator_ack: str = "NO",
    reviewer: Optional[str] = None,
    decision: str = "pending",
    notes: str = "",
) -> Dict[str, Any]:
    normalized_decision = str(decision or "pending").strip().lower()
    if normalized_decision not in {"pending", "approved_for_candidate_review", "rejected", "needs_revision"}:
        normalized_decision = "pending"

    shell = {
        "record_type": "manual_promotion_approval_record_shell",
        "version": "v19.89.8-S39R5-R8",
        "candidate_id": proposal_package.get("candidate_id"),
        "proposal_id": proposal_package.get("proposal_id"),
        "operator_ack": operator_ack,
        "reviewer": reviewer,
        "decision": normalized_decision,
        "notes": notes,
        "authority": dict(LOCKED_AUTHORITY),
        "promotion_effect": "none",
        "runtime_truth_mutation_allowed": False,
        "manual_promotion_still_required": True,
        "source_package_sha256": _canonical_sha256(dict(proposal_package)),
        "created_at": _utc_now(),
    }
    shell["approval_record_sha256"] = _canonical_sha256(shell)
    return shell


def seal_proposal_audit_boundary(
    proposal_package: Mapping[str, Any],
    approval_record_shell: Mapping[str, Any],
) -> Dict[str, Any]:
    proposal_sha = _canonical_sha256(dict(proposal_package))
    record_sha = _canonical_sha256(dict(approval_record_shell))
    boundary = {
        "record_type": "promotion_review_audit_boundary",
        "version": "v19.89.8-S39R5-R8",
        "candidate_id": proposal_package.get("candidate_id"),
        "proposal_id": proposal_package.get("proposal_id"),
        "proposal_sha256": proposal_sha,
        "approval_record_sha256": record_sha,
        "authority": dict(LOCKED_AUTHORITY),
        "promotion_effect": "none",
        "quarantine_required": True,
        "manual_promotion_required": True,
        "runtime_truth_mutation_allowed": False,
        "sealed_at": _utc_now(),
    }
    boundary["audit_boundary_sha256"] = _canonical_sha256(boundary)
    return boundary


def write_review_audit_artifacts(
    proposal_package: Mapping[str, Any],
    output_dir: Path,
    *,
    operator_ack: str = "NO",
    reviewer: Optional[str] = None,
    decision: str = "pending",
    notes: str = "",
) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    status = summarize_review_status(proposal_package)
    shell = build_approval_record_shell(
        proposal_package,
        operator_ack=operator_ack,
        reviewer=reviewer,
        decision=decision,
        notes=notes,
    )
    boundary = seal_proposal_audit_boundary(proposal_package, shell)

    candidate = str(proposal_package.get("candidate_id") or "unknown_candidate").replace("/", "_")
    files = {
        "status": output_dir / f"{candidate}.review_status.json",
        "approval_record_shell": output_dir / f"{candidate}.approval_record_shell.json",
        "audit_boundary": output_dir / f"{candidate}.audit_boundary.json",
    }

    files["status"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["approval_record_shell"].write_text(json.dumps(shell, indent=2, sort_keys=True), encoding="utf-8")
    files["audit_boundary"].write_text(json.dumps(boundary, indent=2, sort_keys=True), encoding="utf-8")
    return files
