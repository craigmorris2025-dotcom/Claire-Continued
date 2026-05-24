from __future__ import annotations

import importlib


def test_s44r1_fetch_contracts_are_backend_truth_read_only():
    module = importlib.import_module("runtime_core.api.s44_cockpit_fetch_contracts")
    payload = module.build_cockpit_fetch_contracts()

    assert payload["version"] == "v19.89.8-S44R1-R8"
    assert payload["status"] == "cockpit_fetch_contracts_ready"
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["contract_count"] == 7

    for contract in payload["contracts"]:
        assert contract["method"] == "GET"
        assert contract["expected_status"] == 200
        assert contract["read_only"] is True
        assert contract["runtime_truth_mutation_allowed"] is False
        assert contract["operator_mutation_enabled"] is False
        assert contract["response_mode"] == "read_only_artifact"


def test_s44r2_fetch_contracts_verify_cleanly():
    module = importlib.import_module("runtime_core.api.s44_cockpit_fetch_contracts")
    verification = module.verify_cockpit_fetch_contracts()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert "/operator/payload" in verification["paths"]
    assert "/operator/routes/status" in verification["paths"]
