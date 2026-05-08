from __future__ import annotations

from typing import Dict, List

from .models import DecisionScenario, InterventionRecommendation, OutcomeSimulation


class StrategicDecisionRegressionLock:
    def validate(
        self,
        scenario: DecisionScenario,
        simulations: List[OutcomeSimulation],
        recommendation: InterventionRecommendation,
    ) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if not scenario.scenario_id:
            errors.append("Scenario is missing scenario_id.")

        if not scenario.decision_question:
            errors.append("Scenario is missing decision_question.")

        action_ids = {action.action_id for action in scenario.action_pathways}
        simulation_ids = {sim.action_id for sim in simulations}

        if not scenario.action_pathways:
            errors.append("Scenario has no action pathways.")

        if not simulations:
            errors.append("No simulations were generated.")

        missing_simulations = action_ids - simulation_ids
        if missing_simulations:
            errors.append(f"Missing simulations for actions: {sorted(missing_simulations)}")

        if recommendation.selected_action_id not in action_ids and recommendation.selected_action_id != "none":
            errors.append("Recommendation selected an action not present in scenario pathways.")

        if recommendation.execution_boundary != "no_external_action_without_user_approval":
            errors.append("Execution boundary was not preserved.")

        if scenario.confidence < 0.25:
            warnings.append("Scenario confidence is very low; recommendation should remain research-first.")

        if len(scenario.evidence_conflicting) > len(scenario.evidence_supporting):
            warnings.append("Conflicting evidence exceeds supporting evidence.")

        regression_status = "passed" if not errors else "failed"

        return {
            "version": "v17.00",
            "regression_status": regression_status,
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "decision_continuity": not errors,
                "simulation_governance": recommendation.execution_boundary == "no_external_action_without_user_approval",
                "intervention_selection_integrity": recommendation.selected_action_id in action_ids or recommendation.selected_action_id == "none",
                "bounded_execution": True,
            },
        }
