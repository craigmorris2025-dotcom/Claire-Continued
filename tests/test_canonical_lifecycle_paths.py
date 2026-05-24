from claire.lifecycle.canonical_paths import route_path
from claire.lifecycle.lifecycle_runner import CoreLifecycleRunner


def test_portfolio_route_uses_uploaded_default_path_without_forcing_breakthrough_or_acquisition():
    payload = CoreLifecycleRunner().run(
        {
            "knowledge_ingestion": {"status": "success"},
            "signal_extraction": {"status": "success"},
            "connector_sources": {"market": {"status": "available"}},
            "keywords": ["automation"],
            "engine_details": {"status": "success"},
            "trend_trajectory": {"status": "success"},
            "trend_discovery": {"status": "success"},
            "market_gap": {"status": "success"},
            "opportunity_discovery": {"status": "success"},
            "thesis_formation": {"route_recommendation": "portfolio_intelligence"},
            "strategic_positioning": {"status": "success"},
            "market_formation": {"status": "success"},
            "portfolio_binder": {"status": "success"},
            "portfolio_optimization": {"portfolio_path": "watchlist_and_weighting"},
            "export_package": {"status": "success"},
        },
        run_id="test-portfolio",
    )

    assert payload["route"] == "portfolio_creation_optimization"
    statuses = {stage["id"]: stage["status"] for stage in payload["stages"]}
    assert statuses["portfolio_creation_optimization"] == "complete"
    assert statuses["gap_detection"] == "skipped_by_route"
    assert statuses["auto_invention_solution_generation"] == "skipped_by_route"
    assert statuses["acquirer_identification"] == "skipped_by_route"
    assert payload["completion_gate"]["status"] == "complete"


def test_acquisition_route_requires_fit_rationale_without_design_portal():
    path = route_path("acquisition_package")
    assert "acquirer_identification" in path
    assert "acquisition_fit_rationale" in path
    assert "auto_invention_solution_generation" not in path


def test_breakthrough_design_route_keeps_full_package_path():
    path = route_path("breakthrough_design")
    assert path[0] == "signal_ingestion"
    assert "auto_invention_solution_generation" in path
    assert "design_portal_output_blueprints_specs" in path
    assert "acquirer_identification" in path
    assert path[-1] == "final_package_construction"


def test_signal_activated_design_portal_selects_breakthrough_design_route():
    route = CoreLifecycleRunner().detect_route(
        {
            "thesis_formation": {"route_recommendation": "portfolio_intelligence"},
            "design_portal": {
                "status": "design_ready",
                "route_to_design": True,
                "inputs": {"signal_activated_breakthrough": True},
            },
            "design_output": {"status": "success"},
        }
    )

    assert route == "breakthrough_design"
