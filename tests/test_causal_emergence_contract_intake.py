from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_causal_contract_traces_all_26_uploaded_files():
    from claire.emergence.causal_contracts import build_causal_contract

    contract = build_causal_contract()

    assert contract["status"] == "ready"
    assert contract["source_file_count"] == 26
    assert contract["thresholds"]["global_similarity"] == 0.65
    for source_file in contract["source_files"]:
        assert Path(source_file).exists()


def test_portfolio_conditions_activate_portfolio_route():
    from claire.emergence.causal_contracts import assess_causal_emergence
    from claire.lifecycle.canonical_paths import PORTFOLIO_ROUTE

    result = assess_causal_emergence(
        {
            "market": {"unmet_demand": 0.58},
            "enabling": {
                "demand_pressure": 0.58,
                "performance_breakthrough": 0.10,
                "cost_collapse": 0.10,
            },
            "similarity": 0.20,
        }
    )

    assert result["route_selected"] == PORTFOLIO_ROUTE
    assert result["route_selected_id"] == "portfolio"
    assert result["momentum"] < 0.55


def test_breakthrough_conditions_activate_breakthrough_route():
    from claire.emergence.causal_contracts import assess_causal_emergence
    from claire.lifecycle.canonical_paths import BREAKTHROUGH_ESCALATION_ROUTE

    result = assess_causal_emergence(
        {
            "enabling": {
                "demand_pressure": 0.80,
                "performance_breakthrough": 0.78,
                "cost_collapse": 0.70,
                "infrastructure_maturity": 0.76,
                "capital_flow": 0.68,
                "cultural_shift": 0.72,
            },
            "similarity": 0.40,
        }
    )

    assert result["route_selected"] == BREAKTHROUGH_ESCALATION_ROUTE
    assert result["route_selected_id"] == "breakthrough"
    assert result["momentum"] >= 0.55


def test_tech_design_build_conditions_activate_design_route_after_required_stage_chain():
    from claire.emergence.causal_contracts import assess_causal_emergence
    from claire.lifecycle.canonical_paths import BREAKTHROUGH_DESIGN_ROUTE

    result = assess_causal_emergence(
        {
            "breakthrough_trigger": "technological",
            "technological": {"manufacturability": 0.71, "scientific_readiness": 0.73},
            "enabling": {
                "demand_pressure": 0.80,
                "performance_breakthrough": 0.78,
                "cost_collapse": 0.70,
                "infrastructure_maturity": 0.76,
            },
            "stage_readiness": {
                "trend_discovery_complete": True,
                "discovery_complete": True,
                "breakthrough_complete": True,
            },
        }
    )

    route_ids = {item["route_id"] for item in result["route_vector"]}
    assert "tech_design_build" in route_ids
    assert any(item["route"] == BREAKTHROUGH_DESIGN_ROUTE for item in result["route_vector"])


def test_weak_breakthrough_stays_portfolio_discovery_only():
    from claire.emergence.causal_contracts import assess_causal_emergence
    from claire.lifecycle.canonical_paths import PORTFOLIO_ROUTE

    result = assess_causal_emergence(
        {
            "breakthrough_trigger": "technological",
            "market": {"unmet_demand": 0.52},
            "technological": {"manufacturability": 0.40, "scientific_readiness": 0.42},
            "enabling": {
                "demand_pressure": 0.52,
                "performance_breakthrough": 0.30,
                "cost_collapse": 0.20,
            },
            "similarity": 0.35,
        }
    )

    assert result["route_selected"] == PORTFOLIO_ROUTE
    assert {item["route_id"] for item in result["route_vector"]} == {"portfolio"}


def test_insufficient_data_produces_insufficient_data_not_fake_output():
    from claire.emergence.causal_contracts import assess_causal_emergence

    result = assess_causal_emergence({})

    assert result["status"] == "insufficient_data"
    assert result["route_selected"] == "insufficient_data"
    assert result["route_vector"] == []


def test_multiple_valid_routes_produce_route_vector_not_random_single_route():
    from claire.emergence.causal_contracts import assess_causal_emergence

    result = assess_causal_emergence(
        {
            "breakthrough_trigger": "technological",
            "system_failures": ["legacy system collapse"],
            "market": {"competitive_gap": 0.82, "unmet_demand": 0.88},
            "economic": {"capital_inflow": 0.84},
            "technological": {"manufacturability": 0.72, "scientific_readiness": 0.75},
            "enabling": {
                "demand_pressure": 0.88,
                "performance_breakthrough": 0.82,
                "cost_collapse": 0.78,
                "infrastructure_maturity": 0.78,
                "capital_flow": 0.84,
                "cultural_shift": 0.75,
            },
            "similarity": 0.72,
            "stage_readiness": {
                "trend_discovery_complete": True,
                "discovery_complete": True,
                "breakthrough_complete": True,
            },
        }
    )

    assert result["route_selected"] == "route_vector"
    assert result["route_selected_id"] == "route_vector"
    assert result["active_route_count"] >= 3
    assert {"breakthrough", "tech_design_build", "acquisition", "system_replacement"}.issubset(
        {item["route_id"] for item in result["route_vector"]}
    )


def test_design_cad_route_does_not_activate_before_trend_discovery_breakthrough():
    from claire.emergence.causal_contracts import assess_causal_emergence
    from claire.lifecycle.canonical_paths import BREAKTHROUGH_DESIGN_ROUTE

    result = assess_causal_emergence(
        {
            "breakthrough_trigger": "technological",
            "technological": {"manufacturability": 0.80, "scientific_readiness": 0.81},
            "enabling": {
                "demand_pressure": 0.75,
                "performance_breakthrough": 0.80,
                "cost_collapse": 0.70,
                "infrastructure_maturity": 0.70,
            },
            "stage_readiness": {
                "trend_discovery_complete": True,
                "discovery_complete": False,
                "breakthrough_complete": False,
            },
        }
    )

    assert not any(item["route"] == BREAKTHROUGH_DESIGN_ROUTE and not item.get("blocked") for item in result["route_vector"])
    assert any(item["route_id"] == "tech_design_build_blocked" for item in result["route_vector"])


def test_causal_contract_endpoints_are_mounted():
    from claire.app import create_app

    client = TestClient(create_app())

    contract = client.get("/api/emergence/causal-contract")
    assessed = client.post("/api/emergence/causal-assess", json={"market": {"unmet_demand": 0.50}})

    assert contract.status_code == 200
    assert contract.json()["source_file_count"] == 26
    assert assessed.status_code == 200
    assert assessed.json()["status"] == "ready"
