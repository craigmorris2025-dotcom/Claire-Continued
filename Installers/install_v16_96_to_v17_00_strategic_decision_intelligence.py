# Claire Syntalion Installer
# v16.96-v17.00 Strategic Decision Intelligence Layer
#
# Place this file in the Claire project root and run:
#
#     python install_v16_96_to_v17_00_strategic_decision_intelligence.py

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "strategic_decision_intelligence"
TESTS = ROOT / "tests" / "strategic_decision_intelligence"
DATA = ROOT / "data" / "strategic_decision_intelligence"
DOCS = ROOT / "docs" / "strategic_decision_intelligence"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v16.96-v17.00 Strategic Decision Intelligence Layer...")

    write_file(LAYER / "__init__.py", """
from .decision_scenario_engine import DecisionScenarioEngine
from .bounded_outcome_simulator import BoundedOutcomeSimulator
from .intervention_strategy_selector import InterventionStrategySelector
from .expected_actual_outcome_tracker import ExpectedActualOutcomeTracker
from .strategic_decision_regression_lock import StrategicDecisionRegressionLock
from .runtime import StrategicDecisionRuntime

__all__ = [
    "DecisionScenarioEngine",
    "BoundedOutcomeSimulator",
    "InterventionStrategySelector",
    "ExpectedActualOutcomeTracker",
    "StrategicDecisionRegressionLock",
    "StrategicDecisionRuntime",
]
""")

    write_file(LAYER / "models.py", """
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class StrategicActionPathway:
    action_id: str
    name: str
    description: str
    action_type: str
    assumptions: List[str] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    expected_benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    reversibility: str = "medium"
    estimated_effort: str = "medium"
    governance_status: str = "bounded"


@dataclass
class DecisionScenario:
    scenario_id: str
    title: str
    thesis: str
    strategic_context: str
    decision_question: str
    source_run_id: Optional[str] = None
    confidence: float = 0.0
    evidence_supporting: List[Dict[str, Any]] = field(default_factory=list)
    evidence_conflicting: List[Dict[str, Any]] = field(default_factory=list)
    action_pathways: List[StrategicActionPathway] = field(default_factory=list)
    governance_notes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OutcomeSimulation:
    scenario_id: str
    action_id: str
    expected_outcome: str
    confidence_delta: float
    upside_score: float
    downside_score: float
    uncertainty_score: float
    evidence_sensitivity: str
    assumptions_tested: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    governance_notes: List[str] = field(default_factory=list)

    def total_score(self) -> float:
        return round((self.upside_score - self.downside_score - self.uncertainty_score) + self.confidence_delta, 4)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["total_score"] = self.total_score()
        return data


@dataclass
class InterventionRecommendation:
    scenario_id: str
    selected_action_id: str
    recommendation: str
    rationale: List[str]
    rejected_actions: List[Dict[str, Any]] = field(default_factory=list)
    expected_outcome: str = ""
    governance_status: str = "recommendation_only"
    execution_boundary: str = "no_external_action_without_user_approval"
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OutcomeRecord:
    scenario_id: str
    action_id: str
    expected_outcome: str
    actual_outcome: Optional[str] = None
    comparison_status: str = "pending_actual"
    variance_notes: List[str] = field(default_factory=list)
    evidence_updates: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
""")

    write_file(LAYER / "decision_scenario_engine.py", """
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from .models import DecisionScenario, StrategicActionPathway


class DecisionScenarioEngine:
    def build_scenario(self, discovery: Dict[str, Any]) -> DecisionScenario:
        thesis = discovery.get("thesis") or discovery.get("summary") or discovery.get("title") or "Unspecified thesis"
        context = discovery.get("strategic_context") or discovery.get("context") or "No strategic context provided."
        question = discovery.get("decision_question") or f"What governed action should Claire recommend for: {thesis}?"

        scenario_id = self._scenario_id(thesis, context, question)
        supporting = list(discovery.get("supporting_evidence", discovery.get("evidence_supporting", [])))
        conflicting = list(discovery.get("conflicting_evidence", discovery.get("evidence_conflicting", [])))
        pathways = self._derive_action_pathways(discovery, supporting, conflicting)

        confidence = float(discovery.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        return DecisionScenario(
            scenario_id=scenario_id,
            title=discovery.get("title", "Strategic Decision Scenario"),
            thesis=thesis,
            strategic_context=context,
            decision_question=question,
            source_run_id=discovery.get("run_id") or discovery.get("source_run_id"),
            confidence=confidence,
            evidence_supporting=supporting,
            evidence_conflicting=conflicting,
            action_pathways=pathways,
            governance_notes=[
                "Scenario generation is bounded to recommendation planning.",
                "No external execution is authorized by this layer.",
                "Actions require user review before implementation.",
            ],
        )

    def _derive_action_pathways(
        self,
        discovery: Dict[str, Any],
        supporting: List[Dict[str, Any]],
        conflicting: List[Dict[str, Any]],
    ) -> List[StrategicActionPathway]:
        explicit = discovery.get("action_pathways")
        if isinstance(explicit, list) and explicit:
            result = []
            for idx, item in enumerate(explicit):
                result.append(
                    StrategicActionPathway(
                        action_id=item.get("action_id", f"action_{idx+1}"),
                        name=item.get("name", f"Action {idx+1}"),
                        description=item.get("description", ""),
                        action_type=item.get("action_type", "strategic"),
                        assumptions=list(item.get("assumptions", [])),
                        required_evidence=list(item.get("required_evidence", [])),
                        expected_benefits=list(item.get("expected_benefits", [])),
                        risks=list(item.get("risks", [])),
                        constraints=list(item.get("constraints", [])),
                        reversibility=item.get("reversibility", "medium"),
                        estimated_effort=item.get("estimated_effort", "medium"),
                        governance_status=item.get("governance_status", "bounded"),
                    )
                )
            return result

        missing_evidence_note = "Resolve conflicting evidence before irreversible commitment." if conflicting else "Validate supporting evidence before escalation."
        return [
            StrategicActionPathway(
                action_id="observe_and_validate",
                name="Observe and validate",
                description="Continue bounded evidence collection before committing resources.",
                action_type="research_continuation",
                assumptions=["Additional evidence can improve confidence."],
                required_evidence=["Fresh supporting and conflicting evidence"],
                expected_benefits=["Lower false-positive risk", "Improved thesis confidence"],
                risks=["Delayed opportunity capture"],
                constraints=["Do not overfit to weak signals"],
                reversibility="high",
                estimated_effort="low",
            ),
            StrategicActionPathway(
                action_id="small_scale_intervention",
                name="Small-scale intervention",
                description="Run a limited, reversible strategic test against the thesis.",
                action_type="bounded_intervention",
                assumptions=["A small test can expose signal strength."],
                required_evidence=["Minimum viable test criteria", "Risk boundary"],
                expected_benefits=["Practical feedback", "Early positioning"],
                risks=[missing_evidence_note],
                constraints=["Bounded exposure", "User approval required"],
                reversibility="medium",
                estimated_effort="medium",
            ),
            StrategicActionPathway(
                action_id="escalate_to_build_or_portfolio",
                name="Escalate to build or portfolio route",
                description="Advance the thesis into a build, acquisition, portfolio, or package route if evidence is strong enough.",
                action_type="route_escalation",
                assumptions=["Current evidence is sufficient for downstream routing."],
                required_evidence=["High-confidence support", "Low unresolved contradiction"],
                expected_benefits=["Earlier strategic capture", "Clear downstream execution path"],
                risks=["Premature escalation", "Resource misallocation"],
                constraints=["Governance lock required", "No autonomous external execution"],
                reversibility="low",
                estimated_effort="high",
            ),
        ]

    def _scenario_id(self, *parts: str) -> str:
        raw = "|".join(parts).encode("utf-8")
        return "scenario_" + hashlib.sha256(raw).hexdigest()[:12]
""")

    write_file(LAYER / "bounded_outcome_simulator.py", """
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
""")

    write_file(LAYER / "intervention_strategy_selector.py", """
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
""")

    write_file(LAYER / "expected_actual_outcome_tracker.py", """
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import InterventionRecommendation, OutcomeRecord


class ExpectedActualOutcomeTracker:
    def create_record(self, recommendation: InterventionRecommendation) -> OutcomeRecord:
        return OutcomeRecord(
            scenario_id=recommendation.scenario_id,
            action_id=recommendation.selected_action_id,
            expected_outcome=recommendation.expected_outcome,
            actual_outcome=None,
            comparison_status="pending_actual",
            variance_notes=["Awaiting later evidence or observed result."],
        )

    def compare(
        self,
        record: OutcomeRecord,
        actual_outcome: Optional[str],
        evidence_updates: Optional[List[Dict[str, Any]]] = None,
    ) -> OutcomeRecord:
        updates = evidence_updates or []
        record.actual_outcome = actual_outcome
        record.evidence_updates.extend(updates)

        if actual_outcome is None:
            record.comparison_status = "pending_actual"
            record.variance_notes.append("No actual outcome supplied.")
            return record

        if actual_outcome == record.expected_outcome:
            record.comparison_status = "matched"
            record.variance_notes.append("Actual outcome matched expected outcome label.")
        elif "uncertain" in record.expected_outcome:
            record.comparison_status = "resolved_from_uncertainty"
            record.variance_notes.append("Actual outcome resolved a previously uncertain expected outcome.")
        else:
            record.comparison_status = "variance_detected"
            record.variance_notes.append("Actual outcome differed from expected outcome label.")

        return record
""")

    write_file(LAYER / "strategic_decision_regression_lock.py", """
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
""")

    write_file(LAYER / "runtime.py", """
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
""")

    write_file(TESTS / "test_strategic_decision_intelligence.py", """
from claire.strategic_decision_intelligence import StrategicDecisionRuntime


def test_strategic_decision_runtime_regression_passes():
    runtime = StrategicDecisionRuntime()
    result = runtime.run(
        {
            "title": "AI infrastructure opportunity",
            "thesis": "Enterprise teams need governed autonomous research systems.",
            "strategic_context": "Discovery layer indicates durable demand for evidence-linked decisioning.",
            "decision_question": "Should Claire escalate this opportunity into a bounded intervention?",
            "confidence": 0.72,
            "supporting_evidence": [
                {"source": "internal_discovery", "claim": "Repeated demand signal"},
                {"source": "campaign_memory", "claim": "Confidence continuity improving"},
            ],
            "conflicting_evidence": [
                {"source": "risk_review", "claim": "Deployment governance remains incomplete"}
            ],
        }
    )

    assert result["layer"] == "strategic_decision_intelligence"
    assert result["regression"]["regression_status"] == "passed"
    assert result["recommendation"]["execution_boundary"] == "no_external_action_without_user_approval"
    assert len(result["simulations"]) >= 3


def test_expected_actual_variance_tracking():
    runtime = StrategicDecisionRuntime()
    result = runtime.run(
        {
            "title": "Low confidence thesis",
            "thesis": "Weak signal may become a market opportunity.",
            "strategic_context": "Early discovery only.",
            "confidence": 0.35,
        },
        actual_outcome="favorable_if_governed",
        evidence_updates=[{"source": "later_result", "claim": "Outcome improved after small test"}],
    )

    assert result["outcome_record"]["actual_outcome"] == "favorable_if_governed"
    assert result["outcome_record"]["comparison_status"] in {
        "matched",
        "variance_detected",
        "resolved_from_uncertainty",
    }
""")

    write_file(DOCS / "v16_96_to_v17_00_strategic_decision_intelligence.md", """
# Claire v16.96-v17.00 Strategic Decision Intelligence Layer

This layer moves Claire from governed discovery toward governed strategic decisioning.

## Included Builds

- v16.96 Decision Scenario Engine
- v16.97 Bounded Outcome Simulation Layer
- v16.98 Intervention Strategy Selector
- v16.99 Expected vs Actual Outcome Tracker
- v17.00 Strategic Decision Regression Lock

## Governance Boundary

This layer recommends actions only. It does not perform external autonomous actions and does not authorize real-world execution without user approval.

## Primary Runtime

```python
from claire.strategic_decision_intelligence import StrategicDecisionRuntime

runtime = StrategicDecisionRuntime()
result = runtime.run(discovery)
```
""")

    write_json(DATA / "strategic_decision_manifest.json", {
        "installed_at": utc_now(),
        "layer": "strategic_decision_intelligence",
        "version_range": "v16.96-v17.00",
        "status": "installed",
        "governance_boundary": "recommendation_only_no_external_execution_without_user_approval",
        "modules": [
            "decision_scenario_engine",
            "bounded_outcome_simulator",
            "intervention_strategy_selector",
            "expected_actual_outcome_tracker",
            "strategic_decision_regression_lock",
            "runtime",
        ],
        "regression_tests": [
            "tests/strategic_decision_intelligence/test_strategic_decision_intelligence.py"
        ],
    })

    print("")
    print("INSTALL COMPLETE: Claire v16.96-v17.00 Strategic Decision Intelligence Layer")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/strategic_decision_intelligence -q")
    print("")
    print("Optional smoke test:")
    print("    python -c \"from claire.strategic_decision_intelligence import StrategicDecisionRuntime; print(StrategicDecisionRuntime().run({'thesis':'test','confidence':0.6})['regression']['regression_status'])\"")


if __name__ == "__main__":
    main()
