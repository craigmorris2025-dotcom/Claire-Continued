
# Claire Syntalion v18.67
# Real Controlled Provider Result Proof
#
# This module is the first controlled proof layer for real provider result
# execution. It can discover provider adapters, but it will not call a real
# provider unless explicit_real_provider_probe=True and all manual env flags are
# enabled. Tests use injected deterministic providers only.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple
import os


CONTRACT_VERSION = "v18.67.real_controlled_provider_result_proof"

GOOGLE_QUERY = "google"
GOOGLE_TITLE = "Google"
GOOGLE_URL = "https://www.google.com"

ENV_FLAGS = [
    "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE",
    "PLATFORM_ALLOW_CONTROLLED_METADATA_GET",
    "PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET",
    "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER",
]

CANDIDATE_PROVIDER_CALLABLES: List[Tuple[str, str]] = [
    ("claire.governed_web.real_controlled_search_provider_adapter", "run_real_controlled_search"),
    ("claire.governed_web.real_controlled_search_provider_adapter", "execute_real_controlled_search"),
    ("claire.governed_web.real_search_provider_adapter", "execute_real_search_provider"),
    ("claire.governed_web.real_search_provider_adapter", "search"),
    ("claire.governed_web.controlled_search_provider_adapter", "execute_controlled_search"),
    ("claire.governed_web.controlled_search_provider_adapter", "search"),
    ("claire.governed_web.live_search_provider_adapter", "execute_live_search"),
    ("claire.governed_web.live_search_provider_adapter", "search"),
    ("claire.governed_web.governed_live_search_orchestrator", "execute_governed_live_search"),
    ("claire.governed_web.governed_live_search_orchestrator", "run_governed_live_search"),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return str(value).strip() or default


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}


@dataclass(frozen=True)
class RealControlledProviderResultProofPolicy:
    explicit_real_provider_probe_required: bool = True
    all_env_flags_required: bool = True
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False
    bounded_result_count: int = 10
    injected_provider_allowed_for_tests: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_real_provider_probe_required": self.explicit_real_provider_probe_required,
            "all_env_flags_required": self.all_env_flags_required,
            "manual_enable_required": self.manual_enable_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
            "bounded_result_count": self.bounded_result_count,
            "injected_provider_allowed_for_tests": self.injected_provider_allowed_for_tests,
        }


def _governance(extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "uncontrolled_browsing": False,
        "fail_closed": True,
        "operator_review_required": True,
    }
    if extra:
        payload.update(dict(extra))
    return payload


def inspect_real_provider_env_flags() -> Dict[str, Any]:
    values = {name: os.getenv(name, "") for name in ENV_FLAGS}
    enabled = {name: _env_enabled(name) for name in ENV_FLAGS}
    all_enabled = all(enabled.values())
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "all_required_env_flags_enabled" if all_enabled else "env_flags_incomplete",
        "created_at": _utc_now(),
        "required_flags": list(ENV_FLAGS),
        "values": values,
        "enabled": enabled,
        "all_required_enabled": all_enabled,
        "manual_commands": [
            "set PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE=1",
            "set PLATFORM_ALLOW_CONTROLLED_METADATA_GET=1",
            "set PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET=1",
            "set PLATFORM_ALLOW_REAL_SEARCH_PROVIDER=1",
        ],
        "governance": _governance({"environment_inspection_only": True}),
    }


def discover_real_provider_adapter(
    candidates: Optional[Iterable[Tuple[str, str]]] = None,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    callable_ref: Optional[Callable[..., Any]] = None
    selected: Dict[str, Any] = {}

    for module_name, attr_name in list(candidates or CANDIDATE_PROVIDER_CALLABLES):
        row: Dict[str, Any] = {
            "module": module_name,
            "attribute": attr_name,
            "module_available": False,
            "attribute_available": False,
            "callable": False,
            "selected": False,
            "reason": "",
        }
        try:
            module = import_module(module_name)
            row["module_available"] = True
            attr = getattr(module, attr_name)
            row["attribute_available"] = True
            row["callable"] = callable(attr)
            if callable(attr) and callable_ref is None:
                callable_ref = attr
                row["selected"] = True
                selected = {
                    "module": module_name,
                    "attribute": attr_name,
                    "name": module_name + ":" + attr_name,
                }
        except Exception as exc:
            row["reason"] = type(exc).__name__
        rows.append(row)

    available = callable_ref is not None
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "provider_adapter_discovered" if available else "provider_adapter_not_discovered",
        "created_at": _utc_now(),
        "available": available,
        "selected": selected,
        "candidates": rows,
        "callable_ref": callable_ref,
        "governance": _governance({"adapter_discovery_only": True}),
    }


def deterministic_google_provider_probe(**kwargs: Any) -> Dict[str, Any]:
    provider = _string(kwargs.get("provider"), "deterministic-v18-67-provider")
    query = _string(kwargs.get("query"), GOOGLE_QUERY)
    max_results = int(kwargs.get("max_results") or 3)
    results = [
        {
            "title": GOOGLE_TITLE,
            "url": GOOGLE_URL,
            "snippet": "Deterministic controlled provider proof result for Google.",
            "provider": provider,
            "trust_score": 1.0,
            "result_id": "v18-67-deterministic-google-result",
            "evidence_id": "v18-67-deterministic-google-evidence",
        }
    ]
    return {
        "provider_status": "ok",
        "query": query,
        "provider": provider,
        "results": results[:max(1, max_results)],
        "real_network": False,
        "deterministic": True,
    }


def _call_provider(provider_callable: Callable[..., Any], *, query: str, provider: str, max_results: int) -> Any:
    # Providers across earlier build layers may accept slightly different
    # signatures. Try the safest keyword form first, then fall back.
    try:
        return provider_callable(
            query=query,
            provider=provider,
            max_results=max_results,
            manual_enable_confirmed=True,
            request_context={
                "source": "v18.67.real_controlled_provider_result_proof",
                "bounded": True,
                "review_required": True,
            },
        )
    except TypeError:
        try:
            return provider_callable(query=query, max_results=max_results)
        except TypeError:
            try:
                return provider_callable(query)
            except TypeError:
                return provider_callable()


def _extract_result_list(provider_response: Any) -> List[Mapping[str, Any]]:
    if provider_response is None:
        return []
    if isinstance(provider_response, list):
        return [item for item in provider_response if isinstance(item, Mapping)]
    if isinstance(provider_response, Mapping):
        for key in ("results", "items", "search_results", "provider_results", "result_cards"):
            value = provider_response.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)]
        if provider_response.get("url") or provider_response.get("link") or provider_response.get("href"):
            return [provider_response]
    return []


def normalize_provider_response_to_dashboard_endpoint(
    provider_response: Any,
    *,
    query: str = GOOGLE_QUERY,
    provider: str = "real-controlled-provider",
    session_id: str = "v18-67-real-controlled-provider-session",
    max_results: int = 10,
) -> Dict[str, Any]:
    try:
        from .dashboard_search_endpoint_result_contract import execute_dashboard_search_endpoint_request
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "dashboard_search_endpoint_contract_unavailable",
            "created_at": _utc_now(),
            "endpoint_response": {},
            "provider_response": provider_response if isinstance(provider_response, Mapping) else {"raw_type": type(provider_response).__name__},
            "error_type": type(exc).__name__,
            "visible_result_count": 0,
            "first_result_title": "",
            "first_result_url": "",
            "governance": _governance(),
        }

    raw_results = _extract_result_list(provider_response)
    bounded_results = raw_results[:max(1, int(max_results or 10))]

    def executor(**kwargs: Any) -> Dict[str, Any]:
        return {
            "provider_status": "ok",
            "query": query,
            "provider": provider,
            "results": bounded_results,
        }

    endpoint_response = execute_dashboard_search_endpoint_request(
        query=query,
        session_id=session_id,
        provider=provider,
        executor=executor,
        manual_enable_confirmed=True,
        require_provider_env=False,
        require_limited_body_env=False,
        max_results=max_results,
        request_context={
            "source": "v18.67.normalize_provider_response_to_dashboard_endpoint",
            "bounded_result_count": len(bounded_results),
        },
        request_id="v18-67-provider-response-normalization",
    )

    cards = endpoint_response.get("result_cards") if isinstance(endpoint_response, Mapping) else []
    first = cards[0] if isinstance(cards, list) and cards and isinstance(cards[0], Mapping) else {}

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "endpoint_response_ready" if endpoint_response.get("endpoint_status") == "endpoint_response_ready" else "endpoint_response_not_ready",
        "reason": endpoint_response.get("reason", "") if isinstance(endpoint_response, Mapping) else "invalid_endpoint_response",
        "created_at": _utc_now(),
        "query": query,
        "provider": provider,
        "raw_result_count": len(raw_results),
        "bounded_result_count": len(bounded_results),
        "provider_response": provider_response if isinstance(provider_response, Mapping) else {"raw_type": type(provider_response).__name__},
        "endpoint_response": endpoint_response,
        "visible_result_count": int(endpoint_response.get("visible_result_count") or 0) if isinstance(endpoint_response, Mapping) else 0,
        "first_result_title": first.get("title", ""),
        "first_result_url": first.get("url", ""),
        "governance": _governance({"provider_response_normalized": True}),
    }


def run_controlled_provider_result_proof(
    *,
    query: str = GOOGLE_QUERY,
    explicit_real_provider_probe: bool = False,
    provider_probe: Optional[Callable[..., Any]] = None,
    provider: str = "real-controlled-provider",
    max_results: int = 3,
) -> Dict[str, Any]:
    policy = RealControlledProviderResultProofPolicy(bounded_result_count=max(1, int(max_results or 3)))
    env = inspect_real_provider_env_flags()
    discovery = discover_real_provider_adapter()

    if provider_probe is not None:
        selected_probe = provider_probe
        probe_source = "injected_provider_probe"
        probe_allowed = True
    elif explicit_real_provider_probe:
        selected_probe = discovery.get("callable_ref")
        probe_source = "discovered_real_provider_adapter"
        probe_allowed = bool(env.get("all_required_enabled") and selected_probe is not None)
    else:
        selected_probe = None
        probe_source = "not_requested"
        probe_allowed = False

    if not explicit_real_provider_probe and provider_probe is None:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_real_provider_probe_required",
            "created_at": _utc_now(),
            "query": query,
            "environment": env,
            "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"},
            "probe_attempted": False,
            "probe_source": probe_source,
            "provider_response": {},
            "endpoint_result": {},
            "visible_result_ready": False,
            "policy": policy.to_dict(),
            "governance": _governance({"real_provider_probe": False}),
        }

    if explicit_real_provider_probe and not env.get("all_required_enabled") and provider_probe is None:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "required_env_flags_incomplete",
            "created_at": _utc_now(),
            "query": query,
            "environment": env,
            "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"},
            "probe_attempted": False,
            "probe_source": probe_source,
            "provider_response": {},
            "endpoint_result": {},
            "visible_result_ready": False,
            "policy": policy.to_dict(),
            "governance": _governance({"real_provider_probe": False}),
        }

    if not probe_allowed or selected_probe is None:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "provider_probe_unavailable",
            "created_at": _utc_now(),
            "query": query,
            "environment": env,
            "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"},
            "probe_attempted": False,
            "probe_source": probe_source,
            "provider_response": {},
            "endpoint_result": {},
            "visible_result_ready": False,
            "policy": policy.to_dict(),
            "governance": _governance({"real_provider_probe": bool(explicit_real_provider_probe)}),
        }

    try:
        provider_response = _call_provider(
            selected_probe,
            query=query,
            provider=provider,
            max_results=max_results,
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": "provider_probe_exception",
            "created_at": _utc_now(),
            "query": query,
            "environment": env,
            "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"},
            "probe_attempted": True,
            "probe_source": probe_source,
            "provider_response": {},
            "endpoint_result": {},
            "error_type": type(exc).__name__,
            "visible_result_ready": False,
            "policy": policy.to_dict(),
            "governance": _governance({"real_provider_probe": bool(explicit_real_provider_probe)}),
        }

    endpoint_result = normalize_provider_response_to_dashboard_endpoint(
        provider_response,
        query=query,
        provider=provider,
        max_results=max_results,
    )

    first_title = endpoint_result.get("first_result_title", "")
    first_url = endpoint_result.get("first_result_url", "")
    visible_ready = (
        endpoint_result.get("status") == "endpoint_response_ready"
        and int(endpoint_result.get("visible_result_count") or 0) > 0
    )
    google_ready = (
        _string(query).lower() == GOOGLE_QUERY
        and first_title == GOOGLE_TITLE
        and first_url == GOOGLE_URL
    )

    if visible_ready and google_ready:
        status = "google_result_ready"
    elif visible_ready:
        status = "provider_result_ready"
    else:
        status = "provider_result_not_ready"

    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "reason": "" if visible_ready else "provider_results_not_dashboard_ready",
        "created_at": _utc_now(),
        "query": query,
        "environment": env,
        "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"},
        "probe_attempted": True,
        "probe_source": probe_source,
        "provider_response": provider_response if isinstance(provider_response, Mapping) else {"raw_type": type(provider_response).__name__},
        "endpoint_result": endpoint_result,
        "visible_result_ready": visible_ready,
        "google_result_ready": google_ready,
        "first_result_title": first_title,
        "first_result_url": first_url,
        "visible_result_count": endpoint_result.get("visible_result_count", 0),
        "policy": policy.to_dict(),
        "governance": _governance({
            "real_provider_probe": bool(explicit_real_provider_probe and provider_probe is None),
            "injected_provider_probe": provider_probe is not None,
        }),
    }


def run_deterministic_controlled_provider_google_proof() -> Dict[str, Any]:
    return run_controlled_provider_result_proof(
        query=GOOGLE_QUERY,
        explicit_real_provider_probe=False,
        provider_probe=deterministic_google_provider_probe,
        provider="deterministic-v18-67-provider",
        max_results=3,
    )


def run_operator_real_provider_probe_if_enabled() -> Dict[str, Any]:
    return run_controlled_provider_result_proof(
        query=GOOGLE_QUERY,
        explicit_real_provider_probe=True,
        provider_probe=None,
        provider="operator-controlled-real-provider",
        max_results=3,
    )


__all__ = [
    "CONTRACT_VERSION",
    "CANDIDATE_PROVIDER_CALLABLES",
    "ENV_FLAGS",
    "GOOGLE_QUERY",
    "GOOGLE_TITLE",
    "GOOGLE_URL",
    "RealControlledProviderResultProofPolicy",
    "deterministic_google_provider_probe",
    "discover_real_provider_adapter",
    "inspect_real_provider_env_flags",
    "normalize_provider_response_to_dashboard_endpoint",
    "run_controlled_provider_result_proof",
    "run_deterministic_controlled_provider_google_proof",
    "run_operator_real_provider_probe_if_enabled",
]
