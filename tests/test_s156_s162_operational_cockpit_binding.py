from __future__ import annotations

from pathlib import Path

from claire.api.governed_operational_cockpit_binding_s156_s162 import (
    build_surface_binding,
    build_all_surface_bindings,
    build_surface_render_contracts,
    build_surface_action_visibility_contract,
    build_surface_continuity_probe,
    build_operational_cockpit_binding_preview,
    build_s156_s162_stop_gate,
)

def test_s156_single_surface_binding_ready():
    binding = build_surface_binding("runtime_spine_surface")
    assert binding["stage_version"] == "S156"
    assert binding["status"] == "surface_binding_ready"
    assert binding["read_only"] is True
    assert binding["runtime_truth_write"] == "blocked"

def test_s157_all_surface_bindings_ready():
    bindings = build_all_surface_bindings()
    assert bindings["stage_version"] == "S157"
    assert bindings["ok"] is True
    assert bindings["surface_count"] == 4

def test_s158_render_contracts_ready():
    contracts = build_surface_render_contracts()
    assert contracts["stage_version"] == "S158"
    assert contracts["ok"] is True
    for contract in contracts["contracts"].values():
        assert contract["read_only"] is True
        assert contract["has_required_fields"] is True

def test_s159_action_visibility_contract_ready():
    contract = build_surface_action_visibility_contract()
    assert contract["stage_version"] == "S159"
    assert contract["read_only_phase"] is True
    assert contract["actions"]["review_export_surface"]["execution_enabled"] is False

def test_s160_surface_continuity_probe():
    probe = build_surface_continuity_probe()
    assert probe["stage_version"] == "S160"
    assert probe["ok"] is True
    assert probe["surface_keys_stable"] is True

def test_s161_binding_preview_ready():
    preview = build_operational_cockpit_binding_preview()
    assert preview["stage_version"] == "S161"
    assert preview["ok"] is True
    assert preview["live_dashboard_rewire_performed"] is False
    assert preview["app_patch_performed"] is False

def test_s162_stop_gate_passes(tmp_path: Path):
    report = build_s156_s162_stop_gate(report_dir=tmp_path / "reports")
    assert report["stage_version"] == "S162"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["remaining_countdown"]["packs_remaining_after_this"] == 2
    assert Path(report["report_path"]).exists()
