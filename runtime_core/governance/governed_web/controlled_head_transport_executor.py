from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
import os
import urllib.request
import urllib.error


HEAD_EXECUTOR_VERSION = "v18.33"
HEAD_EXECUTOR_NAME = "controlled_head_transport_executor_manual_enable"
ENABLE_ENV_VAR = "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE"


@dataclass(frozen=True)
class ControlledHeadTransportExecutorResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    manual_enable_required: bool
    manual_enable_present: bool
    head_request_allowed: bool
    head_request_attempted: bool
    head_request_completed: bool
    response_headers_received: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    response_header_count: int
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    decision: str
    reason: str
    timestamp_utc: str
    safeguards: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _enabled() -> bool:
    return os.getenv(ENABLE_ENV_VAR, "").strip() == "1"


def execute_controlled_head_transport(
    request: Optional[Mapping[str, Any]] = None,
) -> ControlledHeadTransportExecutorResult:
    payload: Mapping[str, Any] = request or {}
    normalized_query = _normalize_query(payload.get("query"))
    planned_url = str(payload.get("url") or payload.get("planned_url") or "https://example.com")
    provider_id = str(payload.get("provider_id") or "governed-web-search-provider-stub")

    safeguards = {
        "manual_enable_required": True,
        "enable_env_var": ENABLE_ENV_VAR,
        "head_only": True,
        "get_body_forbidden": True,
        "response_body_fetch_forbidden": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "default_pytest_safe_mode": True,
        "fail_closed": True,
    }

    manual_enable = _enabled()

    if not normalized_query:
        return ControlledHeadTransportExecutorResult(
            version=HEAD_EXECUTOR_VERSION,
            name=HEAD_EXECUTOR_NAME,
            status="invalid_request",
            query=str(payload.get("query") or ""),
            normalized_query="",
            provider_id=provider_id,
            planned_method="HEAD",
            planned_url=planned_url,
            manual_enable_required=True,
            manual_enable_present=manual_enable,
            head_request_allowed=False,
            head_request_attempted=False,
            head_request_completed=False,
            response_headers_received=False,
            response_body_fetched=False,
            response_status_code=None,
            response_header_count=0,
            execution_performed=False,
            network_call_performed=False,
            external_request_performed=False,
            runtime_truth_mutated=False,
            automatic_update_performed=False,
            decision="hold",
            reason="Controlled HEAD executor requires a non-empty query.",
            timestamp_utc=_utc_now(),
            safeguards=safeguards,
        )

    if not manual_enable:
        return ControlledHeadTransportExecutorResult(
            version=HEAD_EXECUTOR_VERSION,
            name=HEAD_EXECUTOR_NAME,
            status="manual_enable_required_no_network",
            query=str(payload.get("query") or ""),
            normalized_query=normalized_query,
            provider_id=provider_id,
            planned_method="HEAD",
            planned_url=planned_url,
            manual_enable_required=True,
            manual_enable_present=False,
            head_request_allowed=False,
            head_request_attempted=False,
            head_request_completed=False,
            response_headers_received=False,
            response_body_fetched=False,
            response_status_code=None,
            response_header_count=0,
            execution_performed=False,
            network_call_performed=False,
            external_request_performed=False,
            runtime_truth_mutated=False,
            automatic_update_performed=False,
            decision="hold",
            reason="Manual enable flag is absent; no outbound network call was made.",
            timestamp_utc=_utc_now(),
            safeguards=safeguards,
        )

    req = urllib.request.Request(
        planned_url,
        method="HEAD",
        headers={
            "User-Agent": "Claire-Syntalion-Governed-HEAD-Probe/18.33",
            "Accept": "*/*",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = int(getattr(response, "status", 0) or response.getcode() or 0)
            header_count = len(dict(response.headers.items()))

        return ControlledHeadTransportExecutorResult(
            version=HEAD_EXECUTOR_VERSION,
            name=HEAD_EXECUTOR_NAME,
            status="head_request_completed_headers_only",
            query=str(payload.get("query") or ""),
            normalized_query=normalized_query,
            provider_id=provider_id,
            planned_method="HEAD",
            planned_url=planned_url,
            manual_enable_required=True,
            manual_enable_present=True,
            head_request_allowed=True,
            head_request_attempted=True,
            head_request_completed=True,
            response_headers_received=True,
            response_body_fetched=False,
            response_status_code=status_code,
            response_header_count=header_count,
            execution_performed=True,
            network_call_performed=True,
            external_request_performed=True,
            runtime_truth_mutated=False,
            automatic_update_performed=False,
            decision="record_only",
            reason="Controlled HEAD request completed. Headers only; response body was not fetched.",
            timestamp_utc=_utc_now(),
            safeguards=safeguards,
        )

    except Exception as exc:
        return ControlledHeadTransportExecutorResult(
            version=HEAD_EXECUTOR_VERSION,
            name=HEAD_EXECUTOR_NAME,
            status="head_request_failed_fail_closed",
            query=str(payload.get("query") or ""),
            normalized_query=normalized_query,
            provider_id=provider_id,
            planned_method="HEAD",
            planned_url=planned_url,
            manual_enable_required=True,
            manual_enable_present=True,
            head_request_allowed=True,
            head_request_attempted=True,
            head_request_completed=False,
            response_headers_received=False,
            response_body_fetched=False,
            response_status_code=None,
            response_header_count=0,
            execution_performed=True,
            network_call_performed=True,
            external_request_performed=True,
            runtime_truth_mutated=False,
            automatic_update_performed=False,
            decision="fail_closed",
            reason="Controlled HEAD request failed; fail-closed result recorded.",
            timestamp_utc=_utc_now(),
            safeguards=safeguards,
            error=str(exc),
        )


def build_dashboard_controlled_head_executor_payload(query: str) -> Dict[str, Any]:
    result = execute_controlled_head_transport({"query": query})
    return {
        "dashboard_surface": "search_bar",
        "mode": "controlled_head_transport_executor_manual_enable",
        "version": HEAD_EXECUTOR_VERSION,
        "head_transport_executor": result.to_dict(),
        "ui_notice": "Controlled HEAD executor installed. Real network call requires PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE=1.",
    }


__all__ = [
    "HEAD_EXECUTOR_VERSION",
    "HEAD_EXECUTOR_NAME",
    "ENABLE_ENV_VAR",
    "ControlledHeadTransportExecutorResult",
    "execute_controlled_head_transport",
    "build_dashboard_controlled_head_executor_payload",
]
