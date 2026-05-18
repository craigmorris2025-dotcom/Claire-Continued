from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


REVIEW_RECORD_VERSION = "v18.20"
REVIEW_RECORD_NAME = "controlled_live_connectivity_handshake_review_record"


@dataclass(frozen=True)
class ControlledLiveConnectivityHandshakeReviewRecord:
    version: str
    name: str
    status: str
    review_record_created: bool
    review_required: bool
    approved_for_execution: bool
    execution_performed: bool
    network_call_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    handshake_attempted: bool
    operator_intent: str
    provider_id: Optional[str]
    requested_url: Optional[str]
    decision: str
    reason: str
    timestamp_utc: str
    safeguards: Dict[str, Any]
    source_handshake: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_bool(payload: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = payload.get(key, default)
    return bool(value)


def create_controlled_live_connectivity_handshake_review_record(
    handshake_result: Optional[Mapping[str, Any]] = None,
    *,
    operator_intent: str = "review",
    operator_approved: bool = False,
) -> ControlledLiveConnectivityHandshakeReviewRecord:
    # Review-only record. Approval is intentionally recorded as non-executing.
    source: Mapping[str, Any] = handshake_result or {}
    provider_id = source.get("provider_id")
    requested_url = source.get("requested_url") or source.get("url")
    source_status = str(source.get("status", "missing_handshake_result"))

    safeguards = {
        "review_only": True,
        "approval_is_not_execution": True,
        "requires_future_execution_adapter": True,
        "requires_explicit_live_enablement": True,
        "requires_operator_review": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "fail_closed": True,
    }

    if _read_bool(source, "network_call_performed"):
        status = "invalid_source_rejected"
        decision = "reject"
        reason = "Source handshake reported network_call_performed=True; review record rejects it."
    elif _read_bool(source, "execution_performed"):
        status = "invalid_source_rejected"
        decision = "reject"
        reason = "Source handshake reported execution_performed=True; review record rejects it."
    elif _read_bool(source, "runtime_truth_mutated"):
        status = "invalid_source_rejected"
        decision = "reject"
        reason = "Source handshake reported runtime_truth_mutated=True; review record rejects it."
    elif source_status in {"stubbed_not_executed", "held_for_review", "fail_closed"}:
        status = "recorded_for_review"
        decision = "hold"
        reason = "Handshake review record created; no execution path is available in v18.20."
    else:
        status = "recorded_insufficient_source"
        decision = "hold"
        reason = "Handshake source is absent or incomplete; record is held for review."

    return ControlledLiveConnectivityHandshakeReviewRecord(
        version=REVIEW_RECORD_VERSION,
        name=REVIEW_RECORD_NAME,
        status=status,
        review_record_created=True,
        review_required=True,
        approved_for_execution=False,
        execution_performed=False,
        network_call_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        handshake_attempted=False,
        operator_intent=str(operator_intent or "review"),
        provider_id=str(provider_id) if provider_id is not None else None,
        requested_url=str(requested_url) if requested_url is not None else None,
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        safeguards=safeguards,
        source_handshake=dict(source),
    )


def create_review_record_from_request(
    request: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    # Uses the v18.19 handshake evaluator when present, then records review only.
    try:
        from claire.governance.governed_web.live_connectivity_handshake import (
            evaluate_controlled_read_only_live_connectivity_handshake,
        )

        handshake = evaluate_controlled_read_only_live_connectivity_handshake(request).to_dict()
    except Exception as exc:
        handshake = {
            "status": "handshake_import_unavailable",
            "reason": str(exc),
            "execution_performed": False,
            "network_call_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }

    record = create_controlled_live_connectivity_handshake_review_record(handshake)
    return record.to_dict()


__all__ = [
    "REVIEW_RECORD_VERSION",
    "REVIEW_RECORD_NAME",
    "ControlledLiveConnectivityHandshakeReviewRecord",
    "create_controlled_live_connectivity_handshake_review_record",
    "create_review_record_from_request",
]
