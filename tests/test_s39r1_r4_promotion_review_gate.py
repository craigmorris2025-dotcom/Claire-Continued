from __future__ import annotations

import json
from pathlib import Path

from runtime_core.api.governed_promotion_review_gate import (
    LOCKED_AUTHORITY,
    build_promotion_review_gate,
    create_operator_decision_record,
    seal_manual_promotion_candidate,
    build_promotion_status_index,
    run_s39r1_r4_pipeline,
)


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _package(tmp_path: Path, blocked=False) -> Path:
    return _write_json(tmp_path / "output" / "manual_promotion_packages" / "CANDIDATE.manual_promotion_package.json", {"schema_version": "s38r12.manual_promotion_package.v1", "candidate_id": "CANDIDATE", "blocked_reasons": ["contradiction"] if blocked else [], "approval_checklist": ["verify evidence", "verify extraction"], "runtime_truth_mutated": False, "automatic_update_performed": False, "promotion_state": "not_promoted"})


def test_s39r1_review_gate_allows_only_when_package_unblocked(tmp_path: Path):
    package = _package(tmp_path, blocked=False)
    gate = build_promotion_review_gate(tmp_path, package)
    assert gate["schema_version"] == "s39r1.promotion_review_gate.v1"
    assert gate["gate_state"] == "operator_decision_allowed"
    assert gate["runtime_truth_mutated"] is False
    assert gate["automatic_update_performed"] is False
    assert gate["promotion_state"] == "not_promoted"


def test_s39r1_review_gate_blocks_blocked_package(tmp_path: Path):
    package = _package(tmp_path, blocked=True)
    gate = build_promotion_review_gate(tmp_path, package)
    assert gate["gate_state"] == "operator_decision_blocked"
    assert "contradiction" in gate["blocked_reasons"]


def test_s39r2_approval_requires_explicit_ack_and_unblocked_gate(tmp_path: Path):
    _package(tmp_path, blocked=False)
    build_promotion_review_gate(tmp_path)
    downgraded = create_operator_decision_record(tmp_path, decision="approved_for_future_controlled_promotion", operator_ack="NO", operator_id="tester")
    assert downgraded["decision_state"] == "approval_downgraded_fail_closed"
    assert downgraded["effective_decision"] == "needs_revision"
    assert downgraded["runtime_truth_mutated"] is False
    approved = create_operator_decision_record(tmp_path, decision="approved_for_future_controlled_promotion", operator_ack="YES", operator_id="tester", rationale="reviewed evidence lineage")
    assert approved["decision_state"] == "recorded"
    assert approved["effective_decision"] == "approved_for_future_controlled_promotion"
    assert approved["promotion_state"] == "not_promoted"


def test_s39r3_seals_approved_candidate_without_truth_mutation(tmp_path: Path):
    _package(tmp_path, blocked=False)
    build_promotion_review_gate(tmp_path)
    create_operator_decision_record(tmp_path, decision="approved_for_future_controlled_promotion", operator_ack="YES")
    sealed = seal_manual_promotion_candidate(tmp_path)
    assert sealed["schema_version"] == "s39r3.sealed_manual_promotion_candidate.v1"
    assert sealed["future_controlled_promotion_candidate"] is True
    assert sealed["runtime_truth_mutated"] is False
    assert sealed["automatic_update_performed"] is False
    assert sealed["promotion_state"] == "not_promoted"


def test_s39r4_status_index_is_dashboard_ready_but_presentation_only(tmp_path: Path):
    _package(tmp_path, blocked=False)
    build_promotion_review_gate(tmp_path)
    create_operator_decision_record(tmp_path, decision="approved_for_future_controlled_promotion", operator_ack="YES")
    seal_manual_promotion_candidate(tmp_path)
    index = build_promotion_status_index(tmp_path)
    assert index["schema_version"] == "s39r4.promotion_status_index.v1"
    assert index["dashboard_surface_ready"] is True
    assert index["counts"]["approved_future_controlled_promotion_candidates"] == 1
    assert index["runtime_truth_mutated"] is False
    assert index["automatic_update_performed"] is False
    assert index["locked_authority"] == LOCKED_AUTHORITY


def test_s39r1_r4_pipeline_preserves_all_forbidden_authority(tmp_path: Path):
    _package(tmp_path, blocked=False)
    result = run_s39r1_r4_pipeline(tmp_path, decision="approved_for_future_controlled_promotion", operator_ack="YES", operator_id="tester", rationale="manual review complete")
    assert result["status"] == "promotion_review_gate_pipeline_complete"
    assert result["runtime_truth_mutated"] is False
    assert result["automatic_update_performed"] is False
    assert result["manual_promotion_required"] is True
    assert result["locked_authority"] == LOCKED_AUTHORITY
