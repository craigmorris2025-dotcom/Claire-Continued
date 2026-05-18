from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


PERMISSION_SWITCH_VERSION = "v18.30"
PERMISSION_SWITCH_NAME = "first_controlled_read_only_live_probe_permission_switch"


@dataclass(frozen=True)
class FirstLiveProbePermissionSwitchResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    permission_switch_created: bool
    permission_ready_for_next_build: bool
    permission_granted_this_build: bool
    real_transport_ready_for_future_probe: bool
    real_transport_allowed_to_execute: bool
    dry_activation_mode: bool
    final_operator_confirmation_present: bool
    read_only_scope_confirmed: bool
    no_mutation_scope_confirmed: bool
    network_probe_can_run_next_build: bool
    http_client_constructed: bool
    socket_creation_allowed: bool
    request_send_allowed: bool
    probe_attempted: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    decision: str
    reason: str
    timestamp_utc: str
    real_http_transport: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_real_transport_shell(request: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.real_http_transport_dry_activation_shell import (
            build_real_http_transport_dry_activation_shell,
        )

        return build_real_http_transport_dry_activation_shell(
            request,
            request_real_transport_candidate=True,
            explicit_operator_enablement_present=True,
            live_web_execution_enabled=True,
        ).to_dict()
    except Exception as exc:
        normalized_query = _normalize_query(request.get("query"))
        return {
            "status": "real_http_transport_shell_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": normalized_query,
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "real_transport_ready_for_future_probe": False,
            "real_transport_allowed_to_execute": False,
            "dry_activation_mode": True,
            "http_client_constructed": False,
            "socket_creation_allowed": False,
            "request_send_allowed": False,
            "probe_attempted": False,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "response_body_fetched": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def evaluate_first_live_probe_permission_switch(
    request: Optional[Mapping[str, Any]] = None,
    *,
    final_operator_confirmation_present: bool = False,
    read_only_scope_confirmed: bool = False,
    no_mutation_scope_confirmed: bool = False,
) -> FirstLiveProbePermissionSwitchResult:
    payload: Mapping[str, Any] = request or {}
    transport = _safe_real_transport_shell(payload)

    normalized_query = _normalize_query(
        transport.get("normalized_query") or payload.get("query") or ""
    )
    provider_id = str(
        transport.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )
    planned_method = str(transport.get("planned_method") or "GET")
    planned_url = transport.get("planned_url")

    safeguards = {
        "permission_switch_only": True,
        "permission_grant_deferred_to_next_build": True,
        "read_only_get_only": True,
        "no_http_client_invoked": True,
        "socket_creation_forbidden_this_build": True,
        "request_send_forbidden_this_build": True,
        "response_fetch_forbidden_this_build": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "final_operator_confirmation_required": True,
        "read_only_scope_required": True,
        "no_mutation_scope_required": True,
        "fail_closed": True,
    }

    invalid_transport = any(
        bool(transport.get(key))
        for key in (
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

    ready_flags = (
        final_operator_confirmation_present
        and read_only_scope_confirmed
        and no_mutation_scope_confirmed
    )

    if invalid_transport:
        status = "invalid_transport_rejected"
        decision = "reject"
        reason = "Real transport shell reported execution or network activity; permission switch rejected it."
        permission_ready = False
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Permission switch requires a normalized query and planned URL."
        permission_ready = False
    elif not transport.get("real_transport_ready_for_future_probe"):
        status = "transport_not_ready"
        decision = "hold"
        reason = "Real transport shell is not ready for future probe."
        permission_ready = False
    elif ready_flags:
        status = "permission_ready_for_next_build"
        decision = "hold"
        reason = "Final permission inputs are present; next build may perform the first controlled read-only probe."
        permission_ready = True
    else:
        status = "permission_inputs_incomplete"
        decision = "hold"
        reason = "Final operator confirmation, read-only scope, and no-mutation scope must all be present."
        permission_ready = False

    return FirstLiveProbePermissionSwitchResult(
        version=PERMISSION_SWITCH_VERSION,
        name=PERMISSION_SWITCH_NAME,
        status=status,
        query=str(payload.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        permission_switch_created=True,
        permission_ready_for_next_build=permission_ready,
        permission_granted_this_build=False,
        real_transport_ready_for_future_probe=bool(transport.get("real_transport_ready_for_future_probe")),
        real_transport_allowed_to_execute=False,
        dry_activation_mode=True,
        final_operator_confirmation_present=bool(final_operator_confirmation_present),
        read_only_scope_confirmed=bool(read_only_scope_confirmed),
        no_mutation_scope_confirmed=bool(no_mutation_scope_confirmed),
        network_probe_can_run_next_build=permission_ready,
        http_client_constructed=False,
        socket_creation_allowed=False,
        request_send_allowed=False,
        probe_attempted=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        response_body_fetched=False,
        response_status_code=None,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        real_http_transport=dict(transport),
        safeguards=safeguards,
    )


def build_dashboard_first_live_probe_permission_payload(query: str) -> Dict[str, Any]:
    result = evaluate_first_live_probe_permission_switch({"query": query})
    return {
        "dashboard_surface": "search_bar",
        "mode": "first_live_probe_permission_switch",
        "version": PERMISSION_SWITCH_VERSION,
        "permission_switch": result.to_dict(),
        "ui_notice": "First live probe permission switch is installed. No request has been sent.",
    }


__all__ = [
    "PERMISSION_SWITCH_VERSION",
    "PERMISSION_SWITCH_NAME",
    "FirstLiveProbePermissionSwitchResult",
    "evaluate_first_live_probe_permission_switch",
    "build_dashboard_first_live_probe_permission_payload",
]
