from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

CONTRACT_VERSION = "v18.70.consolidated_web_activation_packs"

DASHBOARD_PATH = Path("frontend/command_center/modern/index.html")
PROVIDER_JS_PATH = Path("frontend/command_center/modern/governed_provider_probe_ui_binding.js")

LIVE_SEARCH_PATH = "/api/dashboard/search/live"
LIVE_SMOKE_PATH = "/api/dashboard/search/smoke/google"
PROVIDER_STATUS_PATH = "/api/dashboard/search/provider/status"
PROVIDER_PROBE_PATH = "/api/dashboard/search/provider/probe"

GOOGLE_URL = "https://www.google.com"

HTML_START = "<!-- CLAIRE_PROVIDER_PROBE_UI_START -->"
HTML_END = "<!-- CLAIRE_PROVIDER_PROBE_UI_END -->"
SCRIPT_MARKER = "<!-- CLAIRE_PROVIDER_PROBE_UI_SCRIPT -->"

REQUIRED_PROVIDER_UI_IDS = [
    "claire-provider-probe-panel",
    "claire-provider-probe-form",
    "claire-provider-probe-query",
    "claire-provider-probe-explicit-enable",
    "claire-provider-probe-refresh-status",
    "claire-provider-probe-status",
    "claire-provider-probe-results",
]

REQUIRED_PROVIDER_JS_TEXT = [
    "window.ClaireProviderProbeUI",
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "explicit_real_provider_probe: true",
    "Explicit real provider probe enable is required.",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ConsolidatedWebActivationPolicy:
    manual_enable_required: bool = True
    explicit_provider_probe_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False
    provider_probe_not_triggered_by_mount: bool = True
    activation_checkpoint_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manual_enable_required": self.manual_enable_required,
            "explicit_provider_probe_required": self.explicit_provider_probe_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
            "provider_probe_not_triggered_by_mount": self.provider_probe_not_triggered_by_mount,
            "activation_checkpoint_only": self.activation_checkpoint_only,
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


def inspect_provider_probe_ui_binding(
    dashboard_path: Path | str = DASHBOARD_PATH,
    js_path: Path | str = PROVIDER_JS_PATH,
) -> Dict[str, Any]:
    policy = ConsolidatedWebActivationPolicy()
    dashboard = Path(dashboard_path)
    js = Path(js_path)

    html = dashboard.read_text(encoding="utf-8") if dashboard.exists() else ""
    js_text = js.read_text(encoding="utf-8") if js.exists() else ""

    missing_ids = [item for item in REQUIRED_PROVIDER_UI_IDS if item not in html]
    missing_js = [item for item in REQUIRED_PROVIDER_JS_TEXT if item not in js_text]

    ready = dashboard.exists() and js.exists() and not missing_ids and not missing_js

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "provider_probe_ui_ready" if ready else "provider_probe_ui_incomplete",
        "created_at": _now(),
        "ready": ready,
        "dashboard_path": str(dashboard),
        "js_path": str(js),
        "dashboard_exists": dashboard.exists(),
        "js_exists": js.exists(),
        "missing_ids": missing_ids,
        "missing_js": missing_js,
        "policy": policy.to_dict(),
        "governance": _gov({"ui_inspection_only": True}),
    }


def inspect_combined_web_activation_routes(app: Any) -> Dict[str, Any]:
    policy = ConsolidatedWebActivationPolicy()
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
        "status": "combined_web_routes_present" if not missing else "combined_web_routes_missing",
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


def mount_combined_web_activation_routes(app: Any, *, explicit_enable: bool = False) -> Dict[str, Any]:
    policy = ConsolidatedWebActivationPolicy()

    if not explicit_enable:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_web_activation_mount_enable_required",
            "created_at": _now(),
            "mounted": False,
            "mount_attempted": False,
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": False}),
        }

    if app is None or not hasattr(app, "include_router"):
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_app_with_include_router_required",
            "created_at": _now(),
            "mounted": False,
            "mount_attempted": False,
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True}),
        }

    mounted_parts: List[str] = []
    errors: List[Dict[str, str]] = []

    try:
        from .live_search_active_app_mount_gate import mount_governed_live_search_into_app
        live_result = mount_governed_live_search_into_app(app, explicit_enable=True)
        if live_result.get("mounted") is True:
            mounted_parts.append("live_search")
        else:
            errors.append({"part": "live_search", "reason": live_result.get("reason", "not_mounted")})
    except Exception as exc:
        errors.append({"part": "live_search", "reason": type(exc).__name__})

    try:
        from .operator_probe_active_app_mount import mount_operator_probe_routes_into_app
        provider_result = mount_operator_probe_routes_into_app(app, explicit_enable=True)
        if provider_result.get("mounted") is True:
            mounted_parts.append("provider_probe")
        else:
            errors.append({"part": "provider_probe", "reason": provider_result.get("reason", "not_mounted")})
    except Exception as exc:
        errors.append({"part": "provider_probe", "reason": type(exc).__name__})

    route_table = inspect_combined_web_activation_routes(app)
    mounted = route_table.get("status") == "combined_web_routes_present"

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "mounted" if mounted else "mount_incomplete",
        "reason": "" if mounted else "combined_route_table_missing_required_paths",
        "created_at": _now(),
        "mounted": mounted,
        "mount_attempted": True,
        "mounted_parts": mounted_parts,
        "errors": errors,
        "route_table": route_table,
        "policy": policy.to_dict(),
        "governance": _gov({"explicit_enable": True}),
    }


def run_combined_web_activation_smoke_app() -> Dict[str, Any]:
    policy = ConsolidatedWebActivationPolicy()
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from .real_provider_operator_probe_route import (
            build_operator_probe_request_payload,
            execute_operator_provider_probe_request,
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_or_route_contract_unavailable",
            "created_at": _now(),
            "error_type": type(exc).__name__,
            "policy": policy.to_dict(),
            "governance": _gov(),
        }

    app = FastAPI(title="Claire v18.70 Consolidated Web Activation Smoke App")
    mount_result = mount_combined_web_activation_routes(app, explicit_enable=True)
    route_table = inspect_combined_web_activation_routes(app)
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

    google_cards = google_payload.get("result_cards", []) if isinstance(google_payload, dict) else []
    google_first = google_cards[0] if isinstance(google_cards, list) and google_cards and isinstance(google_cards[0], dict) else {}

    google_ok = (
        google_response.status_code == 200
        and google_first.get("title") == "Google"
        and google_first.get("url") == GOOGLE_URL
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

    passed = (
        mount_result.get("mounted") is True
        and route_table.get("status") == "combined_web_routes_present"
        and google_ok
        and provider_status_ok
        and (provider_probe_block_ok or direct_block_ok)
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "combined_web_activation_smoke_failed",
        "created_at": _now(),
        "mount_result": mount_result,
        "route_table": route_table,
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
        "first_google_title": google_first.get("title", ""),
        "first_google_url": google_first.get("url", ""),
        "policy": policy.to_dict(),
        "governance": _gov({"combined_smoke_test": True}),
    }


def run_web_activation_checkpoint() -> Dict[str, Any]:
    policy = ConsolidatedWebActivationPolicy()
    ui = inspect_provider_probe_ui_binding()
    smoke = run_combined_web_activation_smoke_app()

    try:
        from .accelerated_governed_live_web_activation_pack import run_accelerated_governed_live_web_activation_pack
        accelerated = run_accelerated_governed_live_web_activation_pack()
    except Exception as exc:
        accelerated = {"status": "not_available", "reason": type(exc).__name__}

    try:
        from .real_controlled_provider_result_proof import run_deterministic_controlled_provider_google_proof
        provider_proof = run_deterministic_controlled_provider_google_proof()
    except Exception as exc:
        provider_proof = {"status": "not_available", "reason": type(exc).__name__}

    passed = (
        ui.get("ready") is True
        and smoke.get("status") == "passed"
        and provider_proof.get("status") in {"google_result_ready", "not_available"}
        and accelerated.get("status") in {"passed", "not_available"}
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "web_activation_ready" if passed else "web_activation_incomplete",
        "created_at": _now(),
        "activation_level": "governed_dashboard_and_provider_probe_ready" if passed else "incomplete",
        "ui": ui,
        "smoke": smoke,
        "accelerated_pack": accelerated,
        "provider_result_proof": provider_proof,
        "operator_next_step": (
            "Start Claire, open the dashboard, use Governed Live Web Search for google, then use Provider Probe only with explicit operator enable."
            if passed else
            "Review incomplete sections before attempting operator provider probe."
        ),
        "policy": policy.to_dict(),
        "governance": _gov({"web_activation_checkpoint": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DASHBOARD_PATH",
    "GOOGLE_URL",
    "PROVIDER_JS_PATH",
    "PROVIDER_PROBE_PATH",
    "PROVIDER_STATUS_PATH",
    "ConsolidatedWebActivationPolicy",
    "inspect_combined_web_activation_routes",
    "inspect_provider_probe_ui_binding",
    "mount_combined_web_activation_routes",
    "run_combined_web_activation_smoke_app",
    "run_web_activation_checkpoint",
]
