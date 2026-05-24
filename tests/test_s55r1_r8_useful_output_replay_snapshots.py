from __future__ import annotations

import importlib

def test_s55r1_snapshot_registry_is_read_only():
    module = importlib.import_module("runtime_core.api.s55_useful_output_replay_snapshots")
    registry = module.build_output_replay_snapshot_registry()
    assert registry["version"] == "v19.89.8-S55R1-R8"
    assert registry["status"] == "output_replay_snapshot_registry_ready"
    assert registry["snapshot_count"] == 7
    for snapshot in registry["snapshots"]:
        assert snapshot["snapshot_state"] == "replay_ready"
        assert snapshot["replay_mode"] == "read_only_snapshot"
        assert snapshot["runtime_truth_write_allowed"] is False
        assert snapshot["replay_mutation_allowed"] is False
        assert snapshot["auto_replay_enabled"] is False

def test_s55r4_replay_contracts_require_manual_review():
    module = importlib.import_module("runtime_core.api.s55_useful_output_replay_snapshots")
    contracts = module.build_output_replay_contracts()
    assert contracts["status"] == "output_replay_contracts_ready"
    assert contracts["contract_count"] == 7
    for contract in contracts["contracts"]:
        assert contract["replay_action"] == "render_snapshot_for_review"
        assert contract["requires_manual_review"] is True
        assert contract["runtime_truth_write_allowed"] is False
        assert contract["replay_mutation_allowed"] is False
        assert contract["auto_promotion_enabled"] is False

def test_s55r8_plateau_report_ready():
    module = importlib.import_module("runtime_core.api.s55_useful_output_replay_snapshots")
    report = module.build_s55r1_r8_plateau_report()
    assert report["status"] == "s55r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S56 output package export manifest and review bundle"
