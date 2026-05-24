from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_operator_actions_s163_s169 import (
    build_operator_action_contract,
    build_operator_review_action_preview,
    execute_guarded_operator_action,
    build_operator_action_audit_trail,
    build_export_lifecycle_proof,
    build_operator_action_rollback_contract,
    build_s163_s169_stop_gate,
)

def test_s163_operator_action_contract_ready():
    contract = build_operator_action_contract()
    assert contract["stage_version"] == "S163"
    assert contract["status"] == "operator_action_contract_ready"
    assert contract["manual_operator_only"] is True
    assert contract["runtime_truth_write"] == "blocked"

def test_s164_operator_review_action_preview_ready(tmp_path: Path):
    preview = build_operator_review_action_preview(store_path=tmp_path / "review.json")
    assert preview["stage_version"] == "S164"
    assert preview["status"] == "operator_review_action_preview_ready"
    assert preview["execution_performed"] is False
    assert preview["queue_total"] >= 1

def test_s165_guarded_operator_action_executes_and_exports(tmp_path: Path):
    preview = build_operator_review_action_preview(store_path=tmp_path / "review.json")
    result = execute_guarded_operator_action(
        preview["review_item"]["review_item_id"],
        "approve",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert result["stage_version"] == "S165"
    assert result["status"] == "guarded_operator_action_complete"
    assert result["runtime_truth_write"] == "blocked"
    assert result["export"]["status"] == "exported"
    assert Path(result["export"]["path"]).exists()

def test_s166_audit_trail_ready(tmp_path: Path):
    audit = build_operator_action_audit_trail(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert audit["stage_version"] == "S166"
    assert audit["status"] == "operator_action_audit_trail_ready"
    assert audit["decision_total"] >= 1
    assert len(audit["audit_events"]) == 3

def test_s167_export_lifecycle_proof_ready(tmp_path: Path):
    proof = build_export_lifecycle_proof(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert proof["stage_version"] == "S167"
    assert proof["ok"] is True
    assert proof["derived_artifact_only"] is True
    assert proof["runtime_truth_write"] == "blocked"

def test_s168_rollback_contract_ready():
    rollback = build_operator_action_rollback_contract()
    assert rollback["stage_version"] == "S168"
    assert rollback["rollback_supported"] is True
    assert rollback["runtime_truth_write"] == "blocked"

def test_s169_stop_gate_passes(tmp_path: Path):
    report = build_s163_s169_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["stage_version"] == "S169"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["remaining_countdown"]["packs_remaining_after_this"] == 1
    assert Path(report["report_path"]).exists()
