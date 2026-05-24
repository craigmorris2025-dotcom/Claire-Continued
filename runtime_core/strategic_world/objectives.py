from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StakeholderObjective:
    id: str
    label: str
    weights: dict[str, float]


@dataclass(frozen=True)
class StrategicWorldOption:
    id: str
    label: str
    description: str
    affected_domains: list[str]
    expected_impacts: dict[str, float]
    risk_class: str = "medium"
    execution_boundary: str = "recommendation_only"


@dataclass(frozen=True)
class StrategicWorldRecommendation:
    option_id: str
    score: float
    per_stakeholder_scores: dict[str, float]


def default_stakeholders() -> list[StakeholderObjective]:
    return [
        StakeholderObjective("operator", "Operator", {"readiness": 0.35, "evidence": 0.25, "reversibility": 0.25, "risk_reduction": 0.15}),
        StakeholderObjective("buyer", "Buyer / Acquirer", {"readiness": 0.28, "value_capture": 0.30, "evidence": 0.24, "risk_reduction": 0.18}),
        StakeholderObjective("governance", "Governance", {"risk_reduction": 0.40, "evidence": 0.30, "reversibility": 0.20, "readiness": 0.10}),
    ]


class MultiStakeholderCoordinator:
    def __init__(self, stakeholders: list[StakeholderObjective] | None = None) -> None:
        self._stakeholders = stakeholders or default_stakeholders()

    def evaluate(self, options: list[StrategicWorldOption]) -> list[StrategicWorldRecommendation]:
        ranked: list[StrategicWorldRecommendation] = []
        for option in options:
            per: dict[str, float] = {}
            total = 0.0
            for stakeholder in self._stakeholders:
                score = sum(
                    float(weight) * float(option.expected_impacts.get(metric, 0.0))
                    for metric, weight in stakeholder.weights.items()
                )
                per[stakeholder.id] = round(score, 4)
                total += score
            ranked.append(
                StrategicWorldRecommendation(
                    option_id=option.id,
                    score=round(total, 4),
                    per_stakeholder_scores=per,
                )
            )
        return sorted(ranked, key=lambda item: item.score, reverse=True)
