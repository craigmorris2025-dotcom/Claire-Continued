from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Dict, Iterable, List, Mapping, Optional

CONTRACT_VERSION = "v18.71.active_app_final_web_activation_mount_verification"

LIVE_SEARCH_PATH = "/api/dashboard/search/live"
LIVE_SMOKE_PATH = "/api/dashboard/search/smoke/google"
PROVIDER_STATUS_PATH = "/api/dashboard/search/provider/status"
PROVIDER_PROBE_PATH = "/api/dashboard/search/provider/probe"
GOOGLE_URL = "https://www.google.com"

DEFAULT_ACTIVE_APP_CANDIDATES = [
    "main:app",
    "claire.main:app",
    "claire.server:app",
    "main:app",
    "runtime_core.api.app:app",
    "src.main:app",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ActiveAppFinalWebActivationMountPolicy:
    explicit_mount_required: bool = True
    active_app_import_is_read_only: bool = True
    real_provider_probe_not_triggered: bool = True
    manual_enable_required: bool = True
    explicit_provider_probe_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False
    final_mount_verification_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_mount_required": self.explicit_mount_required,
            "active_app_import_is_read_only": self.active_app_import_is_read_only,
            "real_provider_probe_not_triggered": self.real_provider_probe_not_triggered,
            "manual_enable_required": self.manual_enable_required,
            "explicit_provider_probe_required": self.explicit_provider_probe_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
            "final_mount_verification_only": self.final_mount_verification_only,
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
        "real_provider_probe_triggered": False,
    }
    if extra:
        data.update(dict(extra))
    return data


def inspect_active_app_candidates(candidates: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    policy = ActiveAppFinalWebActivationMountPolicy()

    for candidate in list(candidates or DEFAULT_ACTIVE_APP_CANDIDATES):
        row = {
            "candidate": candidate,
            "available": False,
            "module_imported": False,
            "attribute_found": False,
            "include_router_available": False,
            "reason": "",
        }
        if ":" not in candidate:
            row["reason"] = "invalid_candidate_format"
            rows.append(row)
            continue

        module_name, attr_name = candidate.split(":", 1)
        try:
            module = import_module(module_name)
            row["module_imported"] = True
            app = getattr(module, attr_name)
            row["attribute_found"] = True
            row["include_router_available"] = hasattr(app, "include_router")
            row["available"] = bool(row["include_router_available"])
            if not row["available"]:
                row["reason"] = "attribute_is_not_fastapi_like_app"
        except Exception as exc:
            row["reason"] = type(exc).__name__
        rows.append(row)

    available = [row for row in rows if row.get("available") is True]
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "active_app_candidate_found" if available else "no_active_app_candidate_found",
        "created_at": _now(),
        "checked": rows,
        "available_candidates": available,
        "policy": policy.to_dict(),
        "governance": _gov({"active_app_import_read_only": True}),
    }


def verify_app_has_final_web_activation_routes(app: Any) -> Dict[str, Any]:
    policy = ActiveAppFinalWebActivationMountPolicy()
    rows: List[Dict[str, Any]] = []

    for route in getattr(app, "routes", []) or []:
        path = str(getattr(route, "path", ""))
        methods = getattr(route, "methods", set()) or set()
        rows.append({
            "path": path,
            "methods": sorted(str(method) for method in methods),
            "name": str(getattr(route, "name", "")),
        })

    paths = {row["path"] for row in rows}
    required = [LIVE_SEARCH_PATH, LIVE_SMOKE_PATH, PROVIDER_STATUS_PATH, PROVIDER_PROBE_PATH]
    missing = [path for path in required if path not in paths]

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "final_web_activation_routes_present" if not missing else "final_web_activation_routes_missing",
        "created_at": _now(),
        "routes": rows,
        "required_paths": required,
        "missing_paths": missing,
        "live_search_present": LIVE_SEARCH_PATH in paths,
        "live_smoke_present": LIVE_SMOKE_PATH in paths,
        "provider_status_present": PROVIDER_STATUS_PATH in paths,
        "provider_probe_present": PROVIDER_PROBE_PATH in paths,
        "policy": policy.to_dict(),
        "governance": _gov({"route_table_inspection": True}),
    }


def mount_final_web_activation_routes_into_app(
    app: Any,
    *,
    explicit_enable: bool = False,
) -> Dict[str, Any]:
    policy = ActiveAppFinalWebActivationMountPolicy()

    if not explicit_enable:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_final_web_activation_mount_enable_required",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": False,
            "route_table": {},
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": False}),
        }

    if app is None or not hasattr(app, "include_router"):
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_app_with_include_router_required",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": False,
            "route_table": {},
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True}),
        }

    try:
        from .consolidated_web_activation_packs import mount_combined_web_activation_routes
        mount_result = mount_combined_web_activation_routes(app, explicit_enable=True)
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "consolidated_web_activation_mount_unavailable",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": False,
            "error_type": type(exc).__name__,
            "route_table": {},
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True}),
        }

    route_table = verify_app_has_final_web_activation_routes(app)
    mounted = mount_result.get("mounted") is True and route_table.get("status") == "final_web_activation_routes_present"

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "mounted" if mounted else "mount_incomplete",
        "reason": "" if mounted else "final_web_activation_routes_not_verified",
        "created_at": _now(),
        "mount_attempted": True,
        "mounted": mounted,
        "mount_result": mount_result,
        "route_table": route_table,
        "policy": policy.to_dict(),
        "governance": _gov({"explicit_enable": True}),
    }


def verify_final_web_activation_endpoints(app: Any) -> Dict[str, Any]:
    policy = ActiveAppFinalWebActivationMountPolicy()
    try:
        from fastapi.testclient import TestClient
        from .real_provider_operator_probe_route import (
            build_operator_probe_request_payload,
            execute_operator_provider_probe_request,
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "testclient_or_probe_contract_unavailable",
            "created_at": _now(),
            "error_type": type(exc).__name__,
            "policy": policy.to_dict(),
            "governance": _gov(),
        }

    client = TestClient(app)

    google_response = client.get(LIVE_SMOKE_PATH)
    provider_status_response = client.get(PROVIDER_STATUS_PATH)
    provider_probe_response = client.post(PROVIDER_PROBE_PATH, json={
        "query": "google",
        "explicit_real_provider_probe": False,
        "provider": "operator-controlled-real-provider",
        "max_results": 3,
    })

    def safe_json(response: Any) -> Dict[str, Any]:
        try:
            payload = response.json()
            return payload if isinstance(payload, dict) else {"raw_payload": payload}
        except Exception:
            return {"raw_text": getattr(response, "text", "")}

    google_payload = safe_json(google_response)
    provider_status_payload = safe_json(provider_status_response)
    provider_probe_payload = safe_json(provider_probe_response)
    direct_probe_block = execute_operator_provider_probe_request(
        build_operator_probe_request_payload(query="google", explicit_real_provider_probe=False)
    )

    cards = google_payload.get("result_cards", []) if isinstance(google_payload, dict) else []
    first = cards[0] if isinstance(cards, list) and cards and isinstance(cards[0], dict) else {}

    google_ok = (
        google_response.status_code == 200
        and first.get("title") == "Google"
        and first.get("url") == GOOGLE_URL
    )
    provider_status_ok = provider_status_response.status_code == 200 and isinstance(provider_status_payload, dict)
    provider_probe_block_ok = (
        provider_probe_response.status_code == 200
        and isinstance(provider_probe_payload, dict)
        and provider_probe_payload.get("status") == "blocked"
        and provider_probe_payload.get("reason") == "explicit_real_provider_probe_required"
    )
    direct_block_ok = (
        direct_probe_block.get("status") == "blocked"
        and direct_probe_block.get("reason") == "explicit_real_provider_probe_required"
    )

    passed = google_ok and provider_status_ok and bool(provider_probe_block_ok or direct_block_ok)

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "final_web_activation_endpoints_verified" if passed else "final_web_activation_endpoints_failed",
        "reason": "" if passed else "endpoint_verification_failed",
        "created_at": _now(),
        "google_http_status": google_response.status_code,
        "provider_status_http_status": provider_status_response.status_code,
        "provider_probe_http_status": provider_probe_response.status_code,
        "google_payload": google_payload,
        "provider_status_payload": provider_status_payload,
        "provider_probe_payload": provider_probe_payload,
        "direct_probe_block": direct_probe_block,
        "google_ok": google_ok,
        "provider_status_ok": provider_status_ok,
        "provider_probe_block_confirmed": bool(provider_probe_block_ok or direct_block_ok),
        "first_google_title": first.get("title", ""),
        "first_google_url": first.get("url", ""),
        "policy": policy.to_dict(),
        "governance": _gov({"endpoint_verification": True}),
    }


def run_active_app_final_web_activation_mount_verification(
    app: Any = None,
    *,
    explicit_enable: bool = True,
) -> Dict[str, Any]:
    policy = ActiveAppFinalWebActivationMountPolicy()

    if app is None:
        try:
            from fastapi import FastAPI
            app = FastAPI(title="Claire v18.71 Active App Final Web Activation Verification")
            app_source = "verification_fastapi_app"
        except Exception as exc:
            return {
                "contract_version": CONTRACT_VERSION,
                "status": "blocked",
                "reason": "fastapi_unavailable",
                "created_at": _now(),
                "error_type": type(exc).__name__,
                "policy": policy.to_dict(),
                "governance": _gov(),
            }
    else:
        app_source = "provided_app"

    mount = mount_final_web_activation_routes_into_app(app, explicit_enable=explicit_enable)
    route_table = verify_app_has_final_web_activation_routes(app)

    if mount.get("mounted") is not True:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": mount.get("reason", "mount_not_verified"),
            "created_at": _now(),
            "app_source": app_source,
            "mount": mount,
            "route_table": route_table,
            "endpoints": {},
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": explicit_enable}),
        }

    endpoints = verify_final_web_activation_endpoints(app)
    passed = (
        route_table.get("status") == "final_web_activation_routes_present"
        and endpoints.get("status") == "final_web_activation_endpoints_verified"
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "final_web_activation_mount_verified" if passed else "final_web_activation_mount_failed",
        "reason": "" if passed else "final_mount_or_endpoint_verification_failed",
        "created_at": _now(),
        "app_source": app_source,
        "mount": mount,
        "route_table": route_table,
        "endpoints": endpoints,
        "operator_next_step": (
            "Start Claire, open dashboard, check Manual governed live-search enable, type google, press Search."
            if passed else
            "Review route table and endpoint verification before operator dashboard test."
        ),
        "policy": policy.to_dict(),
        "governance": _gov({"explicit_enable": explicit_enable}),
    }


def run_final_web_activation_operator_report() -> Dict[str, Any]:
    policy = ActiveAppFinalWebActivationMountPolicy()
    verification = run_active_app_final_web_activation_mount_verification(explicit_enable=True)

    try:
        from .consolidated_web_activation_packs import run_web_activation_checkpoint
        checkpoint = run_web_activation_checkpoint()
    except Exception as exc:
        checkpoint = {"status": "not_available", "reason": type(exc).__name__}

    passed = (
        verification.get("status") == "final_web_activation_mount_verified"
        and checkpoint.get("status") in {"web_activation_ready", "not_available"}
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_report_ready" if passed else "operator_report_incomplete",
        "created_at": _now(),
        "web_activation_mount_verified": verification.get("status") == "final_web_activation_mount_verified",
        "checkpoint_status": checkpoint.get("status"),
        "verification": verification,
        "checkpoint": checkpoint,
        "manual_dashboard_test": {
            "step_1": "Start Claire normally.",
            "step_2": "Open the active dashboard.",
            "step_3": "Confirm Governed Live Web Search and Governed Provider Probe panels are visible.",
            "step_4": "Check Manual governed live-search enable.",
            "step_5": "Type google and press Search.",
            "expected_result": "Google / https://www.google.com",
            "provider_probe_note": "Provider Probe requires explicit operator enable and remains blocked until checked.",
        },
        "policy": policy.to_dict(),
        "governance": _gov({"operator_visible_report": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_ACTIVE_APP_CANDIDATES",
    "GOOGLE_URL",
    "LIVE_SEARCH_PATH",
    "LIVE_SMOKE_PATH",
    "PROVIDER_PROBE_PATH",
    "PROVIDER_STATUS_PATH",
    "ActiveAppFinalWebActivationMountPolicy",
    "inspect_active_app_candidates",
    "mount_final_web_activation_routes_into_app",
    "run_active_app_final_web_activation_mount_verification",
    "run_final_web_activation_operator_report",
    "verify_app_has_final_web_activation_routes",
    "verify_final_web_activation_endpoints",
]
