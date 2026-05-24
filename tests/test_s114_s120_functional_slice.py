from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_functional_slice_s114_s120 import (
    build_evidence_to_lifecycle_bridge,
    build_approved_evidence_run_contract,
    build_dashboard_operations_fetch_map,
    build_review_export_control_backend,
    build_governed_search_control_backend,
    build_dashboard_managed_demo_backend,
    build_s114_s120_stop_gate,
)

def test_s114_evidence_to_lifecycle_bridge_ready():
    bridge = build_evidence_to_lifecycle_bridge()
    assert bridge["stage_version"] == "S114"
    assert bridge["status"] == "evidence_to_lifecycle_bridge_ready"
    assert bridge["runtime_truth_write"] == "blocked"
    assert "Discovery Generation" in bridge["mapping"].values()

def test_s115_approved_evidence_run_contract_exports(tmp_path: Path):
    contract = build_approved_evidence_run_contract(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert contract["stage_version"] == "S115"
    assert contract["status"] == "approved_evidence_run_contract_ready"
    assert contract["decision"]["decision"] == "approved"
    assert contract["export"]["status"] == "exported"
    assert Path(contract["export"]["path"]).exists()

def test_s116_dashboard_operations_fetch_map_locked():
    fetch_map = build_dashboard_operations_fetch_map()
    assert fetch_map["stage_version"] == "S116"
    assert fetch_map["status"] == "dashboard_operations_fetch_map_locked"
    assert fetch_map["read_only"] is True
    assert fetch_map["app_patch_performed"] is False
    assert fetch_map["route_registration_performed"] is False

def test_s117_review_export_control_backend_ready(tmp_path: Path):
    control = build_review_export_control_backend(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert control["stage_version"] == "S117"
    assert control["status"] == "review_export_control_backend_ready"
    assert control["manual_operator_only"] is True
    assert control["latest_export"]["status"] == "exported"

def test_s118_governed_search_control_backend_ready():
    search = build_governed_search_control_backend()
    assert search["stage_version"] == "S118"
    assert search["status"] == "governed_search_control_backend_ready"
    assert search["manual_probe_required"] is True
    assert search["continuous_crawling"] == "blocked"
    assert search["automatic_updates"] == "blocked"

def test_s119_dashboard_managed_demo_backend_ready(tmp_path: Path):
    demo = build_dashboard_managed_demo_backend(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert demo["stage_version"] == "S119"
    assert demo["status"] == "dashboard_managed_demo_backend_ready"
    assert demo["app_patch_performed"] is False
    assert demo["route_registration_performed"] is False
    assert demo["approved_run"]["export"]["status"] == "exported"

def test_s120_stop_gate_passes_and_writes_report(tmp_path: Path):
    report = build_s114_s120_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["stage_version"] == "S120"
    assert report["ok"] is True
    assert report["status"] == "s114_s120_stop_gate_passed"
    assert report["forward_motion_allowed"] is True
    assert Path(report["report_path"]).exists()
