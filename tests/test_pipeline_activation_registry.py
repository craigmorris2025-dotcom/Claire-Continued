from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_pipeline_activation_registry_surfaces_existing_pipelines():
    from claire.pipeline.activation_registry import build_pipeline_activation_registry

    payload = build_pipeline_activation_registry()
    assert payload["status"] == "ready"
    assert payload["pipeline_count"] >= 10
    assert payload["activated_count"] >= 1
    assert payload["authority"]["network_request_performed"] is False
    ids = {item["id"] for item in payload["items"]}
    assert "technology_intelligence" in ids
    assert "technical_feasibility" in ids
    assert "portfolio_optimization" in ids
    for item in payload["items"]:
        assert item["owner_file"] == item["module"]
        assert item["what"]
        assert item["why"]
        assert item["when"]
        assert item["trigger"]
        assert item["score"]
        assert item["route"]
        assert item["sequence"]
        assert item["output"]
        assert item["failure_state"]
    assert payload["decision_layer"] == "ACS2 trigger-score-route execution map"
    assert payload["route_execution_map"]["technology_intelligence"]["route"] == "tech_design_build"


def test_acs2_trigger_score_route_selector_representative_routes():
    from claire.pipeline.activation_registry import select_pipeline_route

    portfolio = select_pipeline_route(
        {"trend_strength": 0.62, "portfolio_relevance": 0.71},
        "portfolio_signal_family",
    )
    design = select_pipeline_route(
        {"technology_signal": 0.7, "buildability_readiness": 0.66},
        "technical_breakthrough_classification",
    )
    acquisition = select_pipeline_route(
        {"moat": 0.74, "acquirer_fit": 0.7},
        "acquisition_signal_family",
    )

    assert portfolio["selected_route"] == "portfolio"
    assert "portfolio_optimization" in portfolio["pipeline_ids"]
    assert design["selected_route"] == "tech_design_build"
    assert "system_design" in design["pipeline_ids"]
    assert acquisition["selected_route"] == "acquisition"
    assert "acquirer_matching" in acquisition["pipeline_ids"]


def test_pipeline_activation_route_and_dashboard_binding():
    from claire.app import create_app

    client = TestClient(create_app())
    response = client.get("/api/pipelines/activation")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["pipeline_count"] >= 10

    dashboard = client.get("/api/dashboard/state").json()
    assert dashboard["pipeline_activation"]["status"] == "ready"
    assert dashboard["metrics"]["active_pipelines"]["value"] == payload["activated_count"]
    assert dashboard["metrics"]["pipeline_gaps"]["value"] == payload["placeholder_count"] + payload["failed_count"]


def test_dashboard_exposes_pipeline_activation_registry():
    js = Path("frontend/command_center/modern/claire_dashboard.js").read_text(encoding="utf-8")

    assert "Pipeline Activation Registry" in js
    assert "pipeline_activation" in js
    assert "Active Pipelines" in js
    assert "Pipeline Gaps" in js
