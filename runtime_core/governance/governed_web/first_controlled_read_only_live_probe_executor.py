from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


LIVE_PROBE_EXECUTOR_VERSION = "v18.31"
LIVE_PROBE_EXECUTOR_NAME = "first_controlled_read_only_live_probe_executor"


@dataclass(frozen=True)
class FirstControlledReadOnlyLiveProbeExecutorResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    permission_ready_for_next_build: bool
    live_probe_executor_created: bool
    executor_lifecycle_started: bool
    transport_guard_active: bool
    outbound_network_blocked: bool
    live_probe_execution_allowed: bool
    live_probe_execution_performed: bool
    probe_attempted: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    response_headers_received: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    decision: str
    reason: str
    timestamp_utc: str
    permission_switch: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_permission_switch(request: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from runtime_core.governance.governed_web.first_live_probe_permission_switch import (
            evaluate_first_live_probe_permission_switch,
        )

        return evaluate_first_live_probe_permission_switch(
            request,
            final_operator_confirmation_present=True,
            read_only_scope_confirmed=True,
            no_mutation_scope_confirmed=True,
        ).to_dict()

    except Exception as exc:
        normalized_query = _normalize_query(request.get("query"))
        return {
            "status": "permission_switch_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": normalized_query,
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "permission_ready_for_next_build": False,
            "permission_granted_this_build": False,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "response_body_fetched": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def execute_first_controlled_read_only_live_probe(
    request: Optional[Mapping[str, Any]] = None,
) -> FirstControlledReadOnlyLiveProbeExecutorResult:

    payload: Mapping[str, Any] = request or {}
    permission = _safe_permission_switch(payload)

    normalized_query = _normalize_query(
        permission.get("normalized_query") or payload.get("query") or ""
    )

    provider_id = str(
        permission.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )

    planned_method = str(permission.get("planned_method") or "GET")
    planned_url = permission.get("planned_url")

    safeguards = {
        "transport_guard_active": True,
        "outbound_network_blocked": True,
        "socket_creation_forbidden": True,
        "http_send_forbidden": True,
        "response_read_forbidden": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "fail_closed": True,
    }

    invalid_permission = any(
        bool(permission.get(key))
        for key in (
            "permission_granted_this_build",
            "real_transport_allowed_to_execute",
            "http_client_constructed",
            "socket_creation_allowed",
            "request_send_allowed",
            "probe_attempted",
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "response_body_fetched",
            "runtime_truth_mutated",
            "automatic_update_performed",
        )
    )

    if not normalized_query:
        status = "invalid_request"
        decision = "hold"
        reason = "Live probe executor requires a non-empty normalized query."
        lifecycle_started = False

    elif invalid_permission:
        status = "invalid_permission_state_rejected"
        decision = "reject"
        reason = "Permission switch reported forbidden execution state."
        lifecycle_started = False

    elif not permission.get("permission_ready_for_next_build"):
        status = "permission_not_ready"
        decision = "hold"
        reason = "Permission readiness has not been achieved."
        lifecycle_started = False

    else:
        status = "live_probe_executor_ready_transport_guard_active"
        decision = "hold"
        reason = "Live probe executor lifecycle initialized successfully with transport guard blocking outbound traffic."
        lifecycle_started = True

    return FirstControlledReadOnlyLiveProbeExecutorResult(
        version=LIVE_PROBE_EXECUTOR_VERSION,
        name=LIVE_PROBE_EXECUTOR_NAME,
        status=status,
        query=str(payload.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        permission_ready_for_next_build=bool(permission.get("permission_ready_for_next_build")),
        live_probe_executor_created=True,
        executor_lifecycle_started=lifecycle_started,
        transport_guard_active=True,
        outbound_network_blocked=True,
        live_probe_execution_allowed=False,
        live_probe_execution_performed=False,
        probe_attempted=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        response_headers_received=False,
        response_body_fetched=False,
        response_status_code=None,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        permission_switch=dict(permission),
        safeguards=safeguards,
    )


def build_dashboard_first_live_probe_executor_payload(query: str) -> Dict[str, Any]:
    result = execute_first_controlled_read_only_live_probe({"query": query})

    return {
        "dashboard_surface": "search_bar",
        "mode": "first_controlled_read_only_live_probe_executor",
        "version": LIVE_PROBE_EXECUTOR_VERSION,
        "live_probe_executor": result.to_dict(),
        "ui_notice": "First controlled live probe executor is initialized with outbound transport guard active. No request has been sent.",
    }


__all__ = [
    "LIVE_PROBE_EXECUTOR_VERSION",
    "LIVE_PROBE_EXECUTOR_NAME",
    "FirstControlledReadOnlyLiveProbeExecutorResult",
    "execute_first_controlled_read_only_live_probe",
    "build_dashboard_first_live_probe_executor_payload",
]
