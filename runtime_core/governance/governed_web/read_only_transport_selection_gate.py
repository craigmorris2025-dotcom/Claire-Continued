from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


TRANSPORT_SELECTION_VERSION = "v18.28"
TRANSPORT_SELECTION_NAME = "read_only_transport_selection_gate"


@dataclass(frozen=True)
class ReadOnlyTransportSelectionGateResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    selected_transport: str
    real_transport_candidate_selected: bool
    real_transport_allowed_to_execute: bool
    null_transport_fallback_active: bool
    selection_gate_created: bool
    executor_lifecycle_simulated: bool
    probe_attempted: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    decision: str
    reason: str
    timestamp_utc: str
    null_transport_result: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_null_transport(request: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from runtime_core.governance.governed_web.read_only_probe_executor_null_transport import (
            execute_read_only_probe_with_null_transport,
        )

        return execute_read_only_probe_with_null_transport(request).to_dict()
    except Exception as exc:
        normalized_query = _normalize_query(request.get("query"))
        return {
            "status": "null_transport_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": normalized_query,
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "executor_lifecycle_simulated": False,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
            "response_status_code": None,
        }


def evaluate_read_only_transport_selection_gate(
    request: Optional[Mapping[str, Any]] = None,
    *,
    request_real_transport_candidate: bool = False,
    explicit_operator_enablement_present: bool = False,
    live_web_execution_enabled: bool = False,
) -> ReadOnlyTransportSelectionGateResult:
    payload: Mapping[str, Any] = request or {}
    null_result = _safe_null_transport(payload)

    normalized_query = _normalize_query(
        null_result.get("normalized_query") or payload.get("query") or ""
    )
    provider_id = str(
        null_result.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )
    planned_method = str(null_result.get("planned_method") or "GET")
    planned_url = null_result.get("planned_url")

    safeguards = {
        "selection_gate_only": True,
        "real_transport_execute_forbidden_this_build": True,
        "null_transport_default": True,
        "real_transport_candidate_review_only": True,
        "no_http_client_invoked": True,
        "planned_url_is_not_fetched": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "operator_enablement_required_for_candidate": True,
        "live_web_enablement_required_for_candidate": True,
        "fail_closed": True,
    }

    invalid_null_result = any(
        bool(null_result.get(key))
        for key in (
            "probe_attempted",
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "runtime_truth_mutated",
            "automatic_update_performed",
            "response_body_fetched",
        )
    )

    if invalid_null_result:
        status = "invalid_null_transport_rejected"
        selected_transport = "none"
        real_candidate = False
        null_fallback = False
        decision = "reject"
        reason = "Null transport result reported execution or network activity; selection gate rejected it."
        simulated = False
    elif not normalized_query:
        status = "invalid_request"
        selected_transport = "none"
        real_candidate = False
        null_fallback = False
        decision = "hold"
        reason = "Transport selection requires a non-empty normalized query."
        simulated = False
    elif request_real_transport_candidate and explicit_operator_enablement_present and live_web_execution_enabled:
        status = "real_transport_candidate_selected_review_only"
        selected_transport = "real_transport_candidate"
        real_candidate = True
        null_fallback = True
        decision = "hold"
        reason = "Real transport candidate selected for review only; execution remains forbidden in v18.28."
        simulated = bool(null_result.get("executor_lifecycle_simulated"))
    else:
        status = "null_transport_selected_fail_closed"
        selected_transport = "null_transport"
        real_candidate = False
        null_fallback = True
        decision = "hold"
        reason = "Null transport remains selected; real transport requires future explicit execution build."
        simulated = bool(null_result.get("executor_lifecycle_simulated"))

    return ReadOnlyTransportSelectionGateResult(
        version=TRANSPORT_SELECTION_VERSION,
        name=TRANSPORT_SELECTION_NAME,
        status=status,
        query=str(payload.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        selected_transport=selected_transport,
        real_transport_candidate_selected=real_candidate,
        real_transport_allowed_to_execute=False,
        null_transport_fallback_active=null_fallback,
        selection_gate_created=True,
        executor_lifecycle_simulated=simulated,
        probe_attempted=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        response_body_fetched=False,
        response_status_code=None,
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        null_transport_result=dict(null_result),
        safeguards=safeguards,
    )


def build_dashboard_transport_selection_payload(query: str) -> Dict[str, Any]:
    result = evaluate_read_only_transport_selection_gate({"query": query})
    return {
        "dashboard_surface": "search_bar",
        "mode": "read_only_transport_selection_gate",
        "version": TRANSPORT_SELECTION_VERSION,
        "transport_selection": result.to_dict(),
        "ui_notice": "Read-only transport selection gate is active. Real transport is still review-only.",
    }


__all__ = [
    "TRANSPORT_SELECTION_VERSION",
    "TRANSPORT_SELECTION_NAME",
    "ReadOnlyTransportSelectionGateResult",
    "evaluate_read_only_transport_selection_gate",
    "build_dashboard_transport_selection_payload",
]
