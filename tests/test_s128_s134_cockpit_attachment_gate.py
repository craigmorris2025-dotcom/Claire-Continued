from __future__ import annotations

from pathlib import Path

from claire.api.governed_cockpit_attachment_gate_s128_s134 import (
    build_attachment_eligibility_matrix,
    build_readonly_attachment_contract,
    build_cockpit_payload_merge_preview,
    build_fetch_contract_for_cockpit_attachment,
    build_visual_attachment_gate,
    build_attachment_governance_validation,
    build_s128_s134_stop_gate,
)

def test_s128_attachment_eligibility_matrix():
    matrix = build_attachment_eligibility_matrix()
    assert matrix["stage_version"] == "S128"
    assert "canonical_payload_fragment" in matrix["allowed_targets"]
    assert "direct_app_py_patch" in matrix["blocked_targets"]

def test_s129_readonly_attachment_contract_ready(tmp_path: Path):
    contract = build_readonly_attachment_contract(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert contract["stage_version"] == "S129"
    assert contract["status"] == "readonly_attachment_contract_ready"
    assert contract["app_patch_performed"] is False
    assert contract["route_registration_performed"] is False
    assert contract["runtime_truth_write"] == "blocked"

def test_s130_payload_merge_preview_ready(tmp_path: Path):
    preview = build_cockpit_payload_merge_preview(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert preview["stage_version"] == "S130"
    assert preview["status"] == "cockpit_payload_merge_preview_ready"
    assert preview["canonical_key"] == "governed_operations"
    assert "governed_operations" in preview["merged_payload_preview"]

def test_s131_fetch_contract_ready():
    contract = build_fetch_contract_for_cockpit_attachment()
    assert contract["stage_version"] == "S131"
    assert contract["read_only"] is True
    assert contract["operator_actions_execute_runtime_truth_write"] is False

def test_s132_visual_attachment_gate_blocks_live_rewire():
    gate = build_visual_attachment_gate()
    assert gate["stage_version"] == "S132"
    assert gate["allowed_now"] is False
    assert gate["direct_app_patch_allowed"] is False
    assert gate["live_dashboard_rewire_performed"] is False

def test_s133_attachment_governance_validation_passes(tmp_path: Path):
    validation = build_attachment_governance_validation(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert validation["stage_version"] == "S133"
    assert validation["ok"] is True
    assert validation["checks"]["visual_rewire_blocked"] is True
    assert validation["checks"]["no_app_patch"] is True

def test_s134_stop_gate_passes(tmp_path: Path):
    report = build_s128_s134_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["stage_version"] == "S134"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["next_allowed_phase"] == "S135 controlled payload registry integration without app.py patching"
    assert Path(report["report_path"]).exists()
