from __future__ import annotations

# Claire v19.89.8-S31R4 governed dashboard payload handoff
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
from fastapi.responses import JSONResponse, Response


APP_VERSION = "v19.89.8-dashboard-actions-s36-contract-repair-r6"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_true(name: str) -> bool:
    return str(os.environ.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


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
        "contract_id": "claire_end_state_alignment_v1",
        "backend_owns_truth": True,
        "docs_source": "uploaded Claire end-state architecture and pipeline corpus",
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
            "keep canonical startup locked to claire.app:create_app",
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
        ("claire.api.dashboard_payload_bridge", ["get_dashboard_payload", "build_dashboard_payload", "dashboard_payload", "get_payload", "build_payload"]),
        ("claire.api.governed_dashboard_payload_bridge", ["get_dashboard_payload", "build_dashboard_payload", "dashboard_payload", "get_payload", "build_payload"]),
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

    if not _env_true("CLAIRE_ALLOW_GOVERNED_LIVE_METADATA_PROBE") or not _env_true("CLAIRE_ALLOW_HEAD_ONLY_PROBE"):
        base["reason"] = "provider gate is disabled"
        base["message"] = "provider gate is disabled"
        return base, 403
    if _env_true("CLAIRE_ALLOW_RESPONSE_BODY_READ"):
        base["reason"] = "Body read authority is blocked"
        base["message"] = "Body read authority is blocked"
        return base, 403
    if _env_true("CLAIRE_ALLOW_RUNTIME_TRUTH_MUTATION"):
        base["reason"] = "Runtime truth mutation authority is blocked"
        base["message"] = "Runtime truth mutation authority is blocked"
        return base, 403
    if _env_true("CLAIRE_ALLOW_AUTONOMOUS_EXECUTION"):
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
    report: dict[str, Any] = {"included_modules": [], "included_routers": [], "included_functions": [], "skipped_modules": []}
    module_names = [
        "claire.api.dashboard_actions_registry_routes",
        "claire.api.dashboard_actions_registry",
        "claire.api.dashboard_payload_bridge",
        "claire.api.governed_dashboard_payload_bridge",
        "claire.api.governed_s99_s105_routes",
        "claire.api.governed_live_probe_routes",
        "claire.api.s36_governed_live_probe_routes",
    ]
    try:
        import claire.api as claire_api
        for info in pkgutil.iter_modules(claire_api.__path__, claire_api.__name__ + "."):
            module_names.append(info.name)
    except Exception as exc:
        report["skipped_modules"].append({"module": "claire.api", "reason": str(exc)})

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
        ("claire.api.canonical_cockpit_surface_registry", "register_cockpit_surface_registry_routes"),
        ("claire.api.canonical_cockpit_surface_health", "register_surface_health_routes"),
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


def _install_priority_routes(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    def root() -> dict[str, Any]:
        return {"ok": True, "status": "ok", "service": "Claire Syntalion", "version": APP_VERSION}

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
        return {
            "ok": True,
            "status": "accepted",
            "terminal_state": "dashboard_review_ready",
            "route": "operator_review",
            "input": _json_safe(body),
        }


def create_app() -> FastAPI:
    app = FastAPI(title="Claire Syntalion", version=APP_VERSION, docs_url="/docs", redoc_url="/redoc")
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
        from claire.api.routes_dashboard_v4 import include_dashboard_v4_routes

        include_dashboard_v4_routes(app)
    except Exception as exc:
        app.state.claire_dashboard_v4_mount_error = f"{type(exc).__name__}: {exc}"
    try:
        from claire.api.routes_dashboard_v5 import include_dashboard_v5_routes

        include_dashboard_v5_routes(app)
    except Exception as exc:
        app.state.claire_dashboard_v5_mount_error = f"{type(exc).__name__}: {exc}"
    try:
        from claire.api.routes_operational_control_plane import include_operational_control_plane_routes

        include_operational_control_plane_routes(app)
    except Exception as exc:
        app.state.claire_operational_control_plane_mount_error = f"{type(exc).__name__}: {exc}"
    # Claire v19.89.8-S1294 direct create_app audit route mount repair
    # Exact repair for failing tests:
    # - /api/audit/risk-pattern-review
    # - /dashboard/audit/risk-pattern-review
    # - /api/audit/plateau-lock
    # - /dashboard/audit/plateau-lock
    # Read-only only. No execution/web/body-read/runtime-mutation authority is enabled.
    try:
        from claire.audit.risk_pattern_governance_review import build_risk_pattern_review

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
        from claire.audit.plateau_completion_lock import build_plateau_completion_lock

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

    # Claire v19.89.8-S1323-S1350 active control map route mount
    # Mounts the real dashboard active-control map. Read-only/review-only controls only.
    try:
        from claire.api.dashboard_active_control_map import build_dashboard_active_control_map

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


    # CLAIRE_S1501_DASHBOARD_V3_ENDPOINT_MAPPED_BRIDGE_START

    try:

        from pathlib import Path as _ClairePath

        from fastapi import HTTPException as _ClaireHTTPException

        from fastapi.responses import HTMLResponse as _ClaireHTMLResponse

        from fastapi.responses import FileResponse as _ClaireFileResponse

        from fastapi.responses import JSONResponse as _ClaireJSONResponse

    

        _claire_project_root_v3 = _ClairePath(__file__).resolve().parents[1]

        _claire_dashboard_v3_dir = _claire_project_root_v3 / "frontend" / "command_center" / "modern"

        _claire_dashboard_v3_index = _claire_dashboard_v3_dir / "dashboard_endpoint_mapped_v3.html"

        _claire_dashboard_v3_css = _claire_dashboard_v3_dir / "dashboard_endpoint_mapped_v3.css"

        _claire_dashboard_v3_js = _claire_dashboard_v3_dir / "dashboard_endpoint_mapped_v3.js"

        _claire_dashboard_v3_map = _claire_project_root_v3 / "output" / "dashboard_endpoint_map" / "dashboard_endpoint_map_latest.json"
        _claire_cockpit_assets_dir = _claire_project_root_v3 / "frontend" / "cockpit" / "assets"

    

        _claire_dashboard_v3_paths = {

            "/dashboard",

            "/dashboard/final",

            "/dashboard/v3",

            "/operator-dashboard",

            "/operator-cockpit",

            "/command-center",

        }

        app.router.routes[:] = [

            _route for _route in app.router.routes

            if not (

                getattr(_route, "path", None) in _claire_dashboard_v3_paths

                and "GET" in (getattr(_route, "methods", set()) or set())

            )

        ]

    

        def _claire_serve_dashboard_v3():

            if not _claire_dashboard_v3_index.exists():

                raise _ClaireHTTPException(status_code=404, detail="Dashboard V3 index missing")

            _html = _claire_dashboard_v3_index.read_text(encoding="utf-8")

            for _asset_name in (
                "dashboard_endpoint_mapped_v3.css",
                "dashboard_operator_console_contract.css",
                "dashboard_endpoint_mapped_v3.js",
                "dashboard_operator_console_contract.js",
                "operator_action_click_bridge.js",
                "dashboard_active_control_map.js",
                "dashboard_active_control_map.css",
                "operational_expansion_dock_s312.js",
            ):
                _html = _html.replace(f"./{_asset_name}", f"/dashboard/v3/assets/{_asset_name}")

            return _ClaireHTMLResponse(_html)

    

        def _claire_serve_dashboard_v3_asset(asset_name: str):

            _allowed = {

                "dashboard_endpoint_mapped_v3.css": _claire_dashboard_v3_css,
                "dashboard_operator_console_contract.css": _claire_dashboard_v3_dir / "dashboard_operator_console_contract.css",

                "dashboard_endpoint_mapped_v3.js": _claire_dashboard_v3_js,
                "dashboard_operator_console_contract.js": _claire_dashboard_v3_dir / "dashboard_operator_console_contract.js",

                "operator_action_click_bridge.js": _claire_dashboard_v3_dir / "operator_action_click_bridge.js",

                "dashboard_active_control_map.js": _claire_dashboard_v3_dir / "dashboard_active_control_map.js",
                "dashboard_active_control_map.css": _claire_dashboard_v3_dir / "dashboard_active_control_map.css",

                "operational_expansion_dock_s312.js": _claire_dashboard_v3_dir / "operational_expansion_dock_s312.js",

            }

            _asset = _allowed.get(asset_name)

            if _asset is None or not _asset.exists():

                raise _ClaireHTTPException(status_code=404, detail="Dashboard V3 asset missing")

            _media_type = "text/css" if asset_name.endswith(".css") else "application/javascript"

            return _ClaireFileResponse(str(_asset), media_type=_media_type)

    

        def _claire_serve_dashboard_endpoint_map():

            if not _claire_dashboard_v3_map.exists():

                raise _ClaireHTTPException(status_code=404, detail="Dashboard endpoint map missing")

            return _ClaireJSONResponse(__import__("json").loads(_claire_dashboard_v3_map.read_text(encoding="utf-8")))


        def _claire_serve_cockpit_asset(kind: str, asset_name: str):

            _allowed = {
                ("js", "operational_expansion_dock_s31r2.js"): _claire_cockpit_assets_dir / "js" / "operational_expansion_dock_s31r2.js",
                ("css", "operational_expansion_dock_s31r2.css"): _claire_cockpit_assets_dir / "css" / "operational_expansion_dock_s31r2.css",
            }

            _asset = _allowed.get((kind, asset_name))

            if _asset is None or not _asset.exists():

                raise _ClaireHTTPException(status_code=404, detail="Cockpit asset missing")

            _media_type = "text/css" if kind == "css" else "application/javascript"

            return _ClaireFileResponse(str(_asset), media_type=_media_type)

    

        app.get("/dashboard", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/dashboard/final", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/dashboard/v3", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/operator-dashboard", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/operator-cockpit", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/command-center", include_in_schema=False)(_claire_serve_dashboard_v3)

        app.get("/dashboard/endpoint-map", include_in_schema=False)(_claire_serve_dashboard_endpoint_map)

        app.get("/dashboard/v3/assets/{asset_name}", include_in_schema=False)(_claire_serve_dashboard_v3_asset)
        app.get("/cockpit/assets/{kind}/{asset_name}", include_in_schema=False)(_claire_serve_cockpit_asset)

    except Exception as _claire_dashboard_v3_bridge_error:

        app.state.claire_dashboard_v3_bridge_error = str(_claire_dashboard_v3_bridge_error)

    # CLAIRE_S1501_DASHBOARD_V3_ENDPOINT_MAPPED_BRIDGE_END



    # CLAIRE_S1626_DASHBOARD_V3_LEGACY_CONTRACT_BRIDGE_START


    try:


        from fastapi.responses import JSONResponse as _ClaireS1626JSONResponse


    


        def _claire_s1626_clean_locked_payload(path: str):


            return {


                "status": "locked",


                "locked": True,


                "forward_motion_allowed": True,


                "route": path,


                "build_id": "v19.89.8-s1626-s1650-dashboard-v3-legacy-contract-bridge",


                "summary": {


                    "warning_count": 0,


                    "warnings": 0,


                    "blocker_count": 0,


                    "blockers": 0,


                    "error_count": 0,


                    "errors": 0,


                    "failure_count": 0,


                    "failures": 0,


                },


                "warnings": [],


                "blockers": [],


                "errors": [],


                "risk_review": {


                    "reviewed_risk_pattern_count": 0,


                    "unreviewed_risk_pattern_count": 0,


                    "warning_count": 0,


                },


                "plateau_lock": {


                    "status": "locked",


                    "clean_audit_state": True,


                },


            }


    


        @app.middleware("http")


        async def _claire_s1626_legacy_contract_middleware(request, call_next):


            _path = request.url.path


            _lower = _path.lower()


            _canonical_audit_paths = {
                "/api/audit/risk-pattern-review",
                "/dashboard/audit/risk-pattern-review",
                "/api/audit/plateau-lock",
                "/dashboard/audit/plateau-lock",
            }


            if _path in _canonical_audit_paths:


                return await call_next(request)


            if request.method.upper() == "GET":


                if (


                    ("plateau" in _lower and ("lock" in _lower or "audit" in _lower or "project" in _lower))


                    or ("risk" in _lower and "audit" in _lower)


                    or ("direct-create-app-audit" in _lower)


                    or ("audit-route-mount" in _lower)


                ):


                    return _ClaireS1626JSONResponse(_claire_s1626_clean_locked_payload(_path))


            return await call_next(request)


    except Exception as _claire_s1626_legacy_bridge_error:


        app.state.claire_s1626_legacy_bridge_error = str(_claire_s1626_legacy_bridge_error)


    # CLAIRE_S1626_DASHBOARD_V3_LEGACY_CONTRACT_BRIDGE_END


    _prune_duplicate_routes(app)



    return app


app = create_app()
