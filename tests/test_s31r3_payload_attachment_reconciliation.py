from __future__ import annotations

import importlib


def test_s31r3_reconciled_payload_includes_operational_keys():
    module = importlib.import_module("runtime_core.api.governed_payload_reconciliation")
    payload = module.compose_governed_payload({})

    required = {
        "governed_runtime_timeline",
        "governed_route_activity_overlay",
        "continuous_runtime_presence",
        "governed_search_session",
        "governed_evidence_basket",
        "runtime_continuity_visualization",
        "continuous_browser_runtime_loop",
        "governed_operator_workflow",
        "canonical_browser_session_persistence",
        "multi_panel_runtime_cohesion",
        "governed_operational_session_orchestration",
        "governed_runtime_workspace_continuity",
        "governed_multi_workspace_orchestration",
        "governed_operational_topology_continuity",
        "governed_payload_reconciliation",
    }

    missing = required.difference(payload.keys())
    assert not missing, missing


def test_s31r3_reconciliation_preserves_authority_blocks():
    module = importlib.import_module("runtime_core.api.governed_payload_reconciliation")
    payload = module.compose_governed_payload({})
    reconciliation = payload["governed_payload_reconciliation"]

    assert reconciliation["version"] == "v19.89.8-S31R3"
    assert reconciliation["authority"]["runtime_authority"] == "blocked"
    assert reconciliation["authority"]["browser_execution_authority"] == "blocked"
    assert reconciliation["authority"]["runtime_mutation_enabled"] is False
    assert reconciliation["authority"]["autonomous_execution_expansion"] is False


def test_s31r3_expected_keys_list_contains_topology():
    module = importlib.import_module("runtime_core.api.governed_payload_reconciliation")
    keys = module.expected_payload_keys()

    assert "governed_operational_topology_continuity" in keys
    assert "governed_payload_reconciliation" in keys


def test_s31r3_does_not_require_app_factory_patch():
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[1]
    app_file = root / "runtime_core" / "app.py"
    assert app_file.exists()
    text = app_file.read_text(encoding="utf-8")

    assert "v19.89.8-S31R3 governed optional route registration block" not in text
