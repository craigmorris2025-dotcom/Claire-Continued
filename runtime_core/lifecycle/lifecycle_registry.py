"""Canonical 30-stage Claire core lifecycle registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CoreLifecycleStage:
    id: str
    number: int
    name: str
    phase: str
    requirement: str
    output_key: str


class CoreLifecycleRegistry:
    """Read-only source of truth for the 30-stage core completion lifecycle."""

    lifecycle_name = "Claire Core Completion Lifecycle"
    version = "v5.89.5_core_lifecycle_spine"

    def stages(self) -> List[Dict[str, Any]]:
        return [asdict(stage) for stage in self._stages()]

    def get(self, stage_id_or_number: str | int) -> Optional[Dict[str, Any]]:
        for stage in self._stages():
            if stage.id == stage_id_or_number or stage.number == stage_id_or_number:
                return asdict(stage)
        return None

    def summary(self) -> Dict[str, Any]:
        stages = self._stages()
        phases: Dict[str, int] = {}
        requirements: Dict[str, int] = {}
        for stage in stages:
            phases[stage.phase] = phases.get(stage.phase, 0) + 1
            requirements[stage.requirement] = requirements.get(stage.requirement, 0) + 1
        return {
            "status": "success",
            "registry_version": self.version,
            "lifecycle_name": self.lifecycle_name,
            "stage_count": len(stages),
            "phases": phases,
            "requirements": requirements,
            "first_stage": stages[0].name,
            "final_stage": stages[-1].name,
        }

    def as_payload(self) -> Dict[str, Any]:
        return {**self.summary(), "stages": self.stages()}

    def _stages(self) -> List[CoreLifecycleStage]:
        return [
            CoreLifecycleStage("signal_ingestion", 1, "Signal Ingestion", "signal_governance", "required", "knowledge_ingestion"),
            CoreLifecycleStage("signal_normalization", 2, "Signal Normalization", "signal_governance", "required", "signal_extraction"),
            CoreLifecycleStage("source_validation_weighting", 3, "Source Validation & Weighting", "signal_governance", "required", "knowledge_ingestion"),
            CoreLifecycleStage("context_expansion", 4, "Context Expansion", "signal_governance", "required", "connector_sources"),
            CoreLifecycleStage("signal_consolidation", 5, "Signal Consolidation", "signal_governance", "required", "signal_extraction"),
            CoreLifecycleStage("entity_extraction", 6, "Entity Extraction", "discovery", "required", "keywords"),
            CoreLifecycleStage("relationship_mapping", 7, "Relationship Mapping", "discovery", "required", "engine_details"),
            CoreLifecycleStage("trend_discovery", 8, "Trend Discovery", "discovery", "required", "trend_discovery"),
            CoreLifecycleStage("cluster_formation", 9, "Cluster Formation", "discovery", "required", "market_gap"),
            CoreLifecycleStage("insight_thesis_structuring", 10, "Insight / Thesis Structuring", "discovery", "required", "thesis_formation"),
            CoreLifecycleStage("gap_detection", 11, "Gap Detection", "discovery", "required", "market_gap"),
            CoreLifecycleStage("gap_qualification", 12, "Gap Qualification", "discovery", "required", "market_gap"),
            CoreLifecycleStage("discovery_generation", 13, "Discovery Generation", "discovery", "required", "opportunity_discovery"),
            CoreLifecycleStage("breakthrough_identification_classification", 14, "Breakthrough Identification & Classification", "breakthrough", "required", "breakthrough_synthesis"),
            CoreLifecycleStage("advancement_path_selection", 15, "Advancement Path Selection", "breakthrough", "required", "design_portal"),
            CoreLifecycleStage("auto_invention_solution_generation", 16, "Auto Invention / Solution Generation", "design", "route_dependent", "design_output"),
            CoreLifecycleStage("solution_structuring", 17, "Solution Structuring", "design", "route_dependent", "system_design"),
            CoreLifecycleStage("buildability_assessment", 18, "Buildability Assessment", "validation", "route_dependent", "technical_feasibility"),
            CoreLifecycleStage("viability_assessment", 19, "Viability Assessment", "validation", "required", "business_model"),
            CoreLifecycleStage("manufacturability_deployability_assessment", 20, "Manufacturability / Deployability Assessment", "validation", "route_dependent", "technical_feasibility"),
            CoreLifecycleStage("feasibility_validation", 21, "Feasibility Validation", "validation", "route_dependent", "technical_feasibility"),
            CoreLifecycleStage("design_portal_output_blueprints_specs", 22, "Design Portal Output / Blueprints / Specs", "design", "route_dependent", "design_output"),
            CoreLifecycleStage("market_positioning", 23, "Market Positioning", "strategy", "required", "strategic_positioning"),
            CoreLifecycleStage("moat_differentiation", 24, "Moat & Differentiation", "strategy", "required", "moat"),
            CoreLifecycleStage("business_model_value_capture", 25, "Business Model & Value Capture", "strategy", "required", "business_model"),
            CoreLifecycleStage("competitor_analysis", 26, "Competitor Analysis", "strategy", "required", "market_formation"),
            CoreLifecycleStage("portfolio_creation_optimization", 27, "Portfolio Creation / Optimization", "portfolio", "required", "portfolio_optimization"),
            CoreLifecycleStage("acquirer_identification", 28, "Acquirer Identification", "acquisition", "required", "acquirer_matches"),
            CoreLifecycleStage("acquisition_fit_rationale", 29, "Acquisition Fit & Rationale", "acquisition", "required", "deal_exit_modeling"),
            CoreLifecycleStage("final_package_construction", 30, "Final Package Construction", "package", "required", "export_package"),
        ]
