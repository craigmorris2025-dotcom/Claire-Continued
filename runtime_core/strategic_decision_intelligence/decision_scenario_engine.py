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
