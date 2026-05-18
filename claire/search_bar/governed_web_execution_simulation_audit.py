from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4


CONFIRMATION_TEXT = "I understand this is an eligibility simulation only"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class GovernedWebSimulationAuditEvent:
    audit_id: str
    created_at: str
    request_id: str
    operator_id: str
    requested_mode: str
    confirmation_text_present: bool
    confirmation_text_valid: bool
    approval_recorded: bool
    eligible_for_simulation_review: bool
    execution_performed: bool = False
    live_web_execution_performed: bool = False
    runtime_truth_mutated: bool = False
    autonomous_agent_execution_performed: bool = False
    automatic_update_performed: bool = False
    decision: str = "simulation_audit_only"
    reasons: List[str] = field(default_factory=list)
    source_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_simulation_audit_event(
    request: Mapping[str, Any],
    *,
    operator_id: str = "operator",
    audit_id: Optional[str] = None,
) -> Dict[str, Any]:
    request_id = str(request.get("request_id") or request.get("id") or f"request-{uuid4().hex[:10]}")
    requested_mode = str(request.get("requested_mode") or request.get("mode") or "governed_web")
    confirmation_text = str(request.get("confirmation_text") or "").strip()
    approval_recorded = bool(request.get("approval_recorded") or request.get("approved") or False)

    confirmation_text_present = bool(confirmation_text)
    confirmation_text_valid = confirmation_text == CONFIRMATION_TEXT
    eligible = bool(approval_recorded and confirmation_text_valid)

    reasons: List[str] = []
    if not approval_recorded:
        reasons.append("operator_approval_not_recorded")
    if not confirmation_text_present:
        reasons.append("confirmation_text_missing")
    elif not confirmation_text_valid:
        reasons.append("confirmation_text_invalid")
    if eligible:
        reasons.append("eligible_for_simulation_review_only")
    reasons.extend(
        [
            "execution_blocked_by_policy",
            "live_web_execution_disabled",
            "runtime_truth_mutation_disabled",
            "autonomous_agent_execution_disabled",
            "automatic_updates_disabled",
        ]
    )

    event = GovernedWebSimulationAuditEvent(
        audit_id=audit_id or f"sim-audit-{uuid4().hex[:12]}",
        created_at=_utc_now(),
        request_id=request_id,
        operator_id=operator_id,
        requested_mode=requested_mode,
        confirmation_text_present=confirmation_text_present,
        confirmation_text_valid=confirmation_text_valid,
        approval_recorded=approval_recorded,
        eligible_for_simulation_review=eligible,
        execution_performed=False,
        live_web_execution_performed=False,
        runtime_truth_mutated=False,
        autonomous_agent_execution_performed=False,
        automatic_update_performed=False,
        decision="eligible_for_simulation_review_only" if eligible else "not_eligible_for_simulation_review",
        reasons=reasons,
        source_payload=dict(request),
    )
    return event.to_dict()


def assert_non_executing_audit_event(event: Mapping[str, Any]) -> bool:
    forbidden_true_fields = [
        "execution_performed",
        "live_web_execution_performed",
        "runtime_truth_mutated",
        "autonomous_agent_execution_performed",
        "automatic_update_performed",
    ]
    for field_name in forbidden_true_fields:
        if bool(event.get(field_name)):
            raise AssertionError(f"{field_name} must remain false")
    return True


class GovernedWebExecutionSimulationAuditTrail:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def record(
        self,
        request: Mapping[str, Any],
        *,
        operator_id: str = "operator",
    ) -> Dict[str, Any]:
        event = build_simulation_audit_event(request, operator_id=operator_id)
        assert_non_executing_audit_event(event)
        self._events.append(event)
        return event

    def list_events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    def latest(self) -> Optional[Dict[str, Any]]:
        if not self._events:
            return None
        return self._events[-1]
