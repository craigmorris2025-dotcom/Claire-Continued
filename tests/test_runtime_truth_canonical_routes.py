from runtime_core.runtime_truth.graph import decide_runtime_route
from runtime_core.runtime_truth.runtime_truth_contract import normalize_route


def test_runtime_truth_decision_emits_canonical_portfolio_route():
    decision = decide_runtime_route("market trend thesis portfolio optimization")

    assert decision["route"] == "portfolio_creation_optimization"
    assert decision["terminal_state"] == "portfolio_optimization_ready"


def test_runtime_truth_decision_emits_canonical_breakthrough_design_route():
    decision = decide_runtime_route("breakthrough patent prototype manufacturability feasibility")

    assert decision["route"] == "breakthrough_design"
    assert decision["terminal_state"] == "design_output_ready"


def test_runtime_truth_decision_emits_canonical_acquisition_route():
    decision = decide_runtime_route("acquisition acquirer buyer strategic fit deal")

    assert decision["route"] == "acquisition_package"
    assert decision["terminal_state"] == "acquisition_ready"


def test_runtime_truth_normalizes_legacy_route_names_to_canonical_routes():
    assert normalize_route("portfolio_intelligence") == "portfolio_creation_optimization"
    assert normalize_route("breakthrough_system_transformation") == "breakthrough_design"
    assert normalize_route("acquisition_intelligence") == "acquisition_package"
