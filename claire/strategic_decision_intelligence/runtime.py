from __future__ import annotations

from typing import Any, Dict, Optional, List

from .bounded_outcome_simulator import BoundedOutcomeSimulator
from .decision_scenario_engine import DecisionScenarioEngine
from .expected_actual_outcome_tracker import ExpectedActualOutcomeTracker
from .intervention_strategy_selector import InterventionStrategySelector
from .strategic_decision_regression_lock import StrategicDecisionRegressionLock


class StrategicDecisionRuntime:
    def __init__(self) -> None:
        self.scenario_engine = DecisionScenarioEngine()
        self.simulator = BoundedOutcomeSimulator()
        self.selector = InterventionStrategySelector()
        self.tracker = ExpectedActualOutcomeTracker()
        self.regression = StrategicDecisionRegressionLock()

    def run(
        self,
        discovery: Dict[str, Any],
        actual_outcome: Optional[str] = None,
        evidence_updates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        scenario = self.scenario_engine.build_scenario(discovery)
        simulations = self.simulator.simulate(scenario)
        recommendation = self.selector.select(scenario, simulations)
        outcome_record = self.tracker.create_record(recommendation)

        if actual_outcome is not None or evidence_updates:
            outcome_record = self.tracker.compare(
                outcome_record,
                actual_outcome=actual_outcome,
                evidence_updates=evidence_updates,
            )

        regression = self.regression.validate(scenario, simulations, recommendation)

        return {
            "layer": "strategic_decision_intelligence",
            "versions": {
                "decision_scenario_engine": "v16.96",
                "bounded_outcome_simulation": "v16.97",
                "intervention_strategy_selector": "v16.98",
                "expected_actual_outcome_tracker": "v16.99",
                "strategic_decision_regression_lock": "v17.00",
            },
            "scenario": scenario.to_dict(),
            "simulations": [sim.to_dict() for sim in simulations],
            "recommendation": recommendation.to_dict(),
            "outcome_record": outcome_record.to_dict(),
            "regression": regression,
        }
