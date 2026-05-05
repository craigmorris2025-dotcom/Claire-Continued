
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
    assert result["core_completion_gate"]["status"] in {
        "complete",
        "insufficient_data",
    }

    assert any(
        stage["id"] == "auto_invention_solution_generation"
        for stage in result["core_lifecycle_stages"]
    )


def test_portfolio_route_skips_invention_and_design_stages():
    """
    Regression proof:
    - portfolio_only route must not trigger invention/design stages.
    - invention/design stages must remain visible as skipped_by_route.
    - when the portfolio route has full required outputs, completion gate
      must be complete, not insufficient_data.
    """

    payload = CoreLifecycleRunner().run(
        {
            # Signal governance / early lifecycle
            "knowledge_ingestion": {"status": "success"},
            "signal_ingestion": {"status": "success"},
            "signal_extraction": {"status": "success"},
            "signal_normalization": {"status": "success"},
            "source_validation_weighting": {"status": "success"},
            "context_expansion": {"status": "success"},
            "signal_consolidation": {"status": "success"},
            "connector_sources": {"offline": True},
            "keywords": ["portfolio"],
            "engine_details": {"signals": {"status": "success"}},

            # Trend / thesis / gap / discovery
            "trend_discovery": {"status": "success"},
            "trend_trajectory": {"status": "success"},
            "cluster_formation": {"status": "success"},
            "insight_thesis": {"status": "success"},
            "thesis_formation": {"status": "success"},
            "market_gap": {"status": "success"},
            "gap_detection": {"status": "success"},
            "gap_qualification": {"status": "success"},
            "opportunity_discovery": {"status": "success"},
            "discovery_generation": {"status": "success"},

            # Breakthrough classification exists, but route remains portfolio
            "breakthrough_synthesis": {"status": "success"},
            "breakthrough_classification": {
                "status": "success",
                "route": "portfolio_only",
                "classification": "portfolio",
            },
            "advancement_path": {
                "status": "skipped_by_route",
                "route": "portfolio_only",
            },

            # Design / invention intentionally not routed
            "auto_invention": {
                "status": "not_routed",
                "route_to_design": False,
            },
            "design_portal": {
                "status": "not_routed",
                "route_to_design": False,
            },

            # Strategy / market / portfolio / acquisition package
            "market_positioning": {"status": "success"},
            "strategic_positioning": {"status": "success"},
            "moat": {"status": "success"},
            "moat_differentiation": {"status": "success"},
            "business_model": {"status": "success"},
            "business_model_value_capture": {"status": "success"},
            "competitor_analysis": {"status": "success"},
            "portfolio_binder": {"status": "success"},
            "portfolio_creation_optimization": {"status": "success"},
            "portfolio_optimization": {"status": "success"},
            "acquirer_matches": [{"name": "Strategic buyer"}],
            "acquirer_identification": {"status": "success"},
            "acquisition_fit_rationale": {"status": "success"},
            "deal_exit_modeling": {"status": "success"},

            # Final package / evidence / confidence
            "final_package_construction": {"status": "success"},
            "export_package": {"status": "success"},
            "evidence": {"status": "success"},
            "confidence": {"status": "success"},
            "risks": {"status": "success"},
            "next_steps": {"status": "success"},
        },
        route="portfolio_only",
    )

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