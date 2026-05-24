"""
Core — Planner: Converts intent into an executable plan.
Determines strategy, step sequence, and resource allocation.
"""
import logging
from typing import Any, Dict
from runtime_core.domain.contract import ClaireIntent, PlanObject

logger = logging.getLogger("claire.core.planner")

STRATEGIES = {
    ("evaluate", "deterministic"): {
        "strategy": "deterministic_eval",
        "steps": ["nlp_extract", "domain_scoring", "calibrate_scores",
                  "acquirer_match", "compliance_check", "generate_scorecard"],
        "estimated_phases": 4,
    },
    ("evaluate", "connected"): {
        "strategy": "connected_eval",
        "steps": ["nlp_extract", "fetch_market_data", "fetch_patent_data",
                  "fetch_financial_data", "domain_scoring", "calibrate_scores",
                  "acquirer_match", "compliance_check", "generate_scorecard"],
        "estimated_phases": 4,
    },
    ("evaluate", "hybrid"): {
        "strategy": "hybrid_eval",
        "steps": ["nlp_extract", "fetch_market_data", "fetch_patent_data",
                  "fetch_financial_data", "domain_scoring", "pattern_analysis",
                  "fettio_processing", "calibrate_scores", "acquirer_match",
                  "compliance_check", "desking_distribute", "generate_scorecard"],
        "estimated_phases": 4,
    },
    ("analyze", "deterministic"): {
        "strategy": "deterministic_analysis",
        "steps": ["nlp_extract", "domain_scoring", "calibrate_scores", "generate_report"],
        "estimated_phases": 3,
    },
    ("plan", "deterministic"): {
        "strategy": "planning",
        "steps": ["nlp_extract", "strategy_formulation", "resource_estimation"],
        "estimated_phases": 2,
    },
}


class Planner:
    """Converts validated intents into executable plans."""

    def create_plan(self, intent: ClaireIntent) -> PlanObject:
        key = (intent.request_type, intent.mode)
        template = STRATEGIES.get(key)
        if not template:
            template = STRATEGIES.get((intent.request_type, "deterministic"))
        if not template:
            template = STRATEGIES[("evaluate", "deterministic")]

        plan = PlanObject(
            steps=list(template["steps"]),
            strategy=template["strategy"],
            estimated_phases=template["estimated_phases"],
        )
        if intent.metadata.priority == "high":
            plan.steps = [s for s in plan.steps if s != "desking_distribute"]

        logger.info(f"Plan: {plan.strategy}, {len(plan.steps)} steps for {intent.id}")
        return plan

    def get_status(self) -> Dict[str, Any]:
        return {"component": "Planner", "status": "active", "strategies": len(STRATEGIES)}
