from __future__ import annotations

from typing import Dict, List


PORTFOLIO_ROUTE = "portfolio_creation_optimization"
ACQUISITION_ROUTE = "acquisition_package"
BREAKTHROUGH_DESIGN_ROUTE = "breakthrough_design"
SOLUTION_DESIGN_ROUTE = "solution_design"
BREAKTHROUGH_ESCALATION_ROUTE = "breakthrough_escalation"
EXISTING_SYSTEM_REPLACEMENT_ROUTE = "existing_system_replacement"

ROUTE_ALIASES = {
    "portfolio_only": PORTFOLIO_ROUTE,
    "portfolio_intelligence": PORTFOLIO_ROUTE,
    "portfolio_candidate": PORTFOLIO_ROUTE,
    "breakthrough_escalation_candidate": BREAKTHROUGH_ESCALATION_ROUTE,
    "existing_system_ingestion": EXISTING_SYSTEM_REPLACEMENT_ROUTE,
    "system_replacement": EXISTING_SYSTEM_REPLACEMENT_ROUTE,
    "superior_system_design": EXISTING_SYSTEM_REPLACEMENT_ROUTE,
}

SHARED_SPINE = [
    "signal_ingestion",
    "signal_normalization",
    "source_validation_weighting",
    "context_expansion",
    "signal_consolidation",
    "entity_extraction",
    "relationship_mapping",
    "trend_discovery",
    "cluster_formation",
    "insight_thesis_structuring",
]

CANONICAL_ROUTE_PATHS: Dict[str, List[str]] = {
    PORTFOLIO_ROUTE: [
        *SHARED_SPINE,
        "market_positioning",
        "competitor_analysis",
        "portfolio_creation_optimization",
        "final_package_construction",
    ],
    ACQUISITION_ROUTE: [
        *SHARED_SPINE,
        "gap_detection",
        "gap_qualification",
        "market_positioning",
        "moat_differentiation",
        "business_model_value_capture",
        "competitor_analysis",
        "acquirer_identification",
        "acquisition_fit_rationale",
        "final_package_construction",
    ],
    BREAKTHROUGH_ESCALATION_ROUTE: [
        *SHARED_SPINE,
        "gap_detection",
        "gap_qualification",
        "discovery_generation",
        "breakthrough_identification_classification",
        "advancement_path_selection",
        "market_positioning",
        "moat_differentiation",
        "business_model_value_capture",
        "competitor_analysis",
        "portfolio_creation_optimization",
        "final_package_construction",
    ],
    BREAKTHROUGH_DESIGN_ROUTE: [
        *SHARED_SPINE,
        "gap_detection",
        "gap_qualification",
        "discovery_generation",
        "breakthrough_identification_classification",
        "advancement_path_selection",
        "auto_invention_solution_generation",
        "solution_structuring",
        "buildability_assessment",
        "viability_assessment",
        "manufacturability_deployability_assessment",
        "feasibility_validation",
        "design_portal_output_blueprints_specs",
        "market_positioning",
        "moat_differentiation",
        "business_model_value_capture",
        "competitor_analysis",
        "portfolio_creation_optimization",
        "acquirer_identification",
        "acquisition_fit_rationale",
        "final_package_construction",
    ],
    SOLUTION_DESIGN_ROUTE: [
        *SHARED_SPINE,
        "gap_detection",
        "gap_qualification",
        "discovery_generation",
        "breakthrough_identification_classification",
        "advancement_path_selection",
        "auto_invention_solution_generation",
        "solution_structuring",
        "buildability_assessment",
        "viability_assessment",
        "manufacturability_deployability_assessment",
        "feasibility_validation",
        "design_portal_output_blueprints_specs",
        "market_positioning",
        "moat_differentiation",
        "business_model_value_capture",
        "competitor_analysis",
        "portfolio_creation_optimization",
        "final_package_construction",
    ],
    EXISTING_SYSTEM_REPLACEMENT_ROUTE: [
        "existing_system_ingestion",
        "signal_ingestion",
        "signal_normalization",
        "source_validation_weighting",
        "context_expansion",
        "signal_consolidation",
        "entity_extraction",
        "relationship_mapping",
        "existing_system_decomposition",
        "trend_discovery",
        "cluster_formation",
        "insight_thesis_structuring",
        "gap_detection",
        "gap_qualification",
        "discovery_generation",
        "breakthrough_identification_classification",
        "advancement_path_selection",
        "auto_invention_solution_generation",
        "solution_structuring",
        "buildability_assessment",
        "viability_assessment",
        "manufacturability_deployability_assessment",
        "feasibility_validation",
        "design_portal_output_blueprints_specs",
        "superior_system_design",
        "market_positioning",
        "moat_differentiation",
        "business_model_value_capture",
        "competitor_analysis",
        "portfolio_creation_optimization",
        "acquirer_identification",
        "acquisition_fit_rationale",
        "final_package_construction",
    ],
}


def normalize_route(route: str | None) -> str:
    value = str(route or "").strip()
    return ROUTE_ALIASES.get(value, value or PORTFOLIO_ROUTE)


def route_path(route: str | None) -> List[str]:
    normalized = normalize_route(route)
    return CANONICAL_ROUTE_PATHS.get(normalized, CANONICAL_ROUTE_PATHS[PORTFOLIO_ROUTE])
