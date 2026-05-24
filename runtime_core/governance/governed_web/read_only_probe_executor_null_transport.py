from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


NULL_TRANSPORT_VERSION = "v18.27.2"
NULL_TRANSPORT_NAME = "read_only_probe_executor_null_transport_empty_query_order_repair"


@dataclass(frozen=True)
class ReadOnlyProbeExecutorNullTransportResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    executor_created: bool
    executor_lifecycle_simulated: bool
    authorization_ready_for_next_build: bool
    null_transport_active: bool
    real_transport_active: bool
    probe_attempted: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    transport_block_reason: str
    decision: str
    reason: str
    timestamp_utc: str
    authorization_audit: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _empty_authorization_audit(normalized_query: str) -> Dict[str, Any]:
    return {
        "status": "skipped_for_invalid_request",
        "reason": "Authorization audit skipped because query is empty.",
        "authorization_ready_for_next_build": False,
        "query": normalized_query,
        "normalized_query": normalized_query,
        "provider_id": "governed-web-search-provider-stub",
        "planned_method": "GET",
        "planned_url": None,
        "execution_performed": False,
        "network_call_performed": False,
        "external_request_performed": False,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "response_body_fetched": False,
    }


def _safe_authorization_audit(request: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from runtime_core.governance.governed_web.pre_live_probe_authorization_audit import (
            evaluate_pre_live_probe_authorization_audit,
        )

        return evaluate_pre_live_probe_authorization_audit(
            request,
            live_web_execution_enabled=True,
            operator_approved_planning=True,
            explicit_operator_enablement_present=True,
            probe_executor_enabled=True,
            provider_readiness_passed=True,
            allowlist_policy_passed=True,
            rate_limit_policy_passed=True,
            source_trust_policy_passed=True,
            dry_run_eligibility_passed=True,
        ).to_dict()
    except Exception as exc:
        normalized_query = _normalize_query(request.get("query"))
        return {
            "status": "authorization_audit_unavailable",
            "reason": str(exc),
            "authorization_ready_for_next_build": False,
            "query": str(request.get("query") or ""),
            "normalized_query": normalized_query,
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
        }


def execute_read_only_probe_with_null_transport(
    request: Optional[Mapping[str, Any]] = None,
) -> ReadOnlyProbeExecutorNullTransportResult:
    payload: Mapping[str, Any] = request or {}
    raw_query = payload.get("query") or ""
    normalized_query = _normalize_query(raw_query)

    # v18.27.2 repair:
    # Invalid request checks happen before authorization audit checks.
    if not normalized_query:
        audit = _empty_authorization_audit(normalized_query)
    else:
        audit = _safe_authorization_audit(payload)

    normalized_query = _normalize_query(audit.get("normalized_query") or normalized_query)
    provider_id = str(
        audit.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )
    planned_method = str(audit.get("planned_method") or "GET")
    planned_url = audit.get("planned_url")

    safeguards = {
        "null_transport_only": True,
        "real_transport_forbidden": True,
        "socket_creation_forbidden": True,
        "http_client_forbidden": True,
        "response_fetch_forbidden": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "invalid_request_checked_before_authorization": True,
        "fail_closed": True,
    }

    invalid_audit = any(
        bool(audit.get(key))
        for key in (
            "authorization_granted",
            "execution_gate_passed",
            "execution_permitted",
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "response_body_fetched",
        )
    )

    if not normalized_query:
        status = "invalid_request"
        decision = "hold"
        reason = "Probe executor requires a non-empty normalized query."
        lifecycle_simulated = False
    elif invalid_audit:
        status = "invalid_audit_rejected"
        decision = "reject"
        reason = "Authorization audit reported execution or authorization unexpectedly."
        lifecycle_simulated = False
    elif not audit.get("authorization_ready_for_next_build"):
        status = "authorization_not_ready"
        decision = "hold"
        reason = "Authorization readiness was not achieved."
        lifecycle_simulated = False
    elif not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Probe executor requires a planned URL."
        lifecycle_simulated = False
    else:
        status = "null_transport_execution_simulated"
        decision = "hold"
        reason = "Executor lifecycle simulated successfully using null transport only."
        lifecycle_simulated = True

    return ReadOnlyProbeExecutorNullTransportResult(
        version=NULL_TRANSPORT_VERSION,
        name=NULL_TRANSPORT_NAME,
        status=status,
        query=str(raw_query or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        executor_created=True,
        executor_lifecycle_simulated=lifecycle_simulated,
        authorization_ready_for_next_build=bool(audit.get("authorization_ready_for_next_build")),
        null_transport_active=True,
        real_transport_active=False,
        probe_attempted=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        response_body_fetched=False,
        response_status_code=None,
        transport_block_reason="Real HTTP transport layer is replaced by fail-closed null transport.",
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        authorization_audit=dict(audit),
        safeguards=safeguards,
    )


def build_dashboard_null_transport_payload(query: str) -> Dict[str, Any]:
    result = execute_read_only_probe_with_null_transport({"query": query})
    return {
        "dashboard_surface": "search_bar",
        "mode": "read_only_probe_executor_null_transport",
        "version": NULL_TRANSPORT_VERSION,
        "probe_executor": result.to_dict(),
        "ui_notice": "Probe executor lifecycle simulated using null transport. No network traffic occurred.",
    }


__all__ = [
    "NULL_TRANSPORT_VERSION",
    "NULL_TRANSPORT_NAME",
    "ReadOnlyProbeExecutorNullTransportResult",
    "execute_read_only_probe_with_null_transport",
    "build_dashboard_null_transport_payload",
]
