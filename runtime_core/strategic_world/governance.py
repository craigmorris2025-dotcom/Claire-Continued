from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ActionType = Literal[
    "run_pipeline",
    "propose_strategy",
    "propose_intervention",
    "deploy_system_replacement",
    "export_package",
    "promote_runtime_truth",
    "execute_external_action",
    "update_runtime",
]

RiskClass = Literal["low", "medium", "high", "unbounded"]


@dataclass(frozen=True)
class HardConstraint:
    id: str
    description: str
    applies_to_actions: list[ActionType]
    prohibited_phrases: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StakeholderRole:
    id: str
    name: str
    allowed_actions: list[ActionType]
    max_risk: RiskClass


@dataclass(frozen=True)
class ClaireCharter:
    version: str
    purpose: str
    hard_constraints: list[HardConstraint]
    roles: dict[str, StakeholderRole]


@dataclass(frozen=True)
class GovernanceContext:
    actor_role_id: str
    action: ActionType
    risk_class: RiskClass
    objective_summary: str


@dataclass(frozen=True)
class GovernanceDecision:
    allowed: bool
    reason: str
    requires_human_approval: bool = False
    execution_boundary: str = "recommendation_only_no_external_action"


def default_charter() -> ClaireCharter:
    return ClaireCharter(
        version="claire.strategic_world.charter.v1",
        purpose="Allow strategic-world analysis and recommendations while blocking autonomous intervention, runtime mutation, or external action.",
        hard_constraints=[
            HardConstraint(
                id="no_harmful_or_destabilizing_objectives",
                description="Reject objectives that optimize for harm, instability, coercion, or exploitative vulnerability use.",
                applies_to_actions=[
                    "propose_strategy",
                    "propose_intervention",
                    "deploy_system_replacement",
                    "promote_runtime_truth",
                    "execute_external_action",
                    "update_runtime",
                ],
                prohibited_phrases=[
                    "maximize instability",
                    "cause systemic harm",
                    "exploit vulnerability without mitigation",
                    "coerce",
                    "evade oversight",
                ],
            ),
            HardConstraint(
                id="no_autonomous_external_execution",
                description="Strategic-world outputs may recommend or queue review only; external action is never allowed from this layer.",
                applies_to_actions=["execute_external_action", "deploy_system_replacement", "update_runtime"],
            ),
        ],
        roles={
            "runtime": StakeholderRole(
                id="runtime",
                name="Claire Runtime",
                allowed_actions=["run_pipeline", "propose_strategy", "propose_intervention", "export_package"],
                max_risk="medium",
            ),
            "operator": StakeholderRole(
                id="operator",
                name="Human Operator",
                allowed_actions=[
                    "run_pipeline",
                    "propose_strategy",
                    "propose_intervention",
                    "deploy_system_replacement",
                    "export_package",
                    "promote_runtime_truth",
                ],
                max_risk="high",
            ),
        },
    )


class GovernanceGuard:
    def __init__(self, charter: ClaireCharter | None = None) -> None:
        self._charter = charter or default_charter()

    def evaluate(self, ctx: GovernanceContext) -> GovernanceDecision:
        role = self._charter.roles.get(ctx.actor_role_id)
        if role is None:
            return GovernanceDecision(False, f"Unknown role: {ctx.actor_role_id}")
        if ctx.action not in role.allowed_actions:
            return GovernanceDecision(False, f"Action {ctx.action} is not permitted for role {role.id}")
        if self._risk_level(ctx.risk_class) > self._risk_level(role.max_risk):
            return GovernanceDecision(False, f"Risk {ctx.risk_class} exceeds max {role.max_risk} for role {role.id}")
        lowered = ctx.objective_summary.lower()
        for constraint in self._charter.hard_constraints:
            if ctx.action not in constraint.applies_to_actions:
                continue
            if constraint.id == "no_autonomous_external_execution" and ctx.action in {
                "execute_external_action",
                "deploy_system_replacement",
                "update_runtime",
            }:
                return GovernanceDecision(False, f"Hard constraint violated: {constraint.id}")
            if any(phrase in lowered for phrase in constraint.prohibited_phrases):
                return GovernanceDecision(False, f"Hard constraint violated: {constraint.id}")
        requires_approval = ctx.risk_class == "high"
        return GovernanceDecision(
            allowed=True,
            reason="Allowed to propose under charter; execution remains blocked.",
            requires_human_approval=requires_approval,
        )

    @staticmethod
    def _risk_level(value: RiskClass) -> int:
        return {"low": 1, "medium": 2, "high": 3, "unbounded": 4}[value]
