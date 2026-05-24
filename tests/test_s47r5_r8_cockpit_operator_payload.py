from __future__ import annotations

import importlib


def test_s47r5_cockpit_operator_payload_aggregates_panels_and_status():
    module = importlib.import_module("runtime_core.api.s47_cockpit_operator_payload")
    payload = module.build_cockpit_operator_payload()

    assert payload["version"] == "v19.89.8-S47R1-R8"
    assert payload["status"] == "cockpit_operator_payload_ready"
    assert payload["ready"] is True
    assert payload["operator_panel_count"] == 7
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["operator_mutation_enabled"] is False
    assert payload["failures"] == []

    for panel in payload["operator_panels"]:
        assert panel["state"] == "available"
        assert panel["mounted"] is True
        assert panel["renderable"] is True
        assert panel["runtime_truth_mutation_allowed"] is False
        assert panel["operator_mutation_enabled"] is False
        assert panel["response_mode"] == "read_only_artifact"


def test_s47r6_cockpit_operator_payload_verifies_cleanly():
    module = importlib.import_module("runtime_core.api.s47_cockpit_operator_payload")
    verification = module.verify_cockpit_operator_payload()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["operator_panel_count"] == 7


def test_s47r8_plateau_report_points_to_dashboard_browser():
    module = importlib.import_module("runtime_core.api.s47_cockpit_operator_payload")
    report = module.build_s47r1_r8_plateau_report()

    assert report["status"] == "s47r1_r8_ready"
    assert report["ready"] is True
    assert report["backend_owns_truth"] is True
    assert report["cockpit_presentation_only"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["next_phase"] == "S48 dashboard route and payload browser"
