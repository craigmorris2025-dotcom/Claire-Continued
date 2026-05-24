
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping


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


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_promotion_package_index(readiness_rows: List[Mapping[str, Any]], decision_rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    decisions_by_candidate = {row.get("candidate_id"): dict(row) for row in decision_rows}
    candidates = []
    for row in readiness_rows:
        candidate_id = row.get("candidate_id")
        decision = decisions_by_candidate.get(candidate_id, {})
        candidates.append({
            "candidate_id": candidate_id,
            "proposal_id": row.get("proposal_id"),
            "readiness_status": row.get("status"),
            "decision": decision.get("decision", "pending"),
            "decision_effect": decision.get("decision_effect", "record_only"),
            "proposal_sha256": row.get("proposal_sha256"),
            "approval_record_sha256": row.get("approval_record_sha256"),
            "audit_boundary_sha256": row.get("audit_boundary_sha256"),
            "readiness_ledger_sha256": row.get("readiness_ledger_sha256"),
            "operator_decision_ledger_sha256": decision.get("operator_decision_ledger_sha256"),
            "runtime_truth_mutation_allowed": False,
            "promotion_effect": "none",
        })

    index = {
        "record_type": "manual_promotion_package_index",
        "version": "v19.89.8-S39R13-R16",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "created_at": _utc_now(),
    }
    index["package_index_sha256"] = _sha256(index)
    return index


def build_blocked_candidate_registry(readiness_rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    blocked = [
        {
            "candidate_id": row.get("candidate_id"),
            "proposal_id": row.get("proposal_id"),
            "blocked_reasons": list(row.get("blocked_reasons", []) or []),
            "readiness_ledger_sha256": row.get("readiness_ledger_sha256"),
        }
        for row in readiness_rows
        if row.get("status") == "blocked"
    ]
    registry = {
        "record_type": "blocked_promotion_candidate_registry",
        "version": "v19.89.8-S39R13-R16",
        "blocked_count": len(blocked),
        "blocked_candidates": blocked,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "promotion_effect": "none",
        "created_at": _utc_now(),
    }
    registry["blocked_registry_sha256"] = _sha256(registry)
    return registry


def verify_promotion_replay(index: Mapping[str, Any], readiness_rows: List[Mapping[str, Any]], decision_rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    rebuilt = build_promotion_package_index(readiness_rows, decision_rows)
    expected_candidates = index.get("candidates", [])
    replay_candidates = rebuilt.get("candidates", [])
    ok = expected_candidates == replay_candidates
    report = {
        "record_type": "promotion_package_replay_verification",
        "version": "v19.89.8-S39R13-R16",
        "replay_ok": ok,
        "candidate_count": len(replay_candidates),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "created_at": _utc_now(),
    }
    if not ok:
        report["mismatch"] = {
            "expected_count": len(expected_candidates),
            "replayed_count": len(replay_candidates),
        }
    report["replay_report_sha256"] = _sha256(report)
    return report


def build_s39_plateau_report(index: Mapping[str, Any], blocked_registry: Mapping[str, Any], replay_report: Mapping[str, Any]) -> Dict[str, Any]:
    report = {
        "record_type": "s39_manual_promotion_plateau_report",
        "version": "v19.89.8-S39R13-R16",
        "plateau": "S39 manual promotion candidate governance",
        "status": "plateau_ready" if replay_report.get("replay_ok") is True else "replay_failed",
        "candidate_count": index.get("candidate_count", 0),
        "blocked_count": blocked_registry.get("blocked_count", 0),
        "replay_ok": replay_report.get("replay_ok") is True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
        "manual_promotion_required": True,
        "next_phase": "S40 backend truth surfaces for cockpit consumption",
        "created_at": _utc_now(),
    }
    report["plateau_report_sha256"] = _sha256(report)
    return report


def build_s39_plateau_artifacts(readiness_ledger: Path, decision_ledger: Path, output_dir: Path) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    readiness_rows = _read_jsonl(readiness_ledger)
    decision_rows = _read_jsonl(decision_ledger)

    index = build_promotion_package_index(readiness_rows, decision_rows)
    blocked = build_blocked_candidate_registry(readiness_rows)
    replay = verify_promotion_replay(index, readiness_rows, decision_rows)
    plateau = build_s39_plateau_report(index, blocked, replay)

    files = {
        "package_index": output_dir / "manual_promotion_package_index.json",
        "blocked_registry": output_dir / "blocked_promotion_candidate_registry.json",
        "replay_report": output_dir / "promotion_package_replay_verification.json",
        "plateau_report": output_dir / "s39_manual_promotion_plateau_report.json",
    }
    files["package_index"].write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    files["blocked_registry"].write_text(json.dumps(blocked, indent=2, sort_keys=True), encoding="utf-8")
    files["replay_report"].write_text(json.dumps(replay, indent=2, sort_keys=True), encoding="utf-8")
    files["plateau_report"].write_text(json.dumps(plateau, indent=2, sort_keys=True), encoding="utf-8")

    return {key: str(value) for key, value in files.items()}
