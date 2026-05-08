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
