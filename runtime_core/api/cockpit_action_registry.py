from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Literal

GovernanceClass = Literal[
    "safe_read",
    "operator_review",
    "quarantined_job",
    "proposal_only",
    "blocked_authority",
]

ActionState = Literal["enabled", "disabled", "blocked", "proposal_only"]


@dataclass(frozen=True)
class CockpitAction:
    action_id: str
    label: str
    category: str
    governance_class: GovernanceClass
    state: ActionState
    requires_manual_promotion: bool
    requires_quarantine: bool
    mutates_runtime_truth: bool
    triggers_autonomous_execution: bool
    blocked_reason: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _actions() -> List[CockpitAction]:
    return [
        CockpitAction(
            action_id="inspect_payload_health",
            label="Inspect Payload Health",
            category="monitoring",
            governance_class="safe_read",
            state="enabled",
            requires_manual_promotion=False,
            requires_quarantine=False,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Read-only cockpit action for inspecting canonical payload health.",
        ),
        CockpitAction(
            action_id="inspect_runtime_locks",
            label="Inspect Runtime Locks",
            category="governance",
            governance_class="safe_read",
            state="enabled",
            requires_manual_promotion=False,
            requires_quarantine=False,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Read-only verification of active governance locks.",
        ),
        CockpitAction(
            action_id="review_evidence_basket",
            label="Review Evidence Basket",
            category="review",
            governance_class="operator_review",
            state="enabled",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Operator review of quarantined evidence before any promotion decision.",
        ),
        CockpitAction(
            action_id="export_reviewed_package",
            label="Export Reviewed Package",
            category="export",
            governance_class="operator_review",
            state="enabled",
            requires_manual_promotion=True,
            requires_quarantine=False,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Export only reviewed/approved package material.",
        ),
        CockpitAction(
            action_id="start_bounded_web_job",
            label="Start Bounded Web Job",
            category="web_jobs",
            governance_class="quarantined_job",
            state="enabled",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Operator-triggered bounded web job that stores results in quarantine.",
        ),
        CockpitAction(
            action_id="inspect_source_lineage",
            label="Inspect Source Lineage",
            category="evidence",
            governance_class="safe_read",
            state="enabled",
            requires_manual_promotion=False,
            requires_quarantine=False,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Read-only inspection of source lineage and trust scoring.",
        ),
        CockpitAction(
            action_id="request_mutation_proposal",
            label="Request Mutation Proposal",
            category="proposal",
            governance_class="proposal_only",
            state="proposal_only",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=False,
            description="Creates a reviewable proposal only; does not mutate runtime truth.",
        ),
        CockpitAction(
            action_id="apply_runtime_mutation",
            label="Apply Runtime Mutation",
            category="blocked_authority",
            governance_class="blocked_authority",
            state="blocked",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=True,
            triggers_autonomous_execution=False,
            blocked_reason="Runtime mutation authority remains disabled at this plateau.",
            description="Blocked action reserved for future governed mutation framework.",
        ),
        CockpitAction(
            action_id="enable_continuous_crawling",
            label="Enable Continuous Crawling",
            category="blocked_authority",
            governance_class="blocked_authority",
            state="blocked",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=False,
            triggers_autonomous_execution=True,
            blocked_reason="Continuous crawling remains blocked; bounded jobs only.",
            description="Blocked action reserved for future scheduler/crawler authority.",
        ),
        CockpitAction(
            action_id="enable_automatic_updates",
            label="Enable Automatic Updates",
            category="blocked_authority",
            governance_class="blocked_authority",
            state="blocked",
            requires_manual_promotion=True,
            requires_quarantine=True,
            mutates_runtime_truth=True,
            triggers_autonomous_execution=True,
            blocked_reason="Automatic updates remain blocked; proposal-only update flow required.",
            description="Blocked action reserved for future update authority framework.",
        ),
    ]


def get_cockpit_action_registry() -> dict:
    actions = [a.to_dict() for a in _actions()]
    by_id: Dict[str, dict] = {a["action_id"]: a for a in actions}
    return {
        "version": "v19.89.8-S184",
        "plateau": "visual_cockpit_controls_and_monitoring_backend",
        "registry_name": "cockpit_action_registry",
        "authority_model": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_truth_write_blocked": True,
            "runtime_mutation_blocked": True,
            "automatic_updates_blocked": True,
            "autonomous_execution_blocked": True,
            "manual_promotion_mandatory": True,
            "quarantine_mandatory": True,
            "continuous_crawling_blocked": True,
        },
        "counts": {
            "total": len(actions),
            "enabled": sum(1 for a in actions if a["state"] == "enabled"),
            "proposal_only": sum(1 for a in actions if a["state"] == "proposal_only"),
            "blocked": sum(1 for a in actions if a["state"] == "blocked"),
        },
        "actions": actions,
        "actions_by_id": by_id,
    }


def get_cockpit_action(action_id: str) -> dict | None:
    return get_cockpit_action_registry()["actions_by_id"].get(action_id)


def assert_registry_safe() -> None:
    registry = get_cockpit_action_registry()
    locks = registry["authority_model"]
    assert locks["backend_owns_truth"] is True
    assert locks["cockpit_presentation_only"] is True
    assert locks["runtime_truth_write_blocked"] is True
    assert locks["runtime_mutation_blocked"] is True
    assert locks["automatic_updates_blocked"] is True
    assert locks["autonomous_execution_blocked"] is True
    assert locks["manual_promotion_mandatory"] is True
    assert locks["quarantine_mandatory"] is True
    assert locks["continuous_crawling_blocked"] is True
    for action in registry["actions"]:
        if action["mutates_runtime_truth"] or action["triggers_autonomous_execution"]:
            assert action["state"] == "blocked"
            assert action["blocked_reason"]
