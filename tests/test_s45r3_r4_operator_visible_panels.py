from __future__ import annotations

import importlib


def test_s45r3_operator_visible_panel_bindings_are_read_only():
    module = importlib.import_module("runtime_core.api.s45_operator_visible_panels")
    bindings = module.build_operator_visible_panel_bindings()

    assert bindings["version"] == "v19.89.8-S45R1-R8"
    assert bindings["status"] == "operator_visible_panel_bindings_ready"
    assert bindings["panel_count"] == 7
    assert bindings["backend_owns_truth"] is True
    assert bindings["cockpit_presentation_only"] is True
    assert bindings["runtime_truth_mutation_allowed"] is False

    for panel in bindings["panels"]:
        assert panel["visible_to_operator"] is True
        assert panel["presentation_only"] is True
        assert panel["runtime_truth_mutation_allowed"] is False
        assert panel["operator_mutation_enabled"] is False
        assert panel["response_mode"] == "read_only_artifact"


def test_s45r4_operator_visible_panel_bindings_verify_cleanly():
    module = importlib.import_module("runtime_core.api.s45_operator_visible_panels")
    verification = module.verify_operator_visible_panel_bindings()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["panel_count"] == 7
