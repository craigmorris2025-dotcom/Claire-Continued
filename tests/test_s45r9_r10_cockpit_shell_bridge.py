from __future__ import annotations

import importlib


def test_s45r9_shell_bridge_manifest_mounts_operator_panels():
    module = importlib.import_module("runtime_core.api.s45_cockpit_shell_bridge")
    manifest = module.build_cockpit_shell_bridge_manifest()

    assert manifest["version"] == "v19.89.8-S45R9-R16"
    assert manifest["status"] == "cockpit_shell_bridge_manifest_ready"
    assert manifest["shell_mount_count"] == 7
    assert manifest["backend_owns_truth"] is True
    assert manifest["cockpit_presentation_only"] is True
    assert manifest["runtime_truth_mutation_allowed"] is False

    for mount in manifest["shell_mounts"]:
        assert mount["mounted"] is True
        assert mount["method"] == "GET"
        assert mount["presentation_only"] is True
        assert mount["runtime_truth_mutation_allowed"] is False
        assert mount["operator_mutation_enabled"] is False
        assert mount["response_mode"] == "read_only_artifact"


def test_s45r10_shell_bridge_manifest_verifies_cleanly():
    module = importlib.import_module("runtime_core.api.s45_cockpit_shell_bridge")
    verification = module.verify_cockpit_shell_bridge_manifest()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["shell_mount_count"] == 7
