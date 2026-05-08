from __future__ import annotations

from typing import List

from .models import DecisionScenario, OutcomeSimulation, StrategicActionPathway


class BoundedOutcomeSimulator:
    def simulate(self, scenario: DecisionScenario) -> List[OutcomeSimulation]:
        return [self._simulate_action(scenario, action) for action in scenario.action_pathways]

    def _simulate_action(self, scenario: DecisionScenario, action: StrategicActionPathway) -> OutcomeSimulation:
        support_count = len(scenario.evidence_supporting)
        conflict_count = len(scenario.evidence_conflicting)

        reversibility_bonus = {"high": 0.18, "medium": 0.08, "low": -0.08}.get(action.reversibility, 0.0)
        effort_penalty = {"low": 0.02, "medium": 0.08, "high": 0.16}.get(action.estimated_effort, 0.08)

        evidence_strength = min(1.0, (support_count + 1) / max(1, support_count + conflict_count + 2))
        conflict_pressure = min(1.0, conflict_count / max(1, support_count + conflict_count + 1))

        upside = min(1.0, scenario.confidence * 0.55 + evidence_strength * 0.35 + len(action.expected_benefits) * 0.03)
        downside = min(1.0, conflict_pressure * 0.45 + len(action.risks) * 0.06 + effort_penalty)
        uncertainty = min(1.0, (1.0 - scenario.confidence) * 0.4 + conflict_pressure * 0.3 + (0.1 if not action.required_evidence else 0.0))
        confidence_delta = round(reversibility_bonus - effort_penalty - conflict_pressure * 0.12, 4)
        expected = self._expected_outcome_label(upside, downside, uncertainty)

        return OutcomeSimulation(
            scenario_id=scenario.scenario_id,
            action_id=action.action_id,
            expected_outcome=expected,
            confidence_delta=confidence_delta,
            upside_score=round(upside, 4),
            downside_score=round(downside, 4),
            uncertainty_score=round(uncertainty, 4),
            evidence_sensitivity="high" if conflict_count > 0 or scenario.confidence < 0.65 else "medium",
            assumptions_tested=list(action.assumptions),
            failure_modes=list(action.risks),
            governance_notes=[
                "Simulation is bounded and heuristic.",
                "Expected outcomes are not guarantees.",
                "User approval is required before any real-world action.",
            ],
        )

    def _expected_outcome_label(self, upside: float, downside: float, uncertainty: float) -> str:
        if upside >= 0.7 and downside <= 0.35 and uncertainty <= 0.45:
            return "favorable_if_governed"
        if uncertainty >= 0.65:
            return "uncertain_requires_more_evidence"
        if downside >= 0.6:
            return "high_risk_not_recommended"
        return "mixed_requires_bounded_test"
