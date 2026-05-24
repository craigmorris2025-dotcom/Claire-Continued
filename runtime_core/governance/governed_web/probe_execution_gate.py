from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


EXECUTION_GATE_VERSION = "v18.25"
EXECUTION_GATE_NAME = "controlled_probe_execution_gate"


@dataclass(frozen=True)
class ControlledProbeExecutionGateResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    gate_created: bool
    gate_locked: bool
    execution_gate_passed: bool
    execution_permitted: bool
    operator_review_required: bool
    explicit_operator_enablement_present: bool
    live_web_execution_enabled: bool
    ai_agent_execution_enabled: bool
    probe_executor_enabled: bool
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
    network_probe_shell: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_probe_shell(
    request: Mapping[str, Any],
    live_web_execution_enabled: bool,
    ai_agent_execution_enabled: bool,
    operator_approved_planning: bool,
    probe_executor_enabled: bool,
) -> Dict[str, Any]:
    try:
        from runtime_core.governance.governed_web.network_probe_adapter_shell import (
            build_controlled_network_probe_adapter_shell,
        )

        return build_controlled_network_probe_adapter_shell(
            request,
            live_web_execution_enabled=live_web_execution_enabled,
            ai_agent_execution_enabled=ai_agent_execution_enabled,
            operator_approved_planning=operator_approved_planning,
            probe_executor_enabled=probe_executor_enabled,
        ).to_dict()
    except Exception as exc:
        return {
            "status": "network_probe_shell_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": _normalize_query(request.get("query")),
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "probe_attempted": False,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
            "response_status_code": None,
        }


def evaluate_controlled_probe_execution_gate(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
    operator_approved_planning: bool = False,
    explicit_operator_enablement_present: bool = False,
    probe_executor_enabled: bool = False,
) -> ControlledProbeExecutionGateResult:
    payload: Mapping[str, Any] = request or {}
    shell = _safe_probe_shell(
        payload,
        live_web_execution_enabled=live_web_execution_enabled,
        ai_agent_execution_enabled=ai_agent_execution_enabled,
        operator_approved_planning=operator_approved_planning,
        probe_executor_enabled=probe_executor_enabled,
    )

    normalized_query = _normalize_query(
        shell.get("normalized_query") or payload.get("query") or payload.get("raw_input")
    )
    provider_id = str(
        shell.get("provider_id") or payload.get("provider_id") or "governed-web-search-provider-stub"
    )
    planned_method = str(shell.get("planned_method") or "GET")
    planned_url = shell.get("planned_url")

    safeguards = {
        "gate_only": True,
        "gate_locked_this_build": True,
        "no_http_client_invoked": True,
        "planned_url_is_not_fetched": True,
        "approval_is_not_execution": True,
        "explicit_operator_enablement_required": True,
        "live_web_execution_flag_required": True,
        "probe_executor_flag_required_in_future": True,
        "ai_agent_execution_disallowed": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "requires_operator_review": True,
        "fail_closed": True,
    }

    invalid_shell = any(
        bool(shell.get(key))
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

    if invalid_shell:
        status = "invalid_shell_rejected"
        decision = "reject"
        reason = "Network probe shell reported execution or network activity; execution gate rejected it."
        gate_created = False
    elif ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution remains disabled for controlled probe execution."
        gate_created = bool(normalized_query and planned_url)
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Execution gate requires a normalized query and planned URL."
        gate_created = False
    elif live_web_execution_enabled and explicit_operator_enablement_present and probe_executor_enabled:
        status = "gate_ready_but_locked"
        decision = "hold"
        reason = "All future execution inputs are present, but v18.25 keeps the execution gate locked."
        gate_created = True
    elif live_web_execution_enabled and explicit_operator_enablement_present:
        status = "gate_ready_executor_disabled"
        decision = "hold"
        reason = "Execution gate is ready for future probe adapter, but executor remains disabled."
        gate_created = True
    else:
        status = "gate_ready_fail_closed"
        decision = "hold"
        reason = "Controlled probe execution gate is ready for review; execution remains locked."
        gate_created = True

    return ControlledProbeExecutionGateResult(
        version=EXECUTION_GATE_VERSION,
        name=EXECUTION_GATE_NAME,
        status=status,
        query=str(payload.get("query") or shell.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        gate_created=gate_created,
        gate_locked=True,
        execution_gate_passed=False,
        execution_permitted=False,
        operator_review_required=True,
        explicit_operator_enablement_present=bool(explicit_operator_enablement_present),
        live_web_execution_enabled=bool(live_web_execution_enabled),
        ai_agent_execution_enabled=bool(ai_agent_execution_enabled),
        probe_executor_enabled=False,
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
        network_probe_shell=dict(shell),
        safeguards=safeguards,
    )


def build_dashboard_probe_execution_gate_payload(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    gate = evaluate_controlled_probe_execution_gate(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "controlled_probe_execution_gate",
        "version": EXECUTION_GATE_VERSION,
        "probe_execution_gate": gate.to_dict(),
        "ui_notice": "Controlled probe execution gate is ready and locked. No network request has been made.",
    }


__all__ = [
    "EXECUTION_GATE_VERSION",
    "EXECUTION_GATE_NAME",
    "ControlledProbeExecutionGateResult",
    "evaluate_controlled_probe_execution_gate",
    "build_dashboard_probe_execution_gate_payload",
]
