from __future__ import annotations

import importlib


def test_s45r1_ui_bridge_manifest_preserves_backend_truth():
    module = importlib.import_module("runtime_core.api.s45_cockpit_ui_bridge")
    manifest = module.build_cockpit_ui_bridge_manifest()

    assert manifest["version"] == "v19.89.8-S45R1-R8"
    assert manifest["status"] == "cockpit_ui_bridge_manifest_ready"
    assert manifest["bridge_surface_count"] == 7
    assert manifest["backend_owns_truth"] is True
    assert manifest["cockpit_presentation_only"] is True
    assert manifest["runtime_truth_mutation_allowed"] is False

    for surface in manifest["bridge_surfaces"]:
        assert surface["method"] == "GET"
        assert surface["presentation_only"] is True
        assert surface["runtime_truth_mutation_allowed"] is False
        assert surface["operator_mutation_enabled"] is False
        assert surface["javascript_execution_authority"] == "presentation_only"


def test_s45r2_ui_bridge_manifest_verifies_cleanly():
    module = importlib.import_module("runtime_core.api.s45_cockpit_ui_bridge")
    verification = module.verify_cockpit_ui_bridge_manifest()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["bridge_surface_count"] == 7
    assert verification["cockpit_presentation_only"] is True
