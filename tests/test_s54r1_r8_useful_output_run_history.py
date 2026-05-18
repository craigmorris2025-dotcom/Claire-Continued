from __future__ import annotations

import importlib

def test_s54r1_persistence_contract_is_manual_review_only():
    module = importlib.import_module("claire.api.s54_useful_output_run_history")
    payload = module.build_useful_output_persistence_contract()
    assert payload["version"] == "v19.89.8-S54R1-R8"
    assert payload["status"] == "useful_output_persistence_contract_ready"
    assert payload["record_count"] == 7
    assert payload["runtime_truth_write_allowed"] is False
    assert payload["runtime_truth_mutation_allowed"] is False
    for record in payload["records"]:
        assert record["storage_mode"] == "contract_only_no_runtime_write"
        assert record["requires_manual_review"] is True
        assert record["runtime_truth_write_allowed"] is False
        assert record["auto_persist_enabled"] is False
        assert record["auto_promotion_enabled"] is False

def test_s54r4_run_history_integration_is_visible_without_mutation():
    module = importlib.import_module("claire.api.s54_useful_output_run_history")
    payload = module.build_run_history_integration_contract()
    assert payload["status"] == "run_history_integration_contract_ready"
    assert payload["history_item_count"] == 7
    for item in payload["history_items"]:
        assert item["display_state"] == "visible_in_run_history"
        assert item["review_state"] == "operator_review_required"
        assert item["runtime_truth_write_allowed"] is False
        assert item["auto_update_history_enabled"] is False

def test_s54r8_plateau_report_ready():
    module = importlib.import_module("claire.api.s54_useful_output_run_history")
    report = module.build_s54r1_r8_plateau_report()
    assert report["status"] == "s54r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S55 useful output replay and snapshot registry"
