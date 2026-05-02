from __future__ import annotations

from claire.domain.contract import ContractValidator
from claire.lifecycle import CoreLifecycleRegistry, CoreLifecycleRunner
from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from tests.regression.fixtures.lifecycle_inputs import ALL_FIXTURES


def test_pipeline_exposes_30_stage_core_lifecycle():
    result = PipelineOrchestrator().execute(
        ContractValidator().validate_intent(ALL_FIXTURES["climate_insurance"])
    ).to_dict()

    core_lifecycle = result["core_lifecycle"]
    assert core_lifecycle["stage_count"] == 30
    assert len(result["core_lifecycle_stages"]) == 30
    assert result["core_lifecycle_summary"]["stage_count"] == 30
    assert result["core_completion_gate"]["status"] in {"complete", "insufficient_data"}

    assert any(
        stage["id"] == "auto_invention_solution_generation"
        for stage in result["core_lifecycle_stages"]
    )


def test_portfolio_route_skips_invention_and_design_stages():
    payload = CoreLifecycleRunner().run({
        "knowledge_ingestion": {"status": "success"},
        "signal_extraction": {"status": "success"},
        "connector_sources": {"offline": True},
        "keywords": ["portfolio"],
        "engine_details": {"signals": {}},
        "trend_trajectory": {"status": "success"},
        "market_gap": {"status": "success"},
        "opportunity_discovery": {"status": "success"},
        "breakthrough_synthesis": {"status": "success"},
        "design_portal": {"status": "not_routed", "route_to_design": False},
        "business_model": {"status": "success"},
        "strategic_positioning": {"status": "success"},
        "moat": {"status": "success"},
        "portfolio_binder": {"status": "success"},
        "acquirer_matches": [{"name": "Strategic buyer"}],
        "deal_exit_modeling": {"status": "success"},
        "export_package": {"status": "success"},
    }, route="portfolio_only")

    skipped = [
        stage["id"]
        for stage in payload["stages"]
        if stage["status"] == "skipped_by_route"
    ]
    assert "auto_invention_solution_generation" in skipped
    assert "design_portal_output_blueprints_specs" in skipped
    assert payload["completion_gate"]["status"] == "complete"


def test_core_lifecycle_registry_is_canonical_30_stage_order():
    stages = CoreLifecycleRegistry().stages()
    assert len(stages) == 30
    assert stages[0]["name"] == "Signal Ingestion"
    assert stages[13]["name"] == "Breakthrough Identification & Classification"
    assert stages[-1]["name"] == "Final Package Construction"
