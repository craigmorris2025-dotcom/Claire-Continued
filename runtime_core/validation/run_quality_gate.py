from __future__ import annotations

from typing import Any


GENERIC_MARKERS = (
    "portfolio opportunities cross-sector",
    "validated gap opportunity",
    "hidden signal / repricing opportunity",
    "qualified claire trend thesis",
    "buyer-pain validation",
    "workflow wedge validation",
)


def _nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _text_blob(payload: dict[str, Any]) -> str:
    user = payload.get("user_facing_result") if isinstance(payload.get("user_facing_result"), dict) else {}
    parts = [
        payload.get("route_selected"),
        user.get("headline"),
        user.get("summary"),
        _nested(user, "thesis", "thesis_statement"),
        _nested(user, "discovery", "opportunity_discovery", "opportunity_thesis"),
    ]
    return " ".join(str(part or "") for part in parts).lower()


def evaluate_run_quality(payload: dict[str, Any]) -> dict[str, Any]:
    source_authority = payload.get("source_authority") if isinstance(payload.get("source_authority"), dict) else {}
    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    source_count = int(source_authority.get("effective_source_count") or source_authority.get("source_count_from_knowledge_ingestion") or 0)
    live_evidence_present = bool(source_authority.get("live_evidence_present"))
    request_source_evidence_present = bool(source_authority.get("source_evidence_present"))
    evidence_present = live_evidence_present or request_source_evidence_present
    pending_live_validation = request_source_evidence_present and not live_evidence_present
    scores = source_authority.get("scores") if isinstance(source_authority.get("scores"), dict) else {}
    source_quality = float(scores.get("source_quality_score") or 0.0)
    coverage = float(scores.get("coverage_score") or 0.0)
    evidence_signal = float(scores.get("evidence_signal_score") or 0.0)
    text = _text_blob(payload)
    generic_hits = [marker for marker in GENERIC_MARKERS if marker in text]

    blockers: list[str] = []
    warnings: list[str] = []
    if not source_authority:
        blockers.append("missing_source_authority_contract")
    if not evidence_present:
        blockers.append("no_live_or_request_source_evidence")
    if source_count <= 0:
        blockers.append("no_source_count_from_knowledge_ingestion")
    if pending_live_validation:
        warnings.append("pending_live_validation")
    if source_quality < 0.45:
        warnings.append("low_source_quality")
    if coverage < 0.45:
        warnings.append("low_source_coverage")
    if evidence_signal < 0.45:
        warnings.append("weak_evidence_signal")
    if generic_hits:
        warnings.append("generic_output_markers_present")
    if validation.get("status") not in {None, "passed", "success", "valid", "complete"}:
        warnings.append("validation_not_clean")

    score = 1.0
    score -= 0.22 * len(blockers)
    score -= 0.08 * len(warnings)
    score = round(max(0.0, min(1.0, score)), 3)
    status = "valid_run" if score >= 0.72 and not blockers else "degraded_run"
    if status == "valid_run" and pending_live_validation:
        status = "local_source_seed_pending_live_validation"
    if score < 0.45 or blockers:
        status = "trash_run_blocked_from_truth"
    dashboard_truth_eligible = status in {"valid_run", "local_source_seed_pending_live_validation"}
    live_truth_eligible = status == "valid_run" and live_evidence_present

    return {
        "schema_version": "claire.run_quality_gate.v1",
        "status": status,
        "score": score,
        "blockers": blockers,
        "warnings": warnings,
        "generic_markers": generic_hits,
        "live_evidence_present": live_evidence_present,
        "request_source_evidence_present": request_source_evidence_present,
        "evidence_present": evidence_present,
        "pending_live_validation": pending_live_validation,
        "source_count": source_count,
        "source_quality_score": source_quality,
        "coverage_score": coverage,
        "evidence_signal_score": evidence_signal,
        "dashboard_truth_eligible": dashboard_truth_eligible,
        "live_truth_eligible": live_truth_eligible,
        "memory_feedback_eligible": live_truth_eligible,
        "reason": "Runs without source authority or source evidence are blocked; local source-backed seeds remain pending live validation.",
    }
