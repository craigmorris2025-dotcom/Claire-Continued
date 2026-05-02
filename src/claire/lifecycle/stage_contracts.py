"""Stage output contracts for the 30-stage Claire core lifecycle."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


PORTFOLIO_ONLY_ROUTE = "portfolio_only"
BREAKTHROUGH_DESIGN_ROUTE = "breakthrough_design"


@dataclass(frozen=True)
class StageContract:
    stage_id: str
    required_outputs: List[str]
    route_dependent: bool = False
    required_routes: List[str] | None = None
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def stage_contracts() -> Dict[str, StageContract]:
    return {
        "signal_ingestion": StageContract("signal_ingestion", ["knowledge_ingestion"]),
        "signal_normalization": StageContract("signal_normalization", ["signal_extraction"]),
        "source_validation_weighting": StageContract("source_validation_weighting", ["knowledge_ingestion"]),
        "context_expansion": StageContract("context_expansion", ["connector_sources"]),
        "signal_consolidation": StageContract("signal_consolidation", ["signal_extraction"]),
        "entity_extraction": StageContract("entity_extraction", ["keywords"]),
        "relationship_mapping": StageContract("relationship_mapping", ["engine_details"]),
        "trend_discovery": StageContract("trend_discovery", ["trend_trajectory", "trend_discovery"]),
        "cluster_formation": StageContract("cluster_formation", ["market_gap"]),
        "insight_thesis_structuring": StageContract("insight_thesis_structuring", ["opportunity_discovery", "thesis_formation"]),
        "gap_detection": StageContract("gap_detection", ["market_gap"]),
        "gap_qualification": StageContract("gap_qualification", ["market_gap"]),
        "discovery_generation": StageContract("discovery_generation", ["opportunity_discovery"]),
        "breakthrough_identification_classification": StageContract("breakthrough_identification_classification", ["breakthrough_synthesis"]),
        "advancement_path_selection": StageContract("advancement_path_selection", ["design_portal"]),
        "auto_invention_solution_generation": StageContract("auto_invention_solution_generation", ["design_output"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "solution_structuring": StageContract("solution_structuring", ["system_design"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "buildability_assessment": StageContract("buildability_assessment", ["technical_feasibility"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "viability_assessment": StageContract("viability_assessment", ["business_model"]),
        "manufacturability_deployability_assessment": StageContract("manufacturability_deployability_assessment", ["technical_feasibility"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "feasibility_validation": StageContract("feasibility_validation", ["technical_feasibility"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "design_portal_output_blueprints_specs": StageContract("design_portal_output_blueprints_specs", ["design_output"], True, [BREAKTHROUGH_DESIGN_ROUTE]),
        "market_positioning": StageContract("market_positioning", ["strategic_positioning"]),
        "moat_differentiation": StageContract("moat_differentiation", ["moat"]),
        "business_model_value_capture": StageContract("business_model_value_capture", ["business_model"]),
        "competitor_analysis": StageContract("competitor_analysis", ["market_formation"], optional=True),
        "portfolio_creation_optimization": StageContract("portfolio_creation_optimization", ["portfolio_binder"]),
        "acquirer_identification": StageContract("acquirer_identification", ["acquirer_matches"]),
        "acquisition_fit_rationale": StageContract("acquisition_fit_rationale", ["deal_exit_modeling"]),
        "final_package_construction": StageContract("final_package_construction", ["export_package"]),
    }


def route_requires_contract(contract: StageContract, route: str) -> bool:
    if contract.optional:
        return False
    if not contract.route_dependent:
        return True
    return route in set(contract.required_routes or [])
