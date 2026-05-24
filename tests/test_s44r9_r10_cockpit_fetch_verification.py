from __future__ import annotations

import importlib


def test_s44r9_fetch_verification_reaches_all_contract_paths():
    module = importlib.import_module("runtime_core.api.s44_cockpit_fetch_verification")
    report = module.verify_cockpit_fetch_contract_responses()

    assert report["version"] == "v19.89.8-S44R9-R16"
    assert report["status"] == "cockpit_fetch_verification_ready"
    assert report["verification_ok"] is True
    assert report["probe_count"] == 7
    assert report["ok_count"] == 7
    assert report["available_count"] == 7
    assert report["failure_count"] == 0
    assert report["failures"] == []
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["live_server_required"] is False

    for result in report["results"]:
        assert result["status_code"] == 200
        assert result["available"] is True
        assert result["mutating"] is False
        assert result["runtime_truth_mutation_allowed"] is False
        assert result["response_mode"] == "read_only_artifact"


def test_s44r10_fetch_verification_summary_is_clean():
    module = importlib.import_module("runtime_core.api.s44_cockpit_fetch_verification")
    summary = module.build_cockpit_fetch_verification_summary()

    assert summary["status"] == "all_fetch_contracts_available"
    assert summary["verification_ok"] is True
    assert summary["probe_count"] == 7
    assert summary["failure_count"] == 0
    assert summary["cockpit_presentation_only"] is True
