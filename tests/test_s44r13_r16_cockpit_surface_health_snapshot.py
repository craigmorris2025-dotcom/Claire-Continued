from __future__ import annotations

import importlib


def test_s44r13_surface_health_snapshot_is_available_and_read_only():
    module = importlib.import_module("runtime_core.api.s44_cockpit_surface_health_snapshot")
    snapshot = module.build_cockpit_surface_health_snapshot()

    assert snapshot["status"] == "cockpit_surface_health_snapshot_ready"
    assert snapshot["surface_count"] == 7
    assert snapshot["available_count"] == 7
    assert snapshot["backend_owns_truth"] is True
    assert snapshot["cockpit_presentation_only"] is True
    assert snapshot["runtime_truth_mutation_allowed"] is False

    for item in snapshot["surface_health"]:
        assert item["state"] == "available"
        assert item["status_code"] == 200
        assert item["read_only"] is True
        assert item["mutating"] is False
        assert item["runtime_truth_mutation_allowed"] is False
        assert item["response_mode"] == "read_only_artifact"


def test_s44r14_surface_health_verifies_cleanly():
    module = importlib.import_module("runtime_core.api.s44_cockpit_surface_health_snapshot")
    verification = module.verify_cockpit_surface_health_snapshot()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["surface_count"] == 7
    assert verification["available_count"] == 7


def test_s44r15_r16_plateau_report_is_ready():
    module = importlib.import_module("runtime_core.api.s44_cockpit_surface_health_snapshot")
    report = module.build_s44r9_r16_plateau_report()

    assert report["version"] == "v19.89.8-S44R9-R16"
    assert report["status"] == "s44r9_r16_ready"
    assert report["ready"] is True
    assert report["backend_owns_truth"] is True
    assert report["cockpit_presentation_only"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["failures"] == []
    assert report["next_phase"] == "S45 cockpit UI bridge and operator-visible panel wiring"
