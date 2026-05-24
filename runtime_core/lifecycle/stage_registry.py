"""Canonical Claire lifecycle stage registry.

This module is intentionally descriptive. The executable stage evaluation
still lives in ``claire.engines.lifecycle_stage_engine``; this registry gives
the dashboard, validation tools, and export layers a stable source of truth
for stage ordering and ownership.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LifecycleStage:
    stage: int
    slug: str
    name: str
    category: str
    output_key: str
    objective: str
    primary_evidence_keys: List[str]
    downstream_use: str


class ClaireStageRegistry:
    """Read-only registry for Claire's 21-stage intelligence lifecycle."""

    lifecycle_name = "Claire Intelligence Lifecycle"
    version = "v5.52_stage_threshold_provenance"

    def stages(self) -> List[Dict[str, Any]]:
        return [asdict(stage) for stage in self._stages()]

    def summary(self) -> Dict[str, Any]:
        stages = self._stages()
        categories: Dict[str, int] = {}
        for stage in stages:
            categories[stage.category] = categories.get(stage.category, 0) + 1
        return {
            "status": "success",
            "registry_version": self.version,
            "lifecycle_name": self.lifecycle_name,
            "stage_count": len(stages),
            "categories": categories,
            "first_stage": stages[0].name,
            "final_stage": stages[-1].name,
        }

    def as_payload(self) -> Dict[str, Any]:
        return {
            **self.summary(),
            "stages": self.stages(),
            "output_key_map": self.output_key_map(),
        }

    def output_key_map(self) -> Dict[str, List[Dict[str, Any]]]:
        mapping: Dict[str, List[Dict[str, Any]]] = {}
        for stage in self._stages():
            mapping.setdefault(stage.output_key, []).append({
                "stage": stage.stage,
                "slug": stage.slug,
                "name": stage.name,
            })
        return mapping

    def get(self, slug_or_stage: Any) -> Optional[Dict[str, Any]]:
        for stage in self._stages():
            if slug_or_stage == stage.stage or slug_or_stage == stage.slug:
                return asdict(stage)
        return None

    def validate_result_shape(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result = result or {}
        missing = []
        present = []
        for stage in self._stages():
            if result.get(stage.output_key) is not None:
                present.append(stage.slug)
            else:
                missing.append({
                    "stage": stage.stage,
                    "slug": stage.slug,
                    "output_key": stage.output_key,
                })
        return {
            "status": "success" if not missing else "partial",
            "checked_stage_count": len(self._stages()),
            "present_stage_count": len(present),
            "missing_stage_count": len(missing),
            "present": present,
            "missing": missing,
        }

    def _stages(self) -> List[LifecycleStage]:
        return [
            LifecycleStage(1, "ingestion", "Knowledge Ingestion", "knowledge", "knowledge_ingestion", "Ingest raw input, connector context, source inventory, and coverage signals.", ["raw_input", "connector_sources", "knowledge_quality_score"], "Feeds safe downstream scoring and provenance."),
            LifecycleStage(2, "signal_extraction", "Signal Extraction", "knowledge", "signal_extraction", "Extract buyer, product, evidence, technical, and control signals.", ["signal_contract", "dominant_sector", "routing_evidence"], "Routes the opportunity into the right domain lens."),
            LifecycleStage(3, "trend_trajectory", "Trend + Trajectory Modeling", "discovery", "trend_trajectory", "Evaluate direction, momentum, strategic window, and timing pressure.", ["trend_direction", "strategic_window", "trajectory_score"], "Informs discovery and why-now logic."),
            LifecycleStage(4, "market_sector_industry_mapping", "Market / Sector / Industry Mapping", "discovery", "market_gap", "Map the opportunity to market, sector, industry, and buyer terrain.", ["sector", "buyer_segments", "market_context"], "Keeps mixed signals from drifting into the wrong market."),
            LifecycleStage(5, "gap_detection", "Gap Detection", "discovery", "market_gap", "Identify unmet need, market gap, pressure, and weak incumbent coverage.", ["market_gap", "strategic_pressure", "gap_confidence"], "Provides the problem spine for opportunity discovery."),
            LifecycleStage(6, "needed_solution", "Needed Solution", "discovery", "market_gap", "Translate gaps into needed solution classes and buyer-facing requirements.", ["needed_solution", "solution_class", "buyer_segments"], "Creates the solution target before productization."),
            LifecycleStage(7, "opportunity_discovery_context", "Opportunity Discovery Context", "discovery", "opportunity_discovery", "Score and classify opportunity direction, priority, and portfolio relevance.", ["opportunity_score", "opportunity_type", "priority_assessment"], "Produces candidate opportunity context."),
            LifecycleStage(8, "breakthrough_synthesis", "Breakthrough Synthesis", "breakthrough", "breakthrough_synthesis", "Synthesize non-obviousness, novelty, and breakthrough logic.", ["breakthrough_synthesis_score", "non_obviousness", "breakthrough_classification"], "Determines whether the idea should advance as a breakthrough candidate."),
            LifecycleStage(9, "technical_feasibility", "Technical Feasibility", "validation", "technical_feasibility", "Assess buildability, readiness, implementation risk, and controls.", ["technical_feasibility_score", "feasibility_classification", "deployment_controls"], "Protects the build path from impossible or unsafe execution."),
            LifecycleStage(10, "market_formation", "Market Formation", "validation", "market_formation", "Assess category creation, buyer pull, market stage, and formation pressure.", ["formation_type", "market_stage", "category_creation_score", "buyer_pull"], "Separates live market formation from speculative interest."),
            LifecycleStage(11, "moat_defensibility", "Moat / Defensibility", "validation", "moat", "Assess defensibility, copy risk, distribution advantage, and data/process moat.", ["moat_type", "copy_risk", "defensibility_score"], "Supports strategic positioning and acquisition value."),
            LifecycleStage(12, "risk_regulation_compliance", "Risk / Regulation / Compliance", "validation", "risk_regulation", "Assess risk, regulatory exposure, blockers, and control posture.", ["risk_profile", "regulation_profile", "blocker_assessment"], "Applies governance boundaries and readiness modifiers."),
            LifecycleStage(13, "productization_path", "Productization Path", "design", "productization_path", "Define packaging, pilot path, go-to-market readiness, and launch controls.", ["productization_score", "pilot_strategy", "launch_controls"], "Turns discovery into a launchable product path."),
            LifecycleStage(14, "design_portal", "Design Portal Routing", "design", "design_portal", "Decide whether the opportunity is ready for design generation.", ["route_to_design", "routing_reason", "status"], "Controls transition from intelligence to build blueprint."),
            LifecycleStage(15, "system_design", "System / Technology Design", "design", "design_output", "Generate system design, architecture, modules, and implementation structure.", ["system_design", "architecture_blueprint", "implementation_phases"], "Creates the technical object to build."),
            LifecycleStage(16, "technical_specs_blueprint", "Technical Specs / Blueprint", "design", "design_output", "Generate technical specs, blueprint, data contracts, and build phases.", ["technical_specs", "architecture_blueprint", "build_blueprint"], "Supports implementation and handoff."),
            LifecycleStage(17, "business_model_value_capture", "Business Model / Value Capture", "strategy", "business_model", "Assess revenue model, buyer ROI, value capture, and commercialization logic.", ["revenue_model", "value_capture", "buyer_roi"], "Connects technical opportunity to monetization."),
            LifecycleStage(18, "strategic_positioning", "Strategic Positioning", "strategy", "strategic_positioning", "Define category, buyer, acquirer, and narrative positioning.", ["strategic_positioning_score", "category_positioning", "acquirer_positioning"], "Frames the opportunity for market and exit outcomes."),
            LifecycleStage(19, "portfolio_binder", "Portfolio / Binder", "portfolio", "portfolio_binder", "Assemble evidence, scores, sections, and artifact manifest.", ["sections", "artifact_manifest", "portfolio_score"], "Creates acquisition-grade evidence packaging."),
            LifecycleStage(20, "acquirer_discovery", "Acquirer Discovery", "outcome", "acquirer_matches", "Identify strategic acquirers and match rationale.", ["acquirer_matches", "strategic_fit", "buyer_overlap"], "Connects opportunity to likely buyer universe."),
            LifecycleStage(21, "deal_exit_modeling", "Deal / Exit Modeling", "outcome", "deal_exit_modeling", "Model exit readiness, valuation signal, strategic fit, and deal posture.", ["exit_readiness", "valuation_logic", "strategic_fit"], "Completes the pathway from discovery to value capture."),
        ]
