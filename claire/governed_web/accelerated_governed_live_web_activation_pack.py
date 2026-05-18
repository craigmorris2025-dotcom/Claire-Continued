
# Claire Syntalion v18.66
# Accelerated Governed Live Web Activation Pack
#
# This pack consolidates the remaining governed live web activation checks:
# environment flags, dashboard surface, endpoint/fetch proof, mounted route proof,
# visible google result proof, and provider-readiness diagnostics.
#
# It does not perform uncontrolled browsing, mutate runtime truth, enable
# autonomous execution, or perform automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional
import os


CONTRACT_VERSION = "v18.66.accelerated_governed_live_web_activation_pack"

GOOGLE_QUERY = "google"
GOOGLE_TITLE = "Google"
GOOGLE_URL = "https://www.google.com"

ENV_FLAGS = [
    "CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE",
    "CLAIRE_ALLOW_CONTROLLED_METADATA_GET",
    "CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET",
    "CLAIRE_ALLOW_REAL_SEARCH_PROVIDER",
]

CRITICAL_MODULES = [
    "claire.governed_web.dashboard_search_result_binding",
    "claire.governed_web.dashboard_search_query_execution_bridge",
    "claire.governed_web.dashboard_search_endpoint_result_contract",
    "claire.governed_web.dashboard_live_search_route_mount_adapter",
    "claire.governed_web.dashboard_live_search_ui_fetch_binding",
    "claire.governed_web.dashboard_search_bar_html_integration_gate",
    "claire.governed_web.dashboard_to_endpoint_fetch_proof",
    "claire.governed_web.first_active_dashboard_google_result_proof",
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
class AcceleratedGovernedLiveWebActivationPolicy:
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False
    real_provider_requires_explicit_probe: bool = True
    deterministic_google_proof_allowed: bool = True
    activation_pack_only: bool = True
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manual_enable_required": self.manual_enable_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
            "real_provider_requires_explicit_probe": self.real_provider_requires_explicit_probe,
            "deterministic_google_proof_allowed": self.deterministic_google_proof_allowed,
            "activation_pack_only": self.activation_pack_only,
            "max_results": self.max_results,
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


def inspect_activation_environment() -> Dict[str, Any]:
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
            "set CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=1",
            "set CLAIRE_ALLOW_CONTROLLED_METADATA_GET=1",
            "set CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET=1",
            "set CLAIRE_ALLOW_REAL_SEARCH_PROVIDER=1",
        ],
        "governance": _governance({"environment_inspection_only": True}),
    }


def inspect_activation_modules(modules: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    module_names = list(modules or CRITICAL_MODULES)
    rows: List[Dict[str, Any]] = []

    for name in module_names:
        try:
            import_module(name)
            rows.append({"module": name, "available": True, "reason": ""})
        except Exception as exc:
            rows.append({"module": name, "available": False, "reason": type(exc).__name__})

    missing = [row for row in rows if row["available"] is False]
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "critical_modules_available" if not missing else "critical_modules_missing",
        "created_at": _utc_now(),
        "modules": rows,
        "missing_modules": missing,
        "all_available": not missing,
        "governance": _governance({"module_inspection_only": True}),
    }


def inspect_dashboard_activation_surface(
    dashboard_path: Path | str = Path("frontend/command_center/modern/index.html"),
    js_path: Path | str = Path("frontend/command_center/modern/governed_live_search_ui_binding.js"),
) -> Dict[str, Any]:
    try:
        from .first_active_dashboard_google_result_proof import inspect_active_dashboard_google_search_surface
        surface = inspect_active_dashboard_google_search_surface(dashboard_path, js_path)
        ready = surface.get("status") == "dashboard_google_surface_ready"
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "dashboard_surface_ready" if ready else "dashboard_surface_incomplete",
            "created_at": _utc_now(),
            "ready": ready,
            "source": "v18.65.first_active_dashboard_google_result_proof",
            "surface": surface,
            "governance": _governance({"surface_inspection_only": True}),
        }
    except Exception as exc:
        dashboard = Path(dashboard_path)
        js_file = Path(js_path)
        html = dashboard.read_text(encoding="utf-8") if dashboard.exists() else ""
        js = js_file.read_text(encoding="utf-8") if js_file.exists() else ""
        required_html = [
            "claire-governed-live-search-form",
            "claire-governed-live-search-input",
            "claire-governed-live-search-manual-enable",
            "claire-governed-live-search-results",
            "governed_live_search_ui_binding.js",
        ]
        required_js = [
            "window.ClaireLiveSearch",
            "/api/dashboard/search/live",
            "manual_enable_confirmed: true",
            "result_cards",
        ]
        missing_html = [item for item in required_html if item not in html]
        missing_js = [item for item in required_js if item not in js]
        ready = dashboard.exists() and js_file.exists() and not missing_html and not missing_js
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "dashboard_surface_ready" if ready else "dashboard_surface_incomplete",
            "created_at": _utc_now(),
            "ready": ready,
            "source": "fallback_surface_inspection",
            "reason": type(exc).__name__,
            "dashboard_path": str(dashboard),
            "js_path": str(js_file),
            "dashboard_exists": dashboard.exists(),
            "js_exists": js_file.exists(),
            "missing_html": missing_html,
            "missing_js": missing_js,
            "governance": _governance({"surface_inspection_only": True}),
        }


def deterministic_google_activation_executor(**kwargs: Any) -> Dict[str, Any]:
    provider = _string(kwargs.get("provider"), "accelerated-activation-provider")
    session_id = _string(kwargs.get("session_id"), "accelerated-activation-session")
    return {
        "provider_status": "ok",
        "query": GOOGLE_QUERY,
        "provider": provider,
        "session_id": session_id,
        "results": [
            {
                "title": GOOGLE_TITLE,
                "url": GOOGLE_URL,
                "snippet": "Google result produced by the accelerated governed live web activation proof.",
                "provider": provider,
                "trust_score": 1.0,
                "result_id": "v18-66-google-activation-result",
                "evidence_id": "v18-66-google-activation-evidence",
            }
        ],
    }


def run_endpoint_google_activation_proof() -> Dict[str, Any]:
    try:
        from .dashboard_to_endpoint_fetch_proof import (
            build_dashboard_fetch_request_payload,
            execute_fetch_payload_against_endpoint_contract,
        )

        payload = build_dashboard_fetch_request_payload(
            query=GOOGLE_QUERY,
            manual_enable_confirmed=True,
            provider="accelerated-activation-provider",
            session_id="v18-66-accelerated-activation-session",
            max_results=3,
            require_provider_env=False,
            require_limited_body_env=False,
        )
        result = execute_fetch_payload_against_endpoint_contract(
            payload,
            executor=deterministic_google_activation_executor,
            request_id="v18-66-accelerated-google-activation",
        )
        response = result.get("endpoint_response") if isinstance(result, dict) else {}
        cards = response.get("result_cards") if isinstance(response, dict) else []
        first = cards[0] if isinstance(cards, list) and cards and isinstance(cards[0], dict) else {}
        passed = (
            result.get("status") == "endpoint_response_received"
            and response.get("endpoint_status") == "endpoint_response_ready"
            and first.get("title") == GOOGLE_TITLE
            and first.get("url") == GOOGLE_URL
            and int(response.get("visible_result_count") or 0) >= 1
        )
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "passed" if passed else "failed",
            "reason": "" if passed else "endpoint_google_activation_proof_failed",
            "created_at": _utc_now(),
            "source": "v18.64.dashboard_to_endpoint_fetch_proof",
            "query": GOOGLE_QUERY,
            "first_result_title": first.get("title", ""),
            "first_result_url": first.get("url", ""),
            "visible_result_count": int(response.get("visible_result_count") or 0) if isinstance(response, dict) else 0,
            "fetch_result": result,
            "governance": _governance({"deterministic_executor": True}),
        }
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": "endpoint_fetch_proof_unavailable",
            "created_at": _utc_now(),
            "source": "fallback_error",
            "error_type": type(exc).__name__,
            "query": GOOGLE_QUERY,
            "first_result_title": "",
            "first_result_url": "",
            "visible_result_count": 0,
            "governance": _governance({"deterministic_executor": True}),
        }


def run_dashboard_google_activation_proof() -> Dict[str, Any]:
    try:
        from .first_active_dashboard_google_result_proof import run_first_active_dashboard_google_result_proof
        result = run_first_active_dashboard_google_result_proof()
        passed = (
            result.get("status") == "passed"
            and result.get("visible_result_ready") is True
            and result.get("first_result_title") == GOOGLE_TITLE
            and result.get("first_result_url") == GOOGLE_URL
        )
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "passed" if passed else "failed",
            "reason": "" if passed else "dashboard_google_activation_proof_failed",
            "created_at": _utc_now(),
            "source": "v18.65.first_active_dashboard_google_result_proof",
            "query": GOOGLE_QUERY,
            "visible_result_ready": bool(result.get("visible_result_ready")),
            "first_result_title": result.get("first_result_title", ""),
            "first_result_url": result.get("first_result_url", ""),
            "proof": result,
            "governance": _governance({"dashboard_surface_proof": True}),
        }
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": "dashboard_google_proof_unavailable",
            "created_at": _utc_now(),
            "source": "fallback_error",
            "error_type": type(exc).__name__,
            "query": GOOGLE_QUERY,
            "visible_result_ready": False,
            "first_result_title": "",
            "first_result_url": "",
            "governance": _governance({"dashboard_surface_proof": True}),
        }


def run_mounted_route_activation_proof() -> Dict[str, Any]:
    try:
        from .active_app_mounted_route_verification import run_active_app_mounted_route_verification
        result = run_active_app_mounted_route_verification(explicit_enable=True)
        passed = (
            result.get("status") == "passed"
            and result.get("mount_verification", {}).get("mounted") is True
            and result.get("google_confirmed", True) is True
        )
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "passed" if passed else "failed",
            "reason": "" if passed else "mounted_route_activation_proof_failed",
            "created_at": _utc_now(),
            "source": "v18.63.active_app_mounted_route_verification",
            "mounted": bool(result.get("mount_verification", {}).get("mounted")),
            "proof": result,
            "governance": _governance({"mounted_route_testclient_proof": True}),
        }
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "not_available",
            "reason": "mounted_route_verification_unavailable",
            "created_at": _utc_now(),
            "source": "fallback_error",
            "error_type": type(exc).__name__,
            "mounted": False,
            "governance": _governance({"mounted_route_testclient_proof": True}),
        }


def inspect_controlled_provider_activation_readiness(
    *,
    explicit_real_provider_probe: bool = False,
    provider_probe: Optional[Callable[..., Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    environment = inspect_activation_environment()
    all_flags_enabled = bool(environment.get("all_required_enabled"))

    if not explicit_real_provider_probe:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "real_provider_probe_not_requested",
            "reason": "explicit_real_provider_probe_required",
            "created_at": _utc_now(),
            "environment": environment,
            "probe_attempted": False,
            "provider_response": {},
            "ready_for_operator_probe": all_flags_enabled,
            "governance": _governance({
                "real_provider_probe": False,
                "explicit_real_provider_probe_required": True,
            }),
        }

    if not all_flags_enabled:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "required_env_flags_incomplete",
            "created_at": _utc_now(),
            "environment": environment,
            "probe_attempted": False,
            "provider_response": {},
            "ready_for_operator_probe": False,
            "governance": _governance({
                "real_provider_probe": False,
                "explicit_real_provider_probe_required": True,
            }),
        }

    if provider_probe is None:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "provider_probe_callable_required",
            "created_at": _utc_now(),
            "environment": environment,
            "probe_attempted": False,
            "provider_response": {},
            "ready_for_operator_probe": True,
            "governance": _governance({
                "real_provider_probe": False,
                "explicit_real_provider_probe_required": True,
            }),
        }

    try:
        response = dict(provider_probe(query=GOOGLE_QUERY, max_results=3, provider="operator-controlled-provider"))
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": "provider_probe_exception",
            "created_at": _utc_now(),
            "environment": environment,
            "probe_attempted": True,
            "provider_response": {},
            "error_type": type(exc).__name__,
            "ready_for_operator_probe": True,
            "governance": _governance({
                "real_provider_probe": True,
                "explicit_real_provider_probe_required": True,
            }),
        }

    results = response.get("results") if isinstance(response, dict) else []
    passed = isinstance(results, list) and len(results) > 0
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "provider_probe_returned_results" if passed else "provider_probe_returned_no_results",
        "reason": "" if passed else "no_results",
        "created_at": _utc_now(),
        "environment": environment,
        "probe_attempted": True,
        "provider_response": response,
        "ready_for_operator_probe": True,
        "governance": _governance({
            "real_provider_probe": True,
            "explicit_real_provider_probe_required": True,
        }),
    }


def run_accelerated_governed_live_web_activation_pack(
    *,
    explicit_real_provider_probe: bool = False,
    provider_probe: Optional[Callable[..., Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    policy = AcceleratedGovernedLiveWebActivationPolicy()

    environment = inspect_activation_environment()
    modules = inspect_activation_modules()
    surface = inspect_dashboard_activation_surface()
    endpoint_google = run_endpoint_google_activation_proof()
    dashboard_google = run_dashboard_google_activation_proof()
    mounted_route = run_mounted_route_activation_proof()
    provider_readiness = inspect_controlled_provider_activation_readiness(
        explicit_real_provider_probe=explicit_real_provider_probe,
        provider_probe=provider_probe,
    )

    endpoint_ready = endpoint_google.get("status") == "passed"
    dashboard_ready = dashboard_google.get("status") == "passed"
    surface_ready = surface.get("ready") is True
    modules_ready = modules.get("all_available") is True
    mounted_ready = mounted_route.get("status") in {"passed", "not_available"}
    visible_google_ready = endpoint_ready and dashboard_ready and surface_ready and modules_ready

    if visible_google_ready and provider_readiness.get("status") == "provider_probe_returned_results":
        activation_level = "controlled_real_provider_probe_returned_results"
    elif visible_google_ready:
        activation_level = "dashboard_google_result_ready"
    else:
        activation_level = "activation_incomplete"

    passed = visible_google_ready

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "activation_level": activation_level,
        "reason": "" if passed else "accelerated_activation_requirements_not_met",
        "created_at": _utc_now(),
        "query": GOOGLE_QUERY,
        "expected_title": GOOGLE_TITLE,
        "expected_url": GOOGLE_URL,
        "environment": environment,
        "modules": modules,
        "surface": surface,
        "endpoint_google": endpoint_google,
        "dashboard_google": dashboard_google,
        "mounted_route": mounted_route,
        "provider_readiness": provider_readiness,
        "visible_google_ready": visible_google_ready,
        "endpoint_ready": endpoint_ready,
        "dashboard_ready": dashboard_ready,
        "surface_ready": surface_ready,
        "modules_ready": modules_ready,
        "mounted_ready": mounted_ready,
        "operator_next_step": (
            "Open dashboard, check Manual governed live-search enable, type google, press Search."
            if visible_google_ready
            else "Review failed activation sections before attempting live provider execution."
        ),
        "policy": policy.to_dict(),
        "governance": _governance({
            "accelerated_activation_pack": True,
            "explicit_real_provider_probe": bool(explicit_real_provider_probe),
        }),
    }


def build_accelerated_web_activation_operator_summary() -> Dict[str, Any]:
    result = run_accelerated_governed_live_web_activation_pack()
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_summary_ready",
        "created_at": _utc_now(),
        "activation_level": result.get("activation_level"),
        "visible_google_ready": result.get("visible_google_ready"),
        "operator_next_step": result.get("operator_next_step"),
        "expected_manual_dashboard_test": {
            "query": GOOGLE_QUERY,
            "expected_title": GOOGLE_TITLE,
            "expected_url": GOOGLE_URL,
            "manual_enable_required": True,
        },
        "provider_flags_enabled": result.get("environment", {}).get("all_required_enabled", False),
        "real_provider_probe_status": result.get("provider_readiness", {}).get("status"),
        "policy": AcceleratedGovernedLiveWebActivationPolicy().to_dict(),
        "governance": _governance({"operator_visible_summary": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "ENV_FLAGS",
    "GOOGLE_QUERY",
    "GOOGLE_TITLE",
    "GOOGLE_URL",
    "AcceleratedGovernedLiveWebActivationPolicy",
    "build_accelerated_web_activation_operator_summary",
    "deterministic_google_activation_executor",
    "inspect_activation_environment",
    "inspect_activation_modules",
    "inspect_controlled_provider_activation_readiness",
    "inspect_dashboard_activation_surface",
    "run_accelerated_governed_live_web_activation_pack",
    "run_dashboard_google_activation_proof",
    "run_endpoint_google_activation_proof",
    "run_mounted_route_activation_proof",
]
