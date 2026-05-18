from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _force_false_flags(payload: Mapping[str, Any]) -> Dict[str, Any]:
    copied = dict(payload)
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        copied[field_name] = False
    return copied


@dataclass(frozen=True)
class GovernedWebSimulationResultCard:
    card_id: str
    created_at: str
    request_id: str
    title: str
    status: str
    decision: str
    eligible_for_simulation_review: bool
    approval_recorded: bool
    confirmation_text_valid: bool
    execution_performed: bool = False
    live_web_execution_performed: bool = False
    runtime_truth_mutated: bool = False
    autonomous_agent_execution_performed: bool = False
    automatic_update_performed: bool = False
    safety_badges: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    source_event: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for field_name in FORBIDDEN_EXECUTION_FIELDS:
            data[field_name] = False
        return data


def assert_viewer_card_is_non_executing(card: Mapping[str, Any]) -> bool:
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(card.get(field_name)):
            raise AssertionError(f"{field_name} must remain false in viewer contract")
    return True


def build_simulation_result_card(event: Mapping[str, Any]) -> Dict[str, Any]:
    safe_event = _force_false_flags(event)

    request_id = str(safe_event.get("request_id") or "unknown-request")
    eligible = bool(safe_event.get("eligible_for_simulation_review"))
    approval_recorded = bool(safe_event.get("approval_recorded"))
    confirmation_text_valid = bool(safe_event.get("confirmation_text_valid"))
    decision = str(safe_event.get("decision") or ("eligible_for_simulation_review_only" if eligible else "not_eligible_for_simulation_review"))

    status = "review_eligible_simulation_only" if eligible else "blocked_or_incomplete_simulation_review"
    title = "Governed web simulation review eligible" if eligible else "Governed web simulation review blocked"

    badges = [
        "review_gated",
        "non_executing",
        "live_web_disabled",
        "runtime_truth_mutation_disabled",
        "ai_agent_disabled",
        "automatic_updates_disabled",
    ]

    reasons = list(safe_event.get("reasons") or [])
    if eligible and "eligible_for_simulation_review_only" not in reasons:
        reasons.append("eligible_for_simulation_review_only")
    if "execution_blocked_by_policy" not in reasons:
        reasons.append("execution_blocked_by_policy")

    card = GovernedWebSimulationResultCard(
        card_id=f"sim-result-{request_id}",
        created_at=_utc_now(),
        request_id=request_id,
        title=title,
        status=status,
        decision=decision,
        eligible_for_simulation_review=eligible,
        approval_recorded=approval_recorded,
        confirmation_text_valid=confirmation_text_valid,
        execution_performed=False,
        live_web_execution_performed=False,
        runtime_truth_mutated=False,
        autonomous_agent_execution_performed=False,
        automatic_update_performed=False,
        safety_badges=badges,
        reasons=reasons,
        source_event=safe_event,
    ).to_dict()

    assert_viewer_card_is_non_executing(card)
    return card


def build_simulation_result_view(events: List[Mapping[str, Any]]) -> Dict[str, Any]:
    cards = [build_simulation_result_card(event) for event in events]
    for card in cards:
        assert_viewer_card_is_non_executing(card)

    eligible_count = sum(1 for card in cards if card["eligible_for_simulation_review"])
    blocked_count = len(cards) - eligible_count

    view = {
        "view": "governed_web_simulation_results",
        "created_at": _utc_now(),
        "summary": {
            "total": len(cards),
            "eligible_for_simulation_review": eligible_count,
            "blocked_or_incomplete": blocked_count,
            "execution_performed": False,
            "live_web_execution_performed": False,
            "runtime_truth_mutated": False,
            "autonomous_agent_execution_performed": False,
            "automatic_update_performed": False,
        },
        "cards": cards,
        "safety_state": {
            "approval_equals_execution": False,
            "review_gated": True,
            "execution_enabled": False,
            "live_web_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
        },
    }

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(view["summary"].get(field_name)):
            raise AssertionError(f"{field_name} must remain false in viewer summary")

    return view
