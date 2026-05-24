from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_live_fetch_validation_s170_s176 import (
    build_repeated_live_fetch_validation,
    build_quarantine_continuity_validation,
    build_evidence_continuity_validation,
    build_review_continuity_validation,
    build_payload_continuity_under_review_load,
    build_operational_runtime_plateau_readiness,
    build_s170_s176_stop_gate,
)

def test_s170_repeated_live_fetch_validation():
    result = build_repeated_live_fetch_validation(fetch_count=3)
    assert result["stage_version"] == "S170"
    assert result["ok"] is True
    assert result["checks"]["panel_keys_stable"] is True
    assert result["checks"]["runtime_truth_write_blocked_all"] is True

def test_s171_quarantine_continuity_validation():
    result = build_quarantine_continuity_validation()
    assert result["stage_version"] == "S171"
    assert result["ok"] is True
    assert result["checks"]["discovery_quarantined"] is True
    assert result["checks"]["output_review_required"] is True

def test_s172_evidence_continuity_validation(tmp_path: Path):
    result = build_evidence_continuity_validation(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert result["stage_version"] == "S172"
    assert result["ok"] is True
    assert result["checks"]["source_evidence_ids_present"] is True
    assert result["checks"]["export_file_exists"] is True

def test_s173_review_continuity_validation(tmp_path: Path):
    result = build_review_continuity_validation(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert result["stage_version"] == "S173"
    assert result["ok"] is True
    assert result["decision_total"] >= 1

def test_s174_payload_continuity_under_review_load(tmp_path: Path):
    result = build_payload_continuity_under_review_load(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert result["stage_version"] == "S174"
    assert result["ok"] is True
    assert result["checks"]["panel_keys_unchanged"] is True

def test_s175_operational_runtime_plateau_readiness(tmp_path: Path):
    result = build_operational_runtime_plateau_readiness(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert result["stage_version"] == "S175"
    assert result["ok"] is True
    assert result["checks"]["automatic_updates_blocked"] is True
    assert result["checks"]["autonomous_execution_blocked"] is True

def test_s176_first_operational_plateau_stop_gate(tmp_path: Path):
    report = build_s170_s176_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["stage_version"] == "S176"
    assert report["ok"] is True
    assert report["status"] == "first_governed_operational_cockpit_plateau_passed"
    assert report["remaining_countdown"]["packs_remaining_after_this"] == 0
    assert report["remaining_countdown"]["milestone"] == "first usable governed operational cockpit plateau"
    assert Path(report["report_path"]).exists()
