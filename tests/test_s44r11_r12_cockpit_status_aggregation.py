from __future__ import annotations

import importlib


def test_s44r11_status_aggregation_preserves_blocked_authority():
    module = importlib.import_module("runtime_core.api.s44_cockpit_status_aggregation")
    aggregation = module.build_cockpit_status_aggregation()

    assert aggregation["version"] == "v19.89.8-S44R9-R16"
    assert aggregation["status"] == "cockpit_status_aggregation_ready"
    assert aggregation["ready"] is True
    assert aggregation["surface_count"] == 7
    assert aggregation["available_count"] == 7
    assert aggregation["failure_count"] == 0
    assert aggregation["failures"] == []
    assert aggregation["backend_owns_truth"] is True
    assert aggregation["cockpit_presentation_only"] is True
    assert aggregation["runtime_truth_mutation_allowed"] is False
    assert aggregation["operator_mutation_enabled"] is False
    assert aggregation["automatic_updates_enabled"] is False


def test_s44r12_status_tiles_are_presentation_only():
    module = importlib.import_module("runtime_core.api.s44_cockpit_status_aggregation")
    tiles = module.build_cockpit_status_tiles()

    assert tiles["status"] == "cockpit_status_tiles_ready"
    assert tiles["tile_count"] == 3
    assert tiles["backend_owns_truth"] is True
    assert tiles["cockpit_presentation_only"] is True

    for tile in tiles["tiles"]:
        assert tile["presentation_only"] is True
