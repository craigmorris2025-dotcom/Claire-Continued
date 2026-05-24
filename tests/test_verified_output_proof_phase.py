from __future__ import annotations

import importlib


def test_verified_output_proof_binder_maps_doc_acceptance_criteria(tmp_path, monkeypatch):
    runtime = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    proof = importlib.import_module("runtime_core.proof.verified_output_proof")

    monkeypatch.setattr(runtime, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    payload = runtime.create_cycle_payload(trigger="verified_output_proof_test")
    run_id = payload["cycle"]["cycle_id"]
    current_run = proof.read_json(tmp_path / "continuous_runtime" / "current_run.json", {})
    portfolio_payload = proof.read_json(
        runtime.PROJECT_ROOT / "data" / "continuous_runtime" / "artifacts" / "portfolio" / run_id / "portfolio_brief.json",
        {},
    )

    binder = proof.persist_verified_output_proof_binder(current_run, portfolio_payload, tmp_path)

    assert binder["schema_version"] == "claire.verified_output_proof_binder.v1"
    assert binder["status"] == "verified_output_proof_complete"
    assert binder["lifecycle_generation"]["status"] == "passed"
    assert binder["technology_route_proof"]["status"] == "passed"
    assert binder["portfolio_route_proof"]["status"] == "passed"
    assert binder["portfolio_route_proof"]["checks"]["weights_sum_to_100_percent"] is True
    assert binder["portfolio_route_proof"]["checks"]["market_prices_timestamped_and_verifiable"] is True
    assert binder["acceptance_targets"]["technology_pathway_generated_and_verified"] is True
    assert binder["acceptance_targets"]["portfolio_generated_and_finance_verified"] is True
    assert (tmp_path / "data" / "completion" / "final_binders" / run_id / "verified_output_proof_binder.json").exists()
