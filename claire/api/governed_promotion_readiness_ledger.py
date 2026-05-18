
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


ALLOWED_DECISIONS = {
    "pending",
    "approved_for_candidate_review",
    "rejected",
    "needs_revision",
    "operator_deferred",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def readiness_from_audit_boundary(audit_boundary: Mapping[str, Any]) -> Dict[str, Any]:
    blocked = []
    if audit_boundary.get("runtime_truth_mutation_allowed") is not False:
        blocked.append("runtime_truth_mutation_not_locked_false")
    if audit_boundary.get("promotion_effect") != "none":
        blocked.append("promotion_effect_not_none")
    if audit_boundary.get("manual_promotion_required") is not True:
        blocked.append("manual_promotion_required_missing")
    if audit_boundary.get("quarantine_required") is not True:
        blocked.append("quarantine_required_missing")
    authority = dict(audit_boundary.get("authority", {}) or {})
    for key, expected in LOCKED_AUTHORITY.items():
        if authority.get(key) is not expected:
            blocked.append(f"authority_{key}_not_locked_false")

    status = "candidate_review_ready" if not blocked else "blocked"
    ledger = {
        "record_type": "promotion_readiness_ledger_entry",
        "version": "v19.89.8-S39R9-R12",
        "candidate_id": audit_boundary.get("candidate_id"),
        "proposal_id": audit_boundary.get("proposal_id"),
        "status": status,
        "blocked_reasons": blocked,
        "proposal_sha256": audit_boundary.get("proposal_sha256"),
        "approval_record_sha256": audit_boundary.get("approval_record_sha256"),
        "audit_boundary_sha256": audit_boundary.get("audit_boundary_sha256"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "created_at": _utc_now(),
    }
    ledger["readiness_ledger_sha256"] = _sha256(ledger)
    return ledger


def operator_decision_ledger_entry(
    readiness_entry: Mapping[str, Any],
    *,
    decision: str = "pending",
    reviewer: Optional[str] = None,
    notes: str = "",
    operator_ack: str = "NO",
) -> Dict[str, Any]:
    normalized = str(decision or "pending").strip().lower()
    if normalized not in ALLOWED_DECISIONS:
        normalized = "pending"

    entry = {
        "record_type": "operator_decision_ledger_entry",
        "version": "v19.89.8-S39R9-R12",
        "candidate_id": readiness_entry.get("candidate_id"),
        "proposal_id": readiness_entry.get("proposal_id"),
        "decision": normalized,
        "reviewer": reviewer,
        "notes": notes,
        "operator_ack": operator_ack,
        "source_readiness_ledger_sha256": readiness_entry.get("readiness_ledger_sha256"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "decision_effect": "record_only",
        "created_at": _utc_now(),
    }
    entry["operator_decision_ledger_sha256"] = _sha256(entry)
    return entry


def append_jsonl(path: Path, entry: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(entry), sort_keys=True) + "\n")
    return path


def build_promotion_readiness_ledgers(
    audit_boundary_dir: Path,
    output_dir: Path,
    *,
    reviewer: Optional[str] = None,
    decision: str = "pending",
    operator_ack: str = "NO",
    notes: str = "",
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_files = sorted(audit_boundary_dir.glob("*.audit_boundary.json"))

    readiness_entries: List[Dict[str, Any]] = []
    decision_entries: List[Dict[str, Any]] = []

    readiness_jsonl = output_dir / "promotion_readiness_ledger.jsonl"
    decision_jsonl = output_dir / "operator_decision_ledger.jsonl"

    if readiness_jsonl.exists():
        readiness_jsonl.unlink()
    if decision_jsonl.exists():
        decision_jsonl.unlink()

    for file in audit_files:
        audit_boundary = _load_json(file)
        readiness = readiness_from_audit_boundary(audit_boundary)
        decision_entry = operator_decision_ledger_entry(
            readiness,
            decision=decision,
            reviewer=reviewer,
            notes=notes,
            operator_ack=operator_ack,
        )
        readiness_entries.append(readiness)
        decision_entries.append(decision_entry)
        append_jsonl(readiness_jsonl, readiness)
        append_jsonl(decision_jsonl, decision_entry)

    summary = {
        "record_type": "promotion_readiness_ledger_summary",
        "version": "v19.89.8-S39R9-R12",
        "audit_boundary_dir": str(audit_boundary_dir),
        "total_audit_boundaries": len(audit_files),
        "ready_count": sum(1 for item in readiness_entries if item.get("status") == "candidate_review_ready"),
        "blocked_count": sum(1 for item in readiness_entries if item.get("status") == "blocked"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "readiness_ledger": str(readiness_jsonl),
        "operator_decision_ledger": str(decision_jsonl),
        "created_at": _utc_now(),
    }
    summary["summary_sha256"] = _sha256(summary)
    summary_path = output_dir / "promotion_readiness_ledger_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "summary": summary,
        "summary_path": str(summary_path),
        "readiness_ledger": str(readiness_jsonl),
        "operator_decision_ledger": str(decision_jsonl),
    }
