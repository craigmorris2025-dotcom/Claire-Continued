from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional

CONTRACT_VERSION = "v18.68.1.real_provider_operator_probe_route_smoke_assertion_repair"
STATUS_PATH = "/api/dashboard/search/provider/status"
PROBE_PATH = "/api/dashboard/search/provider/probe"
GOOGLE_URL = "https://www.google.com"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _s(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


@dataclass(frozen=True)
class RealProviderOperatorProbeRoutePolicy:
    explicit_real_provider_probe_required: bool = True
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_real_provider_probe_required": self.explicit_real_provider_probe_required,
            "manual_enable_required": self.manual_enable_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
            "max_results": self.max_results,
        }


def _gov(extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    data = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "uncontrolled_browsing": False,
        "fail_closed": True,
        "operator_review_required": True,
    }
    if extra:
        data.update(dict(extra))
    return data


def build_operator_provider_probe_status() -> Dict[str, Any]:
    try:
        from .real_controlled_provider_result_proof import (
            discover_real_provider_adapter,
            inspect_real_provider_env_flags,
        )
        env = inspect_real_provider_env_flags()
        discovery = discover_real_provider_adapter()
        env_ready = bool(env.get("all_required_enabled"))
        adapter_ready = bool(discovery.get("available"))
    except Exception as exc:
        env = {}
        discovery = {"reason": type(exc).__name__}
        env_ready = False
        adapter_ready = False

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_probe_ready" if env_ready and adapter_ready else "operator_probe_not_ready",
        "reason": "" if env_ready and adapter_ready else "env_flags_or_adapter_incomplete",
        "created_at": _now(),
        "env": env,
        "discovery": {k: v for k, v in discovery.items() if k != "callable_ref"} if isinstance(discovery, dict) else {},
        "env_ready": env_ready,
        "adapter_ready": adapter_ready,
        "operator_probe_ready": env_ready and adapter_ready,
        "status_path": STATUS_PATH,
        "probe_path": PROBE_PATH,
        "policy": RealProviderOperatorProbeRoutePolicy().to_dict(),
        "governance": _gov({"status_only": True}),
    }


def build_operator_probe_request_payload(
    *,
    query: str = "google",
    explicit_real_provider_probe: bool = False,
    provider: str = "operator-controlled-real-provider",
    max_results: int = 3,
) -> Dict[str, Any]:
    return {
        "query": _s(query, "google"),
        "explicit_real_provider_probe": bool(explicit_real_provider_probe),
        "provider": _s(provider, "operator-controlled-real-provider"),
        "max_results": max(1, int(max_results or 3)),
    }


def execute_operator_provider_probe_request(
    payload: Mapping[str, Any],
    *,
    provider_probe: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    policy = RealProviderOperatorProbeRoutePolicy(max_results=max(1, int(payload.get("max_results") or 3)))

    if not bool(payload.get("explicit_real_provider_probe")):
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_real_provider_probe_required",
            "created_at": _now(),
            "query": _s(payload.get("query"), "google"),
            "probe_attempted": False,
            "result_cards": [],
            "visible_result_count": 0,
            "first_result_title": "",
            "first_result_url": "",
            "policy": policy.to_dict(),
            "governance": _gov({"real_provider_probe": False}),
        }

    try:
        from .real_controlled_provider_result_proof import run_controlled_provider_result_proof
        provider_result = run_controlled_provider_result_proof(
            query=_s(payload.get("query"), "google"),
            explicit_real_provider_probe=True,
            provider_probe=provider_probe,
            provider=_s(payload.get("provider"), "operator-controlled-real-provider"),
            max_results=max(1, int(payload.get("max_results") or 3)),
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "real_controlled_provider_result_proof_unavailable",
            "created_at": _now(),
            "query": _s(payload.get("query"), "google"),
            "probe_attempted": False,
            "error_type": type(exc).__name__,
            "result_cards": [],
            "visible_result_count": 0,
            "first_result_title": "",
            "first_result_url": "",
            "policy": policy.to_dict(),
            "governance": _gov({"real_provider_probe": False}),
        }

    endpoint = provider_result.get("endpoint_result", {}) if isinstance(provider_result, dict) else {}
    endpoint_response = endpoint.get("endpoint_response", {}) if isinstance(endpoint, dict) else {}
    cards = endpoint_response.get("result_cards", []) if isinstance(endpoint_response, dict) else []
    cards = cards if isinstance(cards, list) else []
    first = cards[0] if cards and isinstance(cards[0], dict) else {}
    visible_count = int(endpoint_response.get("visible_result_count") or provider_result.get("visible_result_count") or 0)

    ready = provider_result.get("status") in {"google_result_ready", "provider_result_ready"} and visible_count > 0
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_probe_result_ready" if ready else "operator_probe_result_not_ready",
        "reason": "" if ready else provider_result.get("reason", "provider_result_not_ready"),
        "created_at": _now(),
        "query": _s(payload.get("query"), "google"),
        "probe_attempted": bool(provider_result.get("probe_attempted")),
        "probe_source": provider_result.get("probe_source", ""),
        "provider_result": provider_result,
        "result_cards": cards,
        "visible_result_count": visible_count,
        "first_result_title": first.get("title", ""),
        "first_result_url": first.get("url", ""),
        "google_result_ready": provider_result.get("google_result_ready", False),
        "policy": policy.to_dict(),
        "governance": _gov({"real_provider_probe": provider_probe is None, "injected_provider_probe": provider_probe is not None}),
    }


def run_operator_provider_google_probe_proof() -> Dict[str, Any]:
    from .real_controlled_provider_result_proof import deterministic_google_provider_probe
    payload = build_operator_probe_request_payload(
        query="google",
        explicit_real_provider_probe=True,
        provider="deterministic-v18-68-operator-provider",
        max_results=3,
    )
    result = execute_operator_provider_probe_request(payload, provider_probe=deterministic_google_provider_probe)
    passed = (
        result.get("status") == "operator_probe_result_ready"
        and result.get("first_result_title") == "Google"
        and result.get("first_result_url") == GOOGLE_URL
    )
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "operator_provider_google_probe_proof_failed",
        "created_at": _now(),
        "operator_probe": result,
        "query": "google",
        "first_result_title": result.get("first_result_title", ""),
        "first_result_url": result.get("first_result_url", ""),
        "visible_result_count": result.get("visible_result_count", 0),
        "policy": RealProviderOperatorProbeRoutePolicy().to_dict(),
        "governance": _gov({"injected_provider_probe": True}),
    }


def create_real_provider_operator_probe_router() -> Any:
    from fastapi import APIRouter
    from pydantic import BaseModel

    class OperatorProviderProbeRequest(BaseModel):
        query: str = "google"
        explicit_real_provider_probe: bool = False
        provider: str = "operator-controlled-real-provider"
        max_results: int = 3

    router = APIRouter(prefix="/api/dashboard/search/provider", tags=["governed-provider-probe"])

    @router.get("/status")
    def provider_probe_status() -> Dict[str, Any]:
        return build_operator_provider_probe_status()

    @router.post("/probe")
    def provider_probe(request: OperatorProviderProbeRequest) -> Dict[str, Any]:
        payload = build_operator_probe_request_payload(
            query=request.query,
            explicit_real_provider_probe=request.explicit_real_provider_probe,
            provider=request.provider,
            max_results=request.max_results,
        )
        return execute_operator_provider_probe_request(payload)

    return router


def _safe_json(response: Any) -> Dict[str, Any]:
    try:
        payload = response.json()
        return payload if isinstance(payload, dict) else {"raw_payload": payload}
    except Exception:
        return {"raw_text": getattr(response, "text", "")}


def build_operator_probe_smoke_app() -> Dict[str, Any]:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI(title="Claire v18.68.1 Operator Provider Probe Smoke App")
    app.include_router(create_real_provider_operator_probe_router())
    client = TestClient(app)

    status_response = client.get(STATUS_PATH)
    blocked_response = client.post(
        PROBE_PATH,
        json={
            "query": "google",
            "explicit_real_provider_probe": False,
            "provider": "operator-controlled-real-provider",
            "max_results": 3,
        },
    )

    status_payload = _safe_json(status_response)
    route_blocked_payload = _safe_json(blocked_response)

    direct_blocked_payload = execute_operator_provider_probe_request(
        build_operator_probe_request_payload(query="google", explicit_real_provider_probe=False)
    )

    route_block_confirmed = (
        blocked_response.status_code == 200
        and route_blocked_payload.get("status") == "blocked"
        and route_blocked_payload.get("reason") == "explicit_real_provider_probe_required"
    )
    direct_block_confirmed = (
        direct_blocked_payload.get("status") == "blocked"
        and direct_blocked_payload.get("reason") == "explicit_real_provider_probe_required"
    )
    status_confirmed = status_response.status_code == 200 and status_payload.get("contract_version", "").startswith("v18.68")

    passed = status_confirmed and (route_block_confirmed or direct_block_confirmed)

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "operator_probe_smoke_assertion_failed",
        "created_at": _now(),
        "status_http_status": status_response.status_code,
        "blocked_probe_http_status": blocked_response.status_code,
        "status_payload": status_payload,
        "blocked_probe_payload": route_blocked_payload,
        "direct_blocked_probe_payload": direct_blocked_payload,
        "status_confirmed": status_confirmed,
        "route_block_confirmed": route_block_confirmed,
        "direct_block_confirmed": direct_block_confirmed,
        "blocked_probe_confirmed": bool(route_block_confirmed or direct_block_confirmed),
        "paths": {"status": STATUS_PATH, "probe": PROBE_PATH},
        "policy": RealProviderOperatorProbeRoutePolicy().to_dict(),
        "governance": _gov({"router_smoke_test": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "GOOGLE_URL",
    "PROBE_PATH",
    "STATUS_PATH",
    "RealProviderOperatorProbeRoutePolicy",
    "build_operator_probe_request_payload",
    "build_operator_probe_smoke_app",
    "build_operator_provider_probe_status",
    "create_real_provider_operator_probe_router",
    "execute_operator_provider_probe_request",
    "run_operator_provider_google_probe_proof",
]
