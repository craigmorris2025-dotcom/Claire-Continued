from __future__ import annotations

import importlib


def test_s45r11_panel_data_mounting_contracts_are_read_only():
    module = importlib.import_module("runtime_core.api.s45_panel_data_mounting")
    contracts = module.build_panel_data_mounting_contracts()

    assert contracts["version"] == "v19.89.8-S45R9-R16"
    assert contracts["status"] == "panel_data_mounting_contracts_ready"
    assert contracts["contract_count"] == 7
    assert contracts["runtime_truth_mutation_allowed"] is False

    for contract in contracts["contracts"]:
        assert contract["method"] == "GET"
        assert contract["expected_status"] == 200
        assert contract["mount_state"] == "mounted"
        assert contract["runtime_truth_mutation_allowed"] is False
        assert contract["operator_mutation_enabled"] is False
        assert contract["response_mode"] == "read_only_artifact"


def test_s45r13_panel_data_mount_probe_reaches_read_only_routes():
    module = importlib.import_module("runtime_core.api.s45_panel_data_mounting")
    probe = module.probe_panel_data_mounts()

    assert probe["status"] == "panel_data_mount_probe_ready"
    assert probe["probe_count"] == 7
    assert probe["ok_count"] == 7
    assert probe["available_count"] == 7
    assert probe["failure_count"] == 0
    assert probe["failures"] == []
    assert probe["live_server_required"] is False

    for result in probe["results"]:
        assert result["available"] is True
        assert result["status_code"] == 200
        assert result["mounted"] is True
        assert result["renderable"] is True
        assert result["runtime_truth_mutation_allowed"] is False
        assert result["response_mode"] == "read_only_artifact"


def test_s45r15_r16_plateau_report_is_ready():
    module = importlib.import_module("runtime_core.api.s45_panel_data_mounting")
    report = module.build_s45r9_r16_plateau_report()

    assert report["version"] == "v19.89.8-S45R9-R16"
    assert report["status"] == "s45r9_r16_ready"
    assert report["ready"] is True
    assert report["failures"] == []
    assert report["backend_owns_truth"] is True
    assert report["cockpit_presentation_only"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["next_phase"] == "S46 modern cockpit layout consolidation and live status zones"
