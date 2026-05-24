from __future__ import annotations

import importlib


def test_continuous_lifecycle_activation_gate_proves_memory_dashboard_and_readiness(tmp_path, monkeypatch):
    runtime = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    readiness = importlib.import_module("runtime_core.platform.operational_readiness")
    dashboard = importlib.import_module("runtime_core.dashboard.cockpit_dashboard_state")

    monkeypatch.setattr(runtime, "CONTINUOUS_DIR", tmp_path / "data" / "continuous_runtime")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "continuous_runtime").mkdir(parents=True, exist_ok=True)

    payload = runtime.create_cycle_payload(trigger="continuous_lifecycle_gate_test")
    current_run = runtime.read_json(runtime.CONTINUOUS_DIR / "current_run.json", {})

    assert payload["cycle"]["candidate_counts"]["discoveries"] >= 1
    assert payload["cycle"]["candidate_counts"]["portfolios"] >= 1
    assert payload["cycle"]["candidate_counts"]["packages"] >= 1
    assert current_run["route_selected"] in {"portfolio_creation_optimization", "breakthrough_design"}
    assert current_run["advancement_path_decision"]["route_selected"] == current_run["route_selected"]
    assert current_run["quality_gate"]["fresh_input_present"] is True
    assert current_run["quality_gate"]["portfolio_candidate_present"] is True
    assert current_run["quality_gate"]["advancement_path_selected"] is True
    assert current_run["quality_gate"]["design_candidate_present"] is (current_run["route_selected"] == "breakthrough_design")
    assert current_run["quality_gate"]["acquisition_rationale_present"] is True
    assert current_run["quality_gate"]["lifecycle_memory_written"] is True
    assert current_run["authority"]["body_read_performed"] is False
    assert current_run["authority"]["runtime_truth_mutated"] is False

    ready = readiness.build_operational_readiness(tmp_path)
    assert ready["checks"]["current_run_spine_present"] is True
    assert ready["checks"]["advancement_path_policy_respected"] is True
    assert ready["checks"]["portfolio_candidates_present"] is True
    assert ready["checks"]["lifecycle_memory_records_present"] is True
    assert ready["current_run_truth"]["status"] == "valid_continuous_lifecycle_snapshot"

    state = dashboard.build_cockpit_dashboard_state(tmp_path)
    assert state["current_run_truth"]["route_selected"] == current_run["route_selected"]
    assert state["lifecycle"]["stage_count"] == 30
    assert state["records"]["portfolio"]
    assert state["records"]["deals"]
    assert state["records"]["learning"]
    assert state["post_run_handoff"]["route_selected"] == current_run["route_selected"]
