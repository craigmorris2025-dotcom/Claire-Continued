from __future__ import annotations

from pathlib import Path
import importlib

MODULES = [
    ("runtime_core.api.s57_output_dashboard_mounting", "build_s57r1_r8_plateau_report", "s57r1_r8_ready"),
    ("runtime_core.api.s58_governed_web_provider_readiness", "build_s58r1_r8_plateau_report", "s58r1_r8_ready"),
    ("runtime_core.api.s59_controlled_probe_request_contracts", "build_s59r1_r8_plateau_report", "s59r1_r8_ready"),
    ("runtime_core.api.s60_quarantined_evidence_intake", "build_s60r1_r8_plateau_report", "s60r1_r8_ready"),
    ("runtime_core.api.s61_manual_promotion_workflow", "build_s61r1_r8_plateau_report", "s61r1_r8_ready"),
    ("runtime_core.api.s62_governed_update_readiness_boundary", "build_s62r1_r8_plateau_report", "s62r1_r8_ready"),
    ("runtime_core.api.s63_demonstrable_platform_readiness", "build_s63r1_r8_plateau_report", "s63r1_r8_ready"),
]

def test_s57_s63_all_plateaus_ready_and_safe():
    for module_name, fn_name, expected_status in MODULES:
        module = importlib.import_module(module_name)
        report = getattr(module, fn_name)()
        assert report["status"] == expected_status
        assert report["ready"] is True
        assert report["backend_owns_truth"] is True
        assert report["cockpit_presentation_only"] is True
        assert report["runtime_truth_mutation_allowed"] is False
        assert report["runtime_truth_write_allowed"] is False
        assert report["operator_mutation_enabled"] is False
        assert report["automatic_updates_enabled"] is False
        assert report["autonomous_execution_enabled"] is False
        assert report["live_web_execution_enabled"] is False
        assert report["verification"]["verification_ok"] is True
        assert report["verification"]["failures"] == []

def test_s57_output_cards_are_mounted():
    module = importlib.import_module("runtime_core.api.s57_output_dashboard_mounting")
    manifest = module.build_output_dashboard_mounting_manifest()
    assert manifest["card_count"] == 7
    for card in manifest["cards"]:
        assert card["mounted"] is True
        assert card["visible_to_operator"] is True
        assert card["runtime_truth_mutation_allowed"] is False

def test_s58_s62_web_and_update_path_remains_blocked():
    provider = importlib.import_module("runtime_core.api.s58_governed_web_provider_readiness").build_provider_readiness_manifest()
    update = importlib.import_module("runtime_core.api.s62_governed_update_readiness_boundary").build_governed_update_readiness_boundary()
    for item in provider["providers"]:
        assert item["network_request_performed"] is False
        assert item["live_web_execution_enabled"] is False
    for gate in update["gates"]:
        assert gate["enables_updates"] is False
        assert gate["runtime_truth_write_allowed"] is False
    assert update["automatic_updates_enabled"] is False
    assert update["scheduled_updates_enabled"] is False

def test_s63_readiness_snapshot_is_honest_and_asset_exists():
    module = importlib.import_module("runtime_core.api.s63_demonstrable_platform_readiness")
    snapshot = module.build_demonstrable_platform_readiness_snapshot()
    assert snapshot["status"] == "demonstrable_platform_readiness_snapshot_ready"
    assert snapshot["dashboard_demo_ready"] is True
    assert snapshot["useful_outputs_demo_ready"] is True
    assert snapshot["controlled_web_demo_visible"] is True
    assert snapshot["automatic_updates_enabled"] is False
    assert snapshot["runtime_truth_mutation_allowed"] is False
    asset = Path(__file__).resolve().parents[1] / "frontend" / "cockpit" / "modern_shell" / "claire_s57_s63_platform_readiness.js"
    assert asset.exists()
    text = asset.read_text(encoding="utf-8")
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "scheduledUpdatesEnabled: false" in text
