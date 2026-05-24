from __future__ import annotations

from typing import Dict, List

from .models import DecisionScenario, InterventionRecommendation, OutcomeSimulation


class InterventionStrategySelector:
    def select(self, scenario: DecisionScenario, simulations: List[OutcomeSimulation]) -> InterventionRecommendation:
        if not simulations:
            return InterventionRecommendation(
                scenario_id=scenario.scenario_id,
                selected_action_id="none",
                recommendation="No recommendation available.",
                rationale=["No simulations were available for comparison."],
                confidence=0.0,
            )

        ranked = sorted(simulations, key=lambda sim: sim.total_score(), reverse=True)
        selected = ranked[0]
        rejected = [
            {
                "action_id": sim.action_id,
                "expected_outcome": sim.expected_outcome,
                "total_score": sim.total_score(),
                "reason": "Lower governed score than selected action.",
            }
            for sim in ranked[1:]
        ]

        action_lookup: Dict[str, str] = {action.action_id: action.name for action in scenario.action_pathways}
        selected_name = action_lookup.get(selected.action_id, selected.action_id)

        if selected.expected_outcome == "high_risk_not_recommended":
            recommendation = "Do not intervene yet; continue evidence collection."
        elif selected.expected_outcome == "uncertain_requires_more_evidence":
            recommendation = "Continue bounded research before intervention."
        else:
            recommendation = f"Recommend governed pathway: {selected_name}."

        confidence = max(0.0, min(1.0, scenario.confidence + selected.confidence_delta))

        return InterventionRecommendation(
            scenario_id=scenario.scenario_id,
            selected_action_id=selected.action_id,
            recommendation=recommendation,
            rationale=[
                f"Selected action has highest governed score: {selected.total_score()}.",
                f"Expected outcome: {selected.expected_outcome}.",
                f"Evidence sensitivity: {selected.evidence_sensitivity}.",
                "Recommendation remains bounded and review-only.",
            ],
            rejected_actions=rejected,
            expected_outcome=selected.expected_outcome,
            governance_status="governed_recommendation_ready",
            execution_boundary="no_external_action_without_user_approval",
            confidence=round(confidence, 4),
        )
