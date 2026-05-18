from __future__ import annotations

from pathlib import Path

from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_cockpit_payload_read_contract,
    build_live_payload_visibility_probe,
    build_existing_payload_nonbreak_probe,
    build_repeated_payload_fetch_stability_probe,
    build_cockpit_payload_manifest,
    build_cockpit_live_visibility_readiness,
    build_s149_s155_stop_gate,
)

def test_s149_read_contract_ready():
    contract = build_cockpit_payload_read_contract()
    assert contract["stage_version"] == "S149"
    assert contract["status"] == "cockpit_payload_read_contract_ready"
    assert contract["payload_key"] == "governed_operations"
    assert contract["read_only"] is True

def test_s150_visibility_probe_passes():
    probe = build_live_payload_visibility_probe()
    assert probe["stage_version"] == "S150"
    assert probe["ok"] is True
    assert "runtime_spine" in probe["visible_panel_keys"]
    assert "review_export" in probe["visible_panel_keys"]

def test_s151_existing_payload_nonbreak_probe():
    probe = build_existing_payload_nonbreak_probe()
    assert probe["stage_version"] == "S151"
    assert probe["ok"] is True
    assert probe["rules"]["governed_operations_appended_only"] is True
    assert probe["rules"]["app_py_patch_performed"] is False

def test_s152_repeated_fetch_stability():
    probe = build_repeated_payload_fetch_stability_probe(fetch_count=3)
    assert probe["stage_version"] == "S152"
    assert probe["ok"] is True
    assert probe["stable_top_level_keys"] is True
    assert probe["stable_panel_keys"] is True

def test_s153_payload_manifest_ready():
    manifest = build_cockpit_payload_manifest()
    assert manifest["stage_version"] == "S153"
    assert manifest["status"] == "cockpit_payload_manifest_ready"
    assert manifest["panel_count"] >= 4

def test_s154_live_visibility_readiness():
    readiness = build_cockpit_live_visibility_readiness()
    assert readiness["stage_version"] == "S154"
    assert readiness["ok"] is True
    assert readiness["checks"]["runtime_truth_write_blocked"] is True

def test_s155_stop_gate_passes(tmp_path: Path):
    report = build_s149_s155_stop_gate(report_dir=tmp_path / "reports")
    assert report["stage_version"] == "S155"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["remaining_countdown"]["packs_remaining_after_this"] == 3
    assert Path(report["report_path"]).exists()
