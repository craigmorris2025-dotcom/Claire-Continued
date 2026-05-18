from __future__ import annotations

from pathlib import Path

from claire.api.governed_payload_registry_s135_s141 import (
    build_governed_operations_registry_entry,
    build_payload_registry_preview,
    build_existing_payload_bridge_contract,
    build_payload_stability_probe,
    build_existing_cockpit_nonbreak_contract,
    build_readonly_surface_validation,
    build_s135_s141_stop_gate,
)

def test_s135_registry_entry_ready(tmp_path: Path):
    entry = build_governed_operations_registry_entry(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert entry["stage_version"] == "S135"
    assert entry["registry_key"] == "governed_operations"
    assert entry["read_only"] is True
    assert entry["rollback"]["safe_to_remove"] is True

def test_s136_registry_preview_ready(tmp_path: Path):
    preview = build_payload_registry_preview(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert preview["stage_version"] == "S136"
    assert "governed_operations" in preview["registry"]
    assert preview["live_registry_write_performed"] is False
    assert preview["app_patch_performed"] is False

def test_s137_bridge_contract_ready():
    contract = build_existing_payload_bridge_contract()
    assert contract["stage_version"] == "S137"
    assert contract["merge_contract"]["preserve_existing_payload"] is True
    assert contract["merge_contract"]["overwrite_existing_keys"] is False
    assert contract["requires_app_patch"] is False

def test_s138_payload_stability_probe(tmp_path: Path):
    probe = build_payload_stability_probe(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert probe["stage_version"] == "S138"
    assert probe["ok"] is True
    assert probe["live_fetch_required"] is False

def test_s139_existing_cockpit_nonbreak_contract():
    contract = build_existing_cockpit_nonbreak_contract()
    assert contract["stage_version"] == "S139"
    assert contract["rules"]["preserve_existing_dashboard_payload"] is True
    assert contract["rules"]["no_dom_rewrite"] is True

def test_s140_readonly_surface_validation(tmp_path: Path):
    validation = build_readonly_surface_validation(store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert validation["stage_version"] == "S140"
    assert validation["ok"] is True
    assert validation["checks"]["panels_read_only"] is True

def test_s141_stop_gate_passes(tmp_path: Path):
    report = build_s135_s141_stop_gate(
        report_dir=tmp_path / "reports",
        store_path=tmp_path / "review.json",
        export_dir=tmp_path / "exports",
    )
    assert report["stage_version"] == "S141"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["next_allowed_phase"] == "S142 controlled live payload bridge adapter patch"
    assert Path(report["report_path"]).exists()
