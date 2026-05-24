
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


HANDSHAKE_VERSION = "v18.19"
HANDSHAKE_NAME = "controlled_read_only_live_connectivity_handshake_stub"


@dataclass(frozen=True)
class ControlledLiveConnectivityHandshakeResult:
    version: str
    name: str
    status: str
    eligible_for_future_handshake: bool
    handshake_attempted: bool
    execution_performed: bool
    network_call_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    review_required: bool
    live_web_execution_enabled: bool
    ai_agent_execution_enabled: bool
    reason: str
    provider_id: Optional[str]
    requested_url: Optional[str]
    timestamp_utc: str
    governance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evaluate_controlled_read_only_live_connectivity_handshake(
    request: Optional[Mapping[str, Any]] = None,
    *,
    operator_explicitly_requested_handshake: bool = False,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
) -> ControlledLiveConnectivityHandshakeResult:
    payload: Mapping[str, Any] = request or {}
    provider_id = payload.get("provider_id")
    requested_url = payload.get("url") or payload.get("requested_url")

    governance = {
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "requires_operator_review": True,
        "review_gate_only": True,
        "approval_is_not_execution": True,
        "adapter_boundary_fail_closed": True,
    }

    if ai_agent_execution_enabled:
        status = "blocked"
        reason = "AI-agent execution remains disabled for governed web connectivity."
        eligible = False
    elif not operator_explicitly_requested_handshake:
        status = "held_for_review"
        reason = "Controlled live connectivity handshake requires explicit future operator enablement."
        eligible = False
    elif not live_web_execution_enabled:
        status = "fail_closed"
        reason = "Live web execution remains disabled; handshake stub refuses execution."
        eligible = False
    else:
        status = "stubbed_not_executed"
        reason = "Handshake scaffolding exists, but v18.19 does not perform real connectivity."
        eligible = True

    return ControlledLiveConnectivityHandshakeResult(
        version=HANDSHAKE_VERSION,
        name=HANDSHAKE_NAME,
        status=status,
        eligible_for_future_handshake=eligible,
        handshake_attempted=False,
        execution_performed=False,
        network_call_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        review_required=True,
        live_web_execution_enabled=bool(live_web_execution_enabled),
        ai_agent_execution_enabled=bool(ai_agent_execution_enabled),
        reason=reason,
        provider_id=str(provider_id) if provider_id is not None else None,
        requested_url=str(requested_url) if requested_url is not None else None,
        timestamp_utc=_utc_now(),
        governance=governance,
    )


def build_controlled_read_only_live_connectivity_review_payload(
    request: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    result = evaluate_controlled_read_only_live_connectivity_handshake(request)
    return {
        "review_type": HANDSHAKE_NAME,
        "version": HANDSHAKE_VERSION,
        "result": result.to_dict(),
        "operator_notice": (
            "This is a fail-closed connectivity handshake stub. "
            "It prepares review structure only and performs no external call."
        ),
    }


__all__ = [
    "HANDSHAKE_VERSION",
    "HANDSHAKE_NAME",
    "ControlledLiveConnectivityHandshakeResult",
    "evaluate_controlled_read_only_live_connectivity_handshake",
    "build_controlled_read_only_live_connectivity_review_payload",
]
