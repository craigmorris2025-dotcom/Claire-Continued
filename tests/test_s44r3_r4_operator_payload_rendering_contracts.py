from __future__ import annotations

import importlib


def test_s44r3_rendering_contracts_are_presentation_only():
    module = importlib.import_module("claire.api.s44_operator_payload_rendering_contracts")
    payload = module.build_operator_rendering_contracts()

    assert payload["status"] == "operator_payload_rendering_contracts_ready"
    assert payload["render_mode"] == "read_only_operator_card"
    assert payload["presentation_only"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["render_contract_count"] == 7

    for contract in payload["render_contracts"]:
        assert contract["presentation_only"] is True
        assert contract["backend_owns_truth"] is True
        assert contract["runtime_truth_mutation_allowed"] is False
        assert contract["operator_mutation_enabled"] is False


def test_s44r4_render_operator_payload_wraps_without_mutation():
    module = importlib.import_module("claire.api.s44_operator_payload_rendering_contracts")
    rendered = module.render_operator_payload(
        "operator_runtime_status",
        {"status": "available", "sample": True},
    )

    assert rendered["surface_id"] == "operator_runtime_status"
    assert rendered["render_mode"] == "read_only_operator_card"
    assert rendered["presentation_only"] is True
    assert rendered["backend_owns_truth"] is True
    assert rendered["runtime_truth_mutation_allowed"] is False
    assert rendered["payload"]["sample"] is True

    verification = module.verify_operator_rendering_contracts()
    assert verification["verification_ok"] is True
    assert verification["failures"] == []
