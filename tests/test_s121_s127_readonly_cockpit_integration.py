from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_readonly_cockpit_integration_s121_s127 import (
    build_runtime_spine_cockpit_panel,
    build_review_export_cockpit_panel,
    build_governed_search_cockpit_panel,
    build_evidence_demo_cockpit_panel,
    build_consolidated_readonly_cockpit_payload,
    validate_consolidated_readonly_cockpit_payload,
    build_s121_s127_stop_gate,
)

def test_s121_runtime_spine_panel_ready(tmp_path: Path):
    panel = build_runtime_spine_cockpit_panel(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert panel["panel_id"] == "runtime_spine"
    assert panel["read_only"] is True
    assert panel["runtime_truth_write"] == "blocked"

def test_s122_review_export_panel_ready(tmp_path: Path):
    panel = build_review_export_cockpit_panel(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert panel["panel_id"] == "review_export"
    assert panel["read_only"] is True
    assert panel["data"]["manual_operator_only"] is True
    assert panel["data"]["latest_export"]["status"] == "exported"

def test_s123_governed_search_panel_ready():
    panel = build_governed_search_cockpit_panel()
    assert panel["panel_id"] == "governed_search"
    assert panel["data"]["manual_probe_required"] is True
    assert panel["data"]["continuous_crawling"] == "blocked"
    assert panel["data"]["automatic_updates"] == "blocked"

def test_s124_evidence_demo_panel_ready(tmp_path: Path):
    panel = build_evidence_demo_cockpit_panel(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert panel["panel_id"] == "evidence_demo"
    assert panel["data"]["bridge_status"] == "evidence_to_lifecycle_bridge_ready"
    assert panel["data"]["approved_run_status"] == "approved_evidence_run_contract_ready"
    assert panel["data"]["export_status"] == "exported"

def test_s125_s126_consolidated_payload_ready(tmp_path: Path):
    payload = build_consolidated_readonly_cockpit_payload(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert payload["cockpit_payload_version"] == "S121-S127"
    assert payload["status"] == "readonly_cockpit_payload_ready"
    assert payload["read_only"] is True
    assert payload["live_dashboard_rewire_performed"] is False
    assert set(payload["panels"].keys()) == {"runtime_spine", "review_export", "governed_search", "evidence_demo"}

def test_s127_validation_and_stop_gate_pass(tmp_path: Path):
    payload = build_consolidated_readonly_cockpit_payload(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    validation = validate_consolidated_readonly_cockpit_payload(payload)
    assert validation["validation_version"] == "S127"
    assert validation["ok"] is True
    report = build_s121_s127_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert Path(report["report_path"]).exists()
