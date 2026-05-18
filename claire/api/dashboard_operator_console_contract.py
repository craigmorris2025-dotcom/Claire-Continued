from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter


router = APIRouter(tags=["Dashboard Operator Console Contract"])


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_authority() -> dict[str, str]:
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


def _blocked_flags() -> dict[str, bool]:
    return {
        "live_web_execution_enabled": False,
        "search_provider_execution_enabled": False,
        "browser_execution_enabled": False,
        "network_requests_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "body_reads_allowed": False,
        "body_read_performed": False,
        "autonomous_crawling_enabled": False,
        "automatic_updates_enabled": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "package_download_install_enabled": False,
        "command_execution_enabled": False,
        "unlock_allowed": False,
    }


def _load_actions_registry() -> dict[str, Any]:
    try:
        from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry

        payload = build_dashboard_actions_registry()
        if isinstance(payload, dict) and isinstance(payload.get("actions"), list):
            return payload
    except Exception:
        pass

    actions = [
        {
            "id": "plan_search",
            "key": "plan_search",
            "action_key": "plan_search",
            "label": "Plan a governed search",
            "title": "Plan a governed search",
            "description": "Prepare a governed search plan without provider execution.",
            "button_label": "Plan search",
            "status": "ready",
            "enabled": True,
            "safe_to_run": True,
            "execution_enabled": False,
            "body_read_allowed": False,
            "network_request_performed": False,
            "authority": "review_only",
            "preview": {
                "headline": "Plan a governed search",
                "body": "Prepare a governed search plan without provider execution.",
            },
            "blocked_authorities": _blocked_flags(),
        },
        {
            "id": "review_web_readiness",
            "key": "review_web_readiness",
            "action_key": "review_web_readiness",
            "label": "Review Web Readiness",
            "title": "Review Web Readiness",
            "description": "Review governed internet readiness without enabling live web execution.",
            "button_label": "Review readiness",
            "status": "ready",
            "enabled": True,
            "safe_to_run": True,
            "execution_enabled": False,
            "body_read_allowed": False,
            "network_request_performed": False,
            "authority": "review_only",
            "preview": {
                "headline": "Review Web Readiness",
                "body": "Review governed internet readiness without enabling live web execution.",
            },
            "blocked_authorities": _blocked_flags(),
        },
    ]
    return {
        "ok": True,
        "status": "ready",
        "action_count": len(actions),
        "actions": actions,
        "unlock_allowed": False,
        "visual_contract": {
            "actions_tab_should_show_controls": True,
            "actions_chip_should_be_greater_than_zero": True,
            "unlock_allowed": False,
        },
    }


def _normalize_action(action: dict[str, Any], order: int) -> dict[str, Any]:
    label = str(action.get("label") or action.get("title") or action.get("name") or action.get("action_key") or f"Action {order}")
    # The operator console must not display build-stage codes as primary labels.
    if re.fullmatch(r"S\d+(?:[-–]S\d+)?", label.strip(), re.IGNORECASE):
        label = f"Operator action {order}"

    action_key = str(action.get("action_key") or action.get("key") or action.get("id") or f"action_{order}")
    preview = action.get("preview") if isinstance(action.get("preview"), dict) else {}

    return {
        "id": action_key,
        "key": action_key,
        "action_key": action_key,
        "label": label,
        "title": label,
        "description": str(action.get("description") or preview.get("body") or "Review this governed operator action."),
        "button_label": str(action.get("button_label") or label),
        "status": "ready",
        "enabled": bool(action.get("enabled", True)),
        "visible": True,
        "safe_to_run": True,
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "unlock_allowed": False,
        "authority": str(action.get("authority") or "review_only"),
        "preview": {
            "headline": str(preview.get("headline") or label),
            "body": str(preview.get("body") or action.get("description") or "Review-only preview is available."),
        },
        "blocked_authorities": _blocked_flags(),
    }


def build_operator_console_contract() -> dict[str, Any]:
    registry = _load_actions_registry()
    raw_actions = registry.get("actions") if isinstance(registry.get("actions"), list) else []
    controls = [_normalize_action(action, index) for index, action in enumerate(raw_actions, start=1)]
    controls = [control for control in controls if control["visible"]]

    return {
        "ok": True,
        "status": "ready",
        "phase": "S1069-S1096",
        "title": "Operator Console Action Contract Lock",
        "generated_at": _utc_now(),
        "action_count": len(controls),
        "actions_count": len(controls),
        "controls_count": len(controls),
        "unlock_allowed": False,
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "operator_controls": controls,
        "actions": controls,
        "ui_contract": {
            "surface": "operator_console",
            "actions_tab_should_show_controls": True,
            "actions_chip_should_be_greater_than_zero": len(controls) > 0,
            "uses_user_facing_labels": True,
            "dev_stage_grid": False,
            "stage_code_primary_labels_allowed": False,
            "preview_panes_required": True,
            "buttons_are_review_only": True,
            "unlock_allowed": False,
        },
        "visual_contract": {
            "actions_tab_should_show_controls": True,
            "actions_chip_should_be_greater_than_zero": len(controls) > 0,
            "unlock_allowed": False,
            "dev_stage_grid": False,
        },
        "preview_endpoint": "/dashboard/operator-console/preview/{action_key}",
        "fetch_contract": {
            "method": "GET",
            "allowed_methods": ["GET"],
            "forbidden_methods": ["POST", "PUT", "PATCH", "DELETE"],
            "read_only": True,
            "backend_owns_truth": True,
            "cockpit_owns_presentation_only": True,
        },
        "blocked_authority": _blocked_authority(),
        "blocked_authorities": _blocked_flags(),
        "message": "Operator console controls are mounted as review-only, user-facing actions. Unsafe execution authority remains blocked.",
    }


def build_operator_console_summary() -> dict[str, Any]:
    contract = build_operator_console_contract()
    return {
        "ok": True,
        "status": "ready",
        "phase": contract["phase"],
        "generated_at": _utc_now(),
        "action_count": contract["action_count"],
        "actions_count": contract["actions_count"],
        "controls_count": contract["controls_count"],
        "chip": {
            "label": "Actions",
            "value": contract["action_count"],
            "status": "ready" if contract["action_count"] > 0 else "empty",
        },
        "unlock_allowed": False,
        "execution_enabled": False,
        "body_read_allowed": False,
        "network_request_performed": False,
        "ui_contract": contract["ui_contract"],
        "blocked_authority": contract["blocked_authority"],
    }


def build_operator_console_preview(action_key: str) -> dict[str, Any]:
    contract = build_operator_console_contract()
    selected = next((action for action in contract["operator_controls"] if action["action_key"] == action_key), None)
    if selected is None:
        return {
            "ok": False,
            "status": "unknown_action",
            "action_key": action_key,
            "available_actions": [action["action_key"] for action in contract["operator_controls"]],
            "unlock_allowed": False,
            "execution_enabled": False,
            "body_read_allowed": False,
            "network_request_performed": False,
        }

    return {
        "ok": True,
        "status": "preview_ready",
        "phase": contract["phase"],
        "action_key": action_key,
        "action": selected,
        "preview": selected["preview"],
        "unlock_allowed": False,
        "execution_enabled": False,
        "body_read_allowed": False,
        "network_request_performed": False,
        "blocked_authority": _blocked_authority(),
    }


@router.get("/dashboard/operator-console/contract")
def dashboard_operator_console_contract() -> dict[str, Any]:
    return build_operator_console_contract()


@router.get("/api/dashboard/operator-console/contract")
def api_dashboard_operator_console_contract() -> dict[str, Any]:
    return build_operator_console_contract()


@router.get("/dashboard/operator-console/summary")
def dashboard_operator_console_summary() -> dict[str, Any]:
    return build_operator_console_summary()


@router.get("/api/dashboard/operator-console/summary")
def api_dashboard_operator_console_summary() -> dict[str, Any]:
    return build_operator_console_summary()


@router.get("/dashboard/operator-console/actions")
def dashboard_operator_console_actions() -> dict[str, Any]:
    contract = build_operator_console_contract()
    return {
        "ok": True,
        "status": "ready",
        "action_count": contract["action_count"],
        "actions": contract["operator_controls"],
        "unlock_allowed": False,
        "execution_enabled": False,
        "body_read_allowed": False,
    }


@router.get("/api/dashboard/operator-console/actions")
def api_dashboard_operator_console_actions() -> dict[str, Any]:
    return dashboard_operator_console_actions()


@router.get("/dashboard/operator-console/preview/{action_key}")
def dashboard_operator_console_preview(action_key: str) -> dict[str, Any]:
    return build_operator_console_preview(action_key)


@router.get("/api/dashboard/operator-console/preview/{action_key}")
def api_dashboard_operator_console_preview(action_key: str) -> dict[str, Any]:
    return build_operator_console_preview(action_key)


def include_dashboard_operator_console_contract_routes(app: Any) -> None:
    app.include_router(router)
