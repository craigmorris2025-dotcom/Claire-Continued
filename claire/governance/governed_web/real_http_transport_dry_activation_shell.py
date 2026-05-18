from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


REAL_HTTP_TRANSPORT_VERSION = "v18.29"
REAL_HTTP_TRANSPORT_NAME = "real_http_transport_dry_activation_shell"


@dataclass(frozen=True)
class RealHttpTransportDryActivationResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    transport_contract_created: bool
    real_transport_candidate_selected: bool
    dry_activation_mode: bool
    real_transport_ready_for_future_probe: bool
    real_transport_allowed_to_execute: bool
    null_transport_fallback_active: bool
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
    transport_selection: Dict[str, Any]
    transport_contract: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_transport_selection(
    request: Mapping[str, Any],
    request_real_transport_candidate: bool,
    explicit_operator_enablement_present: bool,
    live_web_execution_enabled: bool,
) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.read_only_transport_selection_gate import (
            evaluate_read_only_transport_selection_gate,
        )

        return evaluate_read_only_transport_selection_gate(
            request,
            request_real_transport_candidate=request_real_transport_candidate,
            explicit_operator_enablement_present=explicit_operator_enablement_present,
            live_web_execution_enabled=live_web_execution_enabled,
        ).to_dict()
    except Exception as exc:
        normalized_query = _normalize_query(request.get("query"))
        return {
            "status": "transport_selection_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": normalized_query,
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "selected_transport": "none",
            "real_transport_candidate_selected": False,
            "real_transport_allowed_to_execute": False,
            "null_transport_fallback_active": True,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "response_body_fetched": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def build_real_http_transport_dry_activation_shell(
    request: Optional[Mapping[str, Any]] = None,
    *,
    request_real_transport_candidate: bool = True,
    explicit_operator_enablement_present: bool = True,
    live_web_execution_enabled: bool = True,
) -> RealHttpTransportDryActivationResult:
    payload: Mapping[str, Any] = request or {}

    selection = _safe_transport_selection(
        payload,
        request_real_transport_candidate=request_real_transport_candidate,
        explicit_operator_enablement_present=explicit_operator_enablement_present,
        live_web_execution_enabled=live_web_execution_enabled,
    )

    normalized_query = _normalize_query(
        selection.get("normalized_query") or payload.get("query") or ""
    )
    provider_id = str(
        selection.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )
    planned_method = str(selection.get("planned_method") or "GET")
    planned_url = selection.get("planned_url")
    real_candidate_selected = bool(selection.get("real_transport_candidate_selected"))

    transport_contract = {
        "transport_type": "http_read_only_get",
        "method": planned_method,
        "url": planned_url,
        "timeout_seconds": 10,
        "max_response_bytes": 500000,
        "redirect_policy": "limited",
        "write_methods_forbidden": ["POST", "PUT", "PATCH", "DELETE"],
        "body_upload_forbidden": True,
        "cookies_disabled_by_default": True,
        "runtime_truth_write_forbidden": True,
        "automatic_update_forbidden": True,
    }

    safeguards = {
        "dry_activation_only": True,
        "http_client_not_constructed": True,
        "socket_creation_forbidden": True,
        "request_send_forbidden": True,
        "response_fetch_forbidden": True,
        "real_transport_execute_forbidden_this_build": True,
        "null_transport_fallback_required": True,
        "read_only_get_only": True,
        "fail_closed": True,
    }

    invalid_selection = any(
        bool(selection.get(key))
        for key in (
            "real_transport_allowed_to_execute",
            "probe_attempted",
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "response_body_fetched",
            "runtime_truth_mutated",
            "automatic_update_performed",
        )
    )

    if invalid_selection:
        status = "invalid_transport_selection_rejected"
        decision = "reject"
        reason = "Transport selection reported execution or network activity; dry activation rejected it."
        contract_created = False
        ready_future = False
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Real HTTP transport dry activation requires a normalized query and planned URL."
        contract_created = False
        ready_future = False
    elif real_candidate_selected:
        status = "real_http_transport_contract_ready_dry_activation"
        decision = "hold"
        reason = "Real HTTP transport contract is ready for future controlled probe; execution remains forbidden."
        contract_created = True
        ready_future = True
    else:
        status = "real_http_transport_not_selected"
        decision = "hold"
        reason = "Real HTTP transport candidate was not selected; null transport remains active."
        contract_created = True
        ready_future = False

    return RealHttpTransportDryActivationResult(
        version=REAL_HTTP_TRANSPORT_VERSION,
        name=REAL_HTTP_TRANSPORT_NAME,
        status=status,
        query=str(payload.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        transport_contract_created=contract_created,
        real_transport_candidate_selected=real_candidate_selected,
        dry_activation_mode=True,
        real_transport_ready_for_future_probe=ready_future,
        real_transport_allowed_to_execute=False,
        null_transport_fallback_active=True,
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
        transport_selection=dict(selection),
        transport_contract=transport_contract,
        safeguards=safeguards,
    )


def build_dashboard_real_http_transport_shell_payload(query: str) -> Dict[str, Any]:
    result = build_real_http_transport_dry_activation_shell({"query": query})
    return {
        "dashboard_surface": "search_bar",
        "mode": "real_http_transport_dry_activation_shell",
        "version": REAL_HTTP_TRANSPORT_VERSION,
        "real_http_transport": result.to_dict(),
        "ui_notice": "Real HTTP transport contract is available in dry activation mode. No request has been sent.",
    }


__all__ = [
    "REAL_HTTP_TRANSPORT_VERSION",
    "REAL_HTTP_TRANSPORT_NAME",
    "RealHttpTransportDryActivationResult",
    "build_real_http_transport_dry_activation_shell",
    "build_dashboard_real_http_transport_shell_payload",
]
