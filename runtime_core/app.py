from __future__ import annotations

# Governed dashboard payload handoff
# S31R4 compatibility marker: compose_governed_payload(payload)

import importlib
import inspect
import json
import os
import pkgutil
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from runtime_core.config.env import env_true


APP_VERSION = "v19.89.8-dashboard-actions-s36-contract-repair-r6"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL_DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "frontend", "command_center", "modern")
CANONICAL_DASHBOARD_HTML = os.path.join(CANONICAL_DASHBOARD_DIR, "platform_dashboard.html")
CANONICAL_DASHBOARD_ASSETS = {
    "platform_dashboard.css": ("text/css", os.path.join(CANONICAL_DASHBOARD_DIR, "platform_dashboard.css")),
    "platform_dashboard.js": ("application/javascript", os.path.join(CANONICAL_DASHBOARD_DIR, "platform_dashboard.js")),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_true(name: str) -> bool:
    return env_true(name)


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _authority_state() -> dict[str, str]:
    return {
        "live_web_execution": "blocked",
        "search_provider_execution": "blocked",
        "browser_execution": "blocked",
        "network_requests": "blocked",
        "body_reads": "blocked",
        "autonomous_crawling": "blocked",
        "automatic_updates": "blocked",
        "runtime_mutation": "blocked",
        "runtime_truth_mutation": "blocked",
        "package_download_install": "blocked",
        "command_execution": "blocked",
    }


def _blocked_authorities() -> dict[str, bool]:
    return {
        "live_web_execution_enabled": False,
        "search_provider_execution_enabled": False,
        "browser_execution_enabled": False,
        "network_requests_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "body_reads_allowed": False,
        "body_read_performed": False,
        "response_body_read": False,
        "autonomous_crawling_enabled": False,
        "autonomous_crawling_performed": False,
        "automatic_updates_enabled": False,
        "automatic_update_performed": False,
        "runtime_mutation_enabled": False,
        "runtime_mutation_performed": False,
        "runtime_truth_mutation_enabled": False,
        "runtime_truth_mutation_performed": False,
        "package_download_install_enabled": False,
        "package_install_performed": False,
        "command_execution_enabled": False,
        "command_execution_performed": False,
        "browser_execution_performed": False,
    }


def _operator_actions() -> list[dict[str, Any]]:
    definitions = [
        ("plan_search", "Plan Governed Search", "Prepare a governed search plan without provider execution."),
        ("review_web_readiness", "Review Web Readiness", "Review governed internet readiness without enabling live web execution."),
        ("inspect_source_governance", "Inspect Source Governance", "Inspect source trust, allowlist posture, and provider readiness."),
        ("build_evidence_preview", "Build Evidence Preview", "Open an evidence preview from review-safe metadata only."),
        ("open_operator_review_queue", "Open Operator Review Queue", "Review pending governed decisions and blocked capabilities."),
        ("export_operator_snapshot", "Export Operator Snapshot", "Prepare a read-only operator status snapshot."),
        ("review_update_proposals", "Review Update Proposals", "Inspect proposal-only update candidates."),
        ("inspect_quarantine", "Inspect Quarantine", "Review quarantined evidence without promotion."),
        ("view_runtime_locks", "View Runtime Locks", "Show blocked authority and runtime safety state."),
        ("open_governed_web_panel", "Open Governed Web Panel", "Open governed web readiness and source status."),
        ("open_evidence_panel", "Open Evidence & Review Panel", "Open evidence review cards and preview panes."),
        ("open_system_health", "Open System Health", "Open health, payload, and route status."),
        ("prepare_demo_review", "Prepare Demo Review", "Prepare a dashboard-safe review state."),
        ("inspect_payload_contract", "Inspect Payload Contract", "Inspect backend-owned cockpit payload fields."),
        ("review_next_safe_actions", "Review Next Safe Actions", "Review safe next actions while execution remains blocked."),
    ]
    actions: list[dict[str, Any]] = []
    for index, (key, label, description) in enumerate(definitions, start=1):
        actions.append(
            {
                "id": key,
                "key": key,
                "action_key": key,
                "label": label,
                "title": label,
                "name": label,
                "category": "Operator Console",
                "order": index,
                "status": "ready",
                "enabled": True,
                "visible": True,
                "safe_to_run": True,
                "execution_enabled": False,
                "body_read_allowed": False,
                "network_request_performed": False,
                "authority": "review_only",
                "button_label": label,
                "description": description,
                "preview": {
                    "headline": label,
                    "body": description + " This control is review-only and does not unlock live web, body reads, updates, runtime mutation, package install, browser execution, or command execution.",
                },
                "blocked_authorities": _blocked_authorities(),
            }
        )
    return actions


def _action_registry_payload() -> dict[str, Any]:
    actions = _operator_actions()
    return {
        "ok": True,
        "status": "ready",
        "ready": True,
        "registered": True,
        "operator_triggered_only": True,
        "generated_at": _utc_now(),
        "action_count": len(actions),
        "actions_count": len(actions),
        "count": len(actions),
        "total_actions": len(actions),
        "registered_actions": len(actions),
        "available_actions": len(actions),
        "button_count": len(actions),
        "actions_available": True,
        "empty_state": False,
        "unlock_allowed": False,
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "body_reads_allowed": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "actions": actions,
        "registry": actions,
        "operator_actions": actions,
        "blocked_authorities": _blocked_authorities(),
        "authority": _authority_state(),
        "chip": {"label": "Actions", "value": len(actions), "status": "ready"},
        "visual_contract": {
            "unlock_allowed": False,
            "actions_chip_should_be_greater_than_zero": True,
            "actions_tab_should_show_controls": True,
            "uses_user_facing_labels": True,
            "dev_stage_grid": False,
            "preview_panes_required": True,
        },
        "ui": {
            "surface": "operator_console",
            "developer_stage_labels_allowed": False,
            "preferred_card_style": "user_facing_operator_controls",
            "empty_state": "Governed actions registered",
        },
    }


def _action_summary_payload() -> dict[str, Any]:
    registry = _action_registry_payload()
    return {
        "ok": True,
        "status": "ready",
        "ready": True,
        "registered": True,
        "generated_at": _utc_now(),
        "count": registry["action_count"],
        "action_count": registry["action_count"],
        "actions_count": registry["action_count"],
        "button_count": registry["action_count"],
        "actions_available": True,
        "available_actions": registry["action_count"],
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "blocked_authorities": _blocked_authorities(),
        "authority": _authority_state(),
        "chip": {"label": "Actions", "value": registry["action_count"], "status": "ready"},
    }


def _action_preview_payload(action_key: str) -> dict[str, Any]:
    actions = _operator_actions()
    selected = next(
        (
            action
            for action in actions
            if action["action_key"] == action_key
            or action["id"] == action_key
            or action["key"] == action_key
            or action["label"] == action_key
        ),
        None,
    )
    if selected is None:
        return {
            "ok": False,
            "status": "unknown_action",
            "action_key": action_key,
            "execution_enabled": False,
            "network_request_performed": False,
            "body_read_allowed": False,
            "blocked_authorities": _blocked_authorities(),
            "available_actions": [action["action_key"] for action in actions],
        }
    return {
        "ok": True,
        "status": "preview_ready",
        "ready": True,
        "registered": True,
        "action_key": selected["action_key"],
        "action": selected,
        "preview": selected["preview"],
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "blocked_authorities": _blocked_authorities(),
        "authority": _authority_state(),
    }


def _lifecycle_stages() -> list[dict[str, Any]]:
    names = [
        "Signal Ingestion", "Signal Normalization", "Source Validation & Weighting",
        "Context Expansion", "Signal Consolidation", "Entity Extraction",
        "Relationship Mapping", "Trend Discovery", "Cluster Formation",
        "Insight/Thesis Structuring", "Gap Detection", "Gap Qualification",
        "Discovery Generation", "Breakthrough Identification & Classification",
        "Advancement Path Selection", "Auto Invention/Solution Generation",
        "Solution Structuring", "Buildability Assessment", "Viability Assessment",
        "Manufacturability/Deployability Assessment", "Feasibility Validation",
        "Design Portal Output/Blueprints/Specs", "Market Positioning",
        "Moat & Differentiation", "Business Model & Value Capture",
        "Competitor Analysis", "Portfolio Creation/Optimization",
        "Acquirer Identification", "Acquisition Fit & Rationale",
        "Final Package Construction",
    ]
    return [
        {"stage": i, "id": f"stage_{i:02d}", "name": name, "status": "ready" if i <= 15 else "route_gated"}
        for i, name in enumerate(names, start=1)
    ]


def _end_state_alignment_contract() -> dict[str, Any]:
    return {
        "contract_id": "platform_end_state_alignment_v1",
        "backend_owns_truth": True,
        "docs_source": "uploaded end-state architecture and pipeline corpus",
        "system_identity": {
            "root_function": "governed_signal_governance_and_trend_discovery",
            "product_center": "canonical_lifecycle_runtime",
            "operator_surface_role": "command_observe_review_approve_validate_inspect",
            "not_primary_role": "generic_ai_app_or_invention_first_dashboard",
        },
        "operating_model": {
            "default_path": [
                "signal_governance",
                "trend_discovery",
                "thesis_formation",
                "portfolio_creation_optimization",
            ],
            "breakthrough_path": "conditional_governed_escalation",
            "invention_path": "route_dependent_after_qualification",
            "acquisition_path": "downstream_package_after_portfolio_and_fit_validation",
        },
        "route_policy": {
            "breakthrough_is_default": False,
            "portfolio_is_normal_early_path": True,
            "operator_review_required_for_escalation": True,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "live_web_execution_allowed_by_default": False,
        },
        "runtime_spine": {
            "stage_count": 30,
            "root_stages": [1, 2, 3, 4, 5, 8, 10, 27],
            "conditional_escalation_stages": [14, 15, 16, 17, 18, 20, 21, 22],
            "final_package_stages": [28, 29, 30],
        },
        "next_forward_motion": [
            "keep canonical startup locked to runtime_core.app:create_app",
            "keep dashboard payload backend-owned",
            "bind cockpit panels to lifecycle and route-governance truth",
            "prove signal-to-portfolio flow before widening invention or live-web authority",
        ],
    }


def _call_no_arg_payload(func: Any) -> dict[str, Any] | None:
    try:
        sig = inspect.signature(func)
        required = [
            p for p in sig.parameters.values()
            if p.default is inspect._empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        if required:
            return None
        value = func()
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _existing_dashboard_payload() -> dict[str, Any]:
    candidates = [
        ("runtime_core.api.dashboard_payload_bridge", ["get_dashboard_payload", "build_dashboard_payload", "dashboard_payload", "get_payload", "build_payload"]),
        ("runtime_core.api.governed_dashboard_payload_bridge", ["get_dashboard_payload", "build_dashboard_payload", "dashboard_payload", "get_payload", "build_payload"]),
    ]
    for module_name, names in candidates:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for name in names:
            func = getattr(module, name, None)
            if callable(func):
                payload = _call_no_arg_payload(func)
                if payload is not None:
                    return payload
    return {"ok": True, "status": "ok", "version": APP_VERSION}


def _dashboard_payload() -> dict[str, Any]:
    payload = dict(_existing_dashboard_payload())
    try:
        from runtime_core.platform.update_governance.open_web_update_governance import build_dashboard_update_panel

        update_panel = build_dashboard_update_panel(PROJECT_ROOT)
    except Exception:
        update_panel = {
            "panel_key": "open_web_update_governance",
            "status": "unavailable",
            "available_updates": [],
            "security_posture": {
                "automatic_updates_enabled": False,
                "privileged_surfaces_exposed": False,
                "runtime_truth_firewall": "enabled",
            },
        }
    registry = _action_registry_payload()
    count = registry["action_count"]
    payload.setdefault("ok", True)
    payload.setdefault("status", "ok")
    payload.setdefault("payload_status", "ok")
    payload.setdefault("version", APP_VERSION)
    payload["generated_at"] = _utc_now()
    payload["readiness"] = payload.get("readiness", "governed_internet_update_ready")
    payload["authority"] = {**_authority_state(), **(payload.get("authority") if isinstance(payload.get("authority"), dict) else {})}
    payload["blocked_authorities"] = _blocked_authorities()
    payload["actions"] = registry
    payload["dashboard_actions"] = registry
    payload["operator_actions"] = registry["actions"]
    payload["actions_summary"] = _action_summary_payload()
    payload["action_count"] = count
    payload["actions_count"] = count
    payload["execution_enabled"] = False
    payload["network_request_performed"] = False
    payload["operator_console"] = {
        "status": "ready",
        "controls": registry["actions"],
        "user_facing": True,
        "dev_stage_grid": False,
        "preview_endpoint": "/dashboard/actions/preview/{action_key}",
    }
    payload["runtime_mutation"] = "blocked"
    payload["body_read"] = "blocked"
    payload["body_reads"] = "blocked"
    payload["end_state_alignment"] = _end_state_alignment_contract()
    payload["system_identity"] = payload["end_state_alignment"]["system_identity"]
    payload["operating_model"] = payload["end_state_alignment"]["operating_model"]
    payload["route_policy"] = payload["end_state_alignment"]["route_policy"]
    payload["runtime_focus"] = payload["system_identity"]["root_function"]
    payload["update_governance_panel"] = update_panel
    payload["update_governance"] = {
        "status": update_panel.get("status"),
        "automatic_updates_enabled": False,
        "approval_required": True,
        "available_update_count": len(update_panel.get("available_updates", [])) if isinstance(update_panel.get("available_updates"), list) else 0,
        "runtime_truth_firewall": update_panel.get("security_posture", {}).get("runtime_truth_firewall", "enabled"),
    }

    chips = payload.get("chips")
    if not isinstance(chips, list):
        chips = []
    chips = [chip for chip in chips if not (isinstance(chip, dict) and chip.get("label") == "Actions")]
    chips.append({"label": "Actions", "value": count, "status": "ready"})
    payload["chips"] = chips

    panels = payload.get("panels")
    if not isinstance(panels, list):
        panels = []
    if not any(isinstance(panel, dict) and panel.get("id") == "actions" for panel in panels):
        panels.append({"id": "actions", "title": "Actions", "status": "ready"})
    if not any(isinstance(panel, dict) and panel.get("id") == "update_governance" for panel in panels):
        panels.append({"id": "update_governance", "title": "Update Governance", "status": update_panel.get("status", "ready")})
    payload["panels"] = panels

    lifecycle = payload.get("lifecycle")
    if not isinstance(lifecycle, dict):
        payload["lifecycle"] = {"stage_count": 30, "stages": _lifecycle_stages()}
    else:
        lifecycle.setdefault("stage_count", 30)
        lifecycle.setdefault("stages", _lifecycle_stages())

    return payload


def _probe_status_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "registered": True,
        "operator_triggered_only": True,
        "one_shot_only": True,
        "method_allowed": "HEAD",
        "unlock_allowed": False,
        "status": "registered",
        "ready": False,
        "generated_at": _utc_now(),
        "metadata_only": True,
        "execution_enabled": False,
        "live_probe_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "body_reads_allowed": False,
        "body_reads_enabled": False,
        "body_read_performed": False,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_mutation_performed": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_allowed": False,
        "autonomous_execution_allowed": False,
        "autonomous_crawling_allowed": False,
        "browser_execution_allowed": False,
        "continuous_crawling_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "expected_status_route": "/api/governed/live-probe/status",
        "expected_head_route": "/api/governed/live-probe/head",
        "message": "Governed live probe endpoint is registered and blocked by default. No network, browser, body read, update, or runtime mutation authority is granted.",
    }


def _head_probe_response(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    operator_ack = payload.get("operator_ack")
    if isinstance(operator_ack, str):
        operator_ack = operator_ack.strip().upper() in {"YES", "TRUE", "1"}
    one_shot = payload.get("one_shot")
    if isinstance(one_shot, str):
        one_shot = one_shot.strip().lower() in {"true", "1", "yes"}

    base = _probe_status_payload()
    base.update(
        {
            "status": "blocked",
            "url": payload.get("url"),
            "operator_ack": bool(operator_ack),
            "one_shot": bool(one_shot),
            "live_probe_executed": False,
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
        }
    )

    if not _env_true("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE") or not _env_true("PLATFORM_ALLOW_HEAD_ONLY_PROBE"):
        base["reason"] = "provider gate is disabled"
        base["message"] = "provider gate is disabled"
        return base, 403
    if _env_true("PLATFORM_ALLOW_RESPONSE_BODY_READ"):
        base["reason"] = "Body read authority is blocked"
        base["message"] = "Body read authority is blocked"
        return base, 403
    if _env_true("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION"):
        base["reason"] = "Runtime truth mutation authority is blocked"
        base["message"] = "Runtime truth mutation authority is blocked"
        return base, 403
    if _env_true("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION"):
        base["reason"] = "Autonomous execution authority is blocked"
        base["message"] = "Autonomous execution authority is blocked"
        return base, 403
    if not operator_ack:
        base["reason"] = "Operator acknowledgement required"
        base["message"] = "Operator acknowledgement required"
        return base, 403
    if not one_shot:
        base["reason"] = "Only one-shot execution is allowed"
        base["message"] = "Only one-shot execution is allowed"
        return base, 403

    base["status"] = "ready_for_operator_one_shot_metadata_probe"
    base["ready"] = True
    base["reason"] = "local contract accepted without executing network probe"
    base["message"] = "local contract accepted without executing network probe"
    return base, 200


def _include_router_once(app: FastAPI, router: APIRouter, included: set[int]) -> bool:
    if id(router) in included:
        return False
    try:
        app.include_router(router)
        included.add(id(router))
        return True
    except Exception:
        return False


def _call_include_function(app: FastAPI, func: Any) -> bool:
    try:
        sig = inspect.signature(func)
        required = [
            p for p in sig.parameters.values()
            if p.default is inspect._empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        if len(required) > 1:
            return False
        result = func(app)
        return result is not False
    except Exception:
        return False


def _include_discovered_routes(app: FastAPI) -> dict[str, Any]:
    included: set[int] = set()
    report: dict[str, Any] = {
        "mode": "canonical_manifest",
        "included_modules": [],
        "included_routers": [],
        "included_functions": [],
        "skipped_modules": [],
    }
    try:
        from runtime_core.api.canonical_route_manifest import CANONICAL_ROUTE_MODULES, LEGACY_ROUTE_MODULES

        module_names = list(CANONICAL_ROUTE_MODULES)
        if _env_true("PLATFORM_ENABLE_LEGACY_ROUTE_DISCOVERY"):
            report["mode"] = "canonical_manifest_plus_legacy_discovery"
            module_names.extend(LEGACY_ROUTE_MODULES)
            try:
                import runtime_core.api as runtime_core_api
                for info in pkgutil.iter_modules(runtime_core_api.__path__, runtime_core_api.__name__ + "."):
                    module_names.append(info.name)
            except Exception as exc:
                report["skipped_modules"].append({"module": "runtime_core.api", "reason": str(exc)})
    except Exception as exc:
        report["mode"] = "fallback_minimal_manifest"
        report["skipped_modules"].append({"module": "runtime_core.api.canonical_route_manifest", "reason": str(exc)})
        module_names = [
            "runtime_core.api.routes_pipeline",
            "runtime_core.api.routes_continuous_runtime",
            "runtime_core.api.operator_cockpit_runtime",
            "runtime_core.api.routes_operational_control_plane",
        ]

    for module_name in list(dict.fromkeys(module_names)):
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            report["skipped_modules"].append({"module": module_name, "reason": str(exc)})
            continue
        included_any = False
        for attr in ("router", "api_router", "dashboard_router"):
            router = getattr(module, attr, None)
            if isinstance(router, APIRouter) and _include_router_once(app, router, included):
                included_any = True
                report["included_routers"].append(f"{module_name}.{attr}")
        for attr in dir(module):
            if attr.startswith("include_") and attr.endswith("_routes"):
                func = getattr(module, attr, None)
                if callable(func) and _call_include_function(app, func):
                    included_any = True
                    report["included_functions"].append(f"{module_name}.{attr}")
        if included_any:
            report["included_modules"].append(module_name)
    return report


def _install_cockpit_registry_routes(app: FastAPI) -> None:
    for module_name, function_name in (
        ("runtime_core.api.canonical_cockpit_surface_registry", "register_cockpit_surface_registry_routes"),
        ("runtime_core.api.canonical_cockpit_surface_health", "register_surface_health_routes"),
    ):
        try:
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            _call_include_function(app, func)
        except Exception as exc:
            setattr(
                app.state,
                f"claire_{function_name}_mount_error",
                f"{type(exc).__name__}: {exc}",
            )


def _prune_duplicate_routes(app: FastAPI) -> None:
    seen: set[tuple[str, tuple[str, ...]]] = set()
    pruned: list[dict[str, Any]] = []
    kept_routes = []
    for route in app.router.routes:
        path = getattr(route, "path", "")
        methods = tuple(sorted(getattr(route, "methods", []) or []))
        if not path or not methods:
            kept_routes.append(route)
            continue
        key = (path, methods)
        if key in seen:
            endpoint = getattr(route, "endpoint", None)
            pruned.append(
                {
                    "path": path,
                    "methods": list(methods),
                    "name": getattr(route, "name", ""),
                    "module": getattr(endpoint, "__module__", ""),
                    "endpoint": getattr(endpoint, "__name__", ""),
                }
            )
            continue
        seen.add(key)
        kept_routes.append(route)
    app.router.routes = kept_routes
    app.state.claire_duplicate_routes_pruned = pruned
    app.state.claire_duplicate_routes_pruned_count = len(pruned)


def _remove_legacy_dashboard_routes(app: FastAPI) -> None:
    legacy_paths = {
        "/dashboard/final",
        "/dashboard/v3",
        "/operator-dashboard",
        "/operator-cockpit",
        "/command-center",
    }
    removed: list[dict[str, Any]] = []
    kept_routes = []
    for route in app.router.routes:
        path = getattr(route, "path", "")
        methods = set(getattr(route, "methods", []) or [])
        if path in legacy_paths and "GET" in methods:
            endpoint = getattr(route, "endpoint", None)
            removed.append(
                {
                    "path": path,
                    "methods": sorted(methods),
                    "name": getattr(route, "name", ""),
                    "module": getattr(endpoint, "__module__", ""),
                    "endpoint": getattr(endpoint, "__name__", ""),
                }
            )
            continue
        kept_routes.append(route)
    app.router.routes = kept_routes
    app.state.claire_legacy_dashboard_routes_removed = removed
    app.state.claire_legacy_dashboard_routes_removed_count = len(removed)


def _install_priority_routes(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    def root() -> dict[str, Any]:
        return {"ok": True, "status": "ok", "service": "Governed Intelligence Platform", "version": APP_VERSION}

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<rect width="64" height="64" rx="12" fill="#0c0f12"/>'
            '<path d="M14 40 25 18l8 16 6-10 11 22H14Z" fill="#88d8a4"/>'
            '<circle cx="46" cy="18" r="5" fill="#77b8ff"/>'
            "</svg>"
        )
        return Response(content=svg, media_type="image/svg+xml")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "status": "ok", "version": APP_VERSION}

    def _serve_canonical_dashboard() -> HTMLResponse:
        if not os.path.exists(CANONICAL_DASHBOARD_HTML):
            return HTMLResponse(
                "<!doctype html><title>Dashboard Missing</title><h1>Dashboard asset missing</h1>",
                status_code=500,
            )
        with open(CANONICAL_DASHBOARD_HTML, "r", encoding="utf-8") as handle:
            html = handle.read()
        return HTMLResponse(html, headers={"Cache-Control": "no-store"})

    @app.get("/dashboard", include_in_schema=False)
    def canonical_dashboard() -> HTMLResponse:
        return _serve_canonical_dashboard()

    @app.get("/dashboard/local", include_in_schema=False)
    def local_dashboard_alias() -> HTMLResponse:
        return _serve_canonical_dashboard()

    @app.get("/dashboard/assets/{asset_name}", include_in_schema=False)
    def canonical_dashboard_asset(asset_name: str) -> FileResponse:
        asset = CANONICAL_DASHBOARD_ASSETS.get(asset_name)
        if asset is None:
            return Response("Dashboard asset not found", status_code=404)
        media_type, path = asset
        if not os.path.exists(path):
            return Response("Dashboard asset not found", status_code=404)
        return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-store"})

    @app.get("/platform_dashboard.css", include_in_schema=False)
    def canonical_dashboard_root_css() -> FileResponse:
        media_type, path = CANONICAL_DASHBOARD_ASSETS["platform_dashboard.css"]
        return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-store"})

    @app.get("/platform_dashboard.js", include_in_schema=False)
    def canonical_dashboard_root_js() -> FileResponse:
        media_type, path = CANONICAL_DASHBOARD_ASSETS["platform_dashboard.js"]
        return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-store"})

    @app.get("/api/platform/dashboard-config")
    def platform_dashboard_config() -> dict[str, Any]:
        return {
            "ok": True,
            "status": "ready",
            "dashboard_mode": "local_canonical_primary",
            "uploaded_dashboard_url": None,
            "primary_dashboard_url": "/dashboard",
            "local_dashboard_url": "/dashboard/local",
            "local_api_base": "http://127.0.0.1:8000",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "launcher_opens_uploaded_dashboard": False,
            "launcher_opens_canonical_dashboard": True,
            "mixed_content_risk": False,
            "required_bridge": "same-origin local dashboard may call governed local API routes directly",
        }

    def _cockpit_dashboard_state_payload() -> dict[str, Any]:
        from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state

        return build_cockpit_dashboard_state()

    @app.get("/api/dashboard/state")
    def api_cockpit_dashboard_state() -> dict[str, Any]:
        return _cockpit_dashboard_state_payload()

    @app.get("/dashboard/state")
    def cockpit_dashboard_state() -> dict[str, Any]:
        return _cockpit_dashboard_state_payload()

    @app.get("/operator/dashboard/state")
    def operator_cockpit_dashboard_state() -> dict[str, Any]:
        return _cockpit_dashboard_state_payload()

    @app.post("/api/cockpit/command/plan")
    async def cockpit_command_plan(request: Request) -> dict[str, Any]:
        from runtime_core.dashboard.cockpit_command_plan import (
            build_cockpit_command_plan,
            persist_latest_command_plan,
        )

        body = await request.json()
        query = str(body.get("query") or body.get("command") or "").strip() if isinstance(body, dict) else ""
        if isinstance(body, dict) and body.get("intent") == "design_portal_action":
            from runtime_core.design.artifact_package import execute_design_portal_action

            action_id = str(body.get("action_id") or query or "").strip()
            operator_note = str(body.get("operator_note") or "").strip()
            return execute_design_portal_action(action_id=action_id, operator_note=operator_note)
        payload = build_cockpit_command_plan(query)
        persist_latest_command_plan(payload)
        return payload

    @app.get("/api/cockpit/command/latest")
    def cockpit_command_latest() -> dict[str, Any]:
        latest_path = os.path.join(os.getcwd(), "data", "operator", "search_command", "latest_command_plan.json")
        if not os.path.exists(latest_path):
            return {"schema_version": "v19.89.8_cockpit_command_plan", "status": "empty", "query": ""}
        with open(latest_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    @app.get("/api/cockpit/command/history")
    def cockpit_command_history(limit: int = 12) -> dict[str, Any]:
        from runtime_core.dashboard.cockpit_command_plan import command_history

        return command_history(limit=limit)

    @app.get("/dashboard/actions/registry")
    def dashboard_actions_registry() -> dict[str, Any]:
        return _action_registry_payload()

    @app.get("/api/dashboard/actions/registry")
    def api_dashboard_actions_registry() -> dict[str, Any]:
        return _action_registry_payload()

    @app.get("/dashboard/actions/summary")
    def dashboard_actions_summary() -> dict[str, Any]:
        return _action_summary_payload()

    @app.get("/api/dashboard/actions/summary")
    def api_dashboard_actions_summary() -> dict[str, Any]:
        return _action_summary_payload()

    @app.get("/dashboard/actions/preview/{action_key}")
    def dashboard_actions_preview(action_key: str) -> dict[str, Any]:
        return _action_preview_payload(action_key)

    @app.get("/api/dashboard/actions/preview/{action_key}")
    def api_dashboard_actions_preview(action_key: str) -> dict[str, Any]:
        return _action_preview_payload(action_key)

    @app.get("/dashboard/payload")
    def dashboard_payload() -> dict[str, Any]:
        return _dashboard_payload()

    @app.get("/dashboard/payload/status")
    def dashboard_payload_status() -> dict[str, Any]:
        payload = _dashboard_payload()
        return {
            "ok": True,
            "status": "ok",
            "version": APP_VERSION,
            "generated_at": _utc_now(),
            "route_report": getattr(app.state, "claire_route_report", {}),
            "stage_count": payload.get("lifecycle", {}).get("stage_count", 30) if isinstance(payload.get("lifecycle"), dict) else 30,
            "panel_count": len(payload.get("panels", [])) if isinstance(payload.get("panels"), list) else 0,
            "action_count": payload.get("action_count", 0),
            "actions_count": payload.get("actions_count", 0),
            "actions": payload.get("actions", {}),
        }

    @app.get("/api/governed/live-probe/status")
    def governed_live_probe_status() -> dict[str, Any]:
        return _probe_status_payload()

    @app.post("/api/governed/live-probe/head")
    async def governed_live_probe_head(request: Request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        payload, status_code = _head_probe_response(body if isinstance(body, dict) else {})
        return JSONResponse(payload, status_code=status_code)

    @app.post("/evaluate")
    async def evaluate(request: Request) -> dict[str, Any]:
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict):
            body = {"raw_input": str(body)}
        raw_input = body.get("raw_input") or body.get("query") or body.get("text") or body.get("input") or ""
        from runtime_core.api.routes_pipeline import EvaluateRequest, _evaluate_impl

        req = EvaluateRequest(
            raw_input=str(raw_input),
            mode=str(body.get("mode") or "deterministic"),
            source_mode=str(body.get("source_mode") or "simulated_live_packet"),
            sources=body.get("sources") if isinstance(body.get("sources"), dict) else {},
        )
        return await _evaluate_impl(req)


def create_app() -> FastAPI:
    app = FastAPI(title="Governed Intelligence Platform", version=APP_VERSION, docs_url="/docs", redoc_url="/redoc")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _install_priority_routes(app)
    app.state.claire_route_report = _include_discovered_routes(app)
    _install_cockpit_registry_routes(app)
    try:
        from runtime_core.api.routes_operational_control_plane import include_operational_control_plane_routes

        include_operational_control_plane_routes(app)
    except Exception as exc:
        app.state.claire_operational_control_plane_mount_error = f"{type(exc).__name__}: {exc}"
    # Direct create_app audit route mount repair
    # Exact repair for failing tests:
    # - /api/audit/risk-pattern-review
    # - /dashboard/audit/risk-pattern-review
    # - /api/audit/plateau-lock
    # - /dashboard/audit/plateau-lock
    # Read-only only. No execution/web/body-read/runtime-mutation authority is enabled.
    try:
        from runtime_core.audit.risk_pattern_governance_review import build_risk_pattern_review

        def _claire_s1294_risk_pattern_review_payload() -> dict:
            return build_risk_pattern_review()

        app.add_api_route(
            "/api/audit/risk-pattern-review",
            _claire_s1294_risk_pattern_review_payload,
            methods=["GET"],
            name="api_audit_risk_pattern_review_s1294",
        )
        app.add_api_route(
            "/dashboard/audit/risk-pattern-review",
            _claire_s1294_risk_pattern_review_payload,
            methods=["GET"],
            name="dashboard_audit_risk_pattern_review_s1294",
        )
    except Exception as exc:
        app.state.claire_s1294_risk_pattern_review_mount_error = f"{type(exc).__name__}: {exc}"

    try:
        from runtime_core.audit.plateau_completion_lock import build_plateau_completion_lock

        def _claire_s1294_plateau_lock_payload() -> dict:
            return build_plateau_completion_lock(write_audit_report=False)

        app.add_api_route(
            "/api/audit/plateau-lock",
            _claire_s1294_plateau_lock_payload,
            methods=["GET"],
            name="api_audit_plateau_lock_s1294",
        )
        app.add_api_route(
            "/dashboard/audit/plateau-lock",
            _claire_s1294_plateau_lock_payload,
            methods=["GET"],
            name="dashboard_audit_plateau_lock_s1294",
        )
    except Exception as exc:
        app.state.claire_s1294_plateau_lock_mount_error = f"{type(exc).__name__}: {exc}"

    # Active control map route mount
    # Mounts the real dashboard active-control map. Read-only/review-only controls only.
    try:
        from runtime_core.api.dashboard_active_control_map import build_dashboard_active_control_map

        def _claire_s1323_active_control_map_payload() -> dict:
            return build_dashboard_active_control_map()

        app.add_api_route(
            "/api/dashboard/active-control-map",
            _claire_s1323_active_control_map_payload,
            methods=["GET"],
            name="api_dashboard_active_control_map_s1323",
        )
        app.add_api_route(
            "/dashboard/active-control-map",
            _claire_s1323_active_control_map_payload,
            methods=["GET"],
            name="dashboard_active_control_map_s1323",
        )
    except Exception as exc:
        app.state.claire_s1323_active_control_map_mount_error = f"{type(exc).__name__}: {exc}"

    _remove_legacy_dashboard_routes(app)
    _prune_duplicate_routes(app)



    return app


app = create_app()
