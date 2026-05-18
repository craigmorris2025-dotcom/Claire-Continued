from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter


router = APIRouter(tags=["Operator Action Click Result Surface"])


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


def _actions() -> list[dict[str, Any]]:
    try:
        from claire.api.dashboard_operator_console_contract import build_operator_console_contract

        contract = build_operator_console_contract()
        controls = contract.get("operator_controls")
        if isinstance(controls, list) and controls:
            return controls
    except Exception:
        pass

    try:
        from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry

        payload = build_dashboard_actions_registry()
        actions = payload.get("actions")
        if isinstance(actions, list) and actions:
            return actions
    except Exception:
        pass

    return [
        {
            "id": "plan_search",
            "key": "plan_search",
            "action_key": "plan_search",
            "label": "Plan a governed search",
            "description": "Prepare a governed search plan without provider execution.",
            "preview": {
                "headline": "Plan a governed search",
                "body": "Prepare a governed search plan without provider execution.",
            },
        }
    ]


def _normalize_key(action: dict[str, Any]) -> str:
    return str(action.get("action_key") or action.get("key") or action.get("id") or action.get("label") or "")


def _find_action(action_key: str) -> dict[str, Any] | None:
    wanted = str(action_key or "").strip()
    wanted_lower = wanted.lower()
    for action in _actions():
        keys = {
            str(action.get("action_key") or ""),
            str(action.get("key") or ""),
            str(action.get("id") or ""),
            str(action.get("label") or ""),
            str(action.get("title") or ""),
            str(action.get("button_label") or ""),
        }
        if wanted in keys or wanted_lower in {key.lower() for key in keys}:
            return action
    return None


def build_operator_action_result(action_key: str) -> dict[str, Any]:
    action = _find_action(action_key)
    if action is None:
        return {
            "ok": False,
            "status": "unknown_action",
            "action_key": action_key,
            "available_actions": [_normalize_key(action) for action in _actions()],
            "result": {
                "headline": "Unknown governed action",
                "body": "No review-only operator action is registered for that key.",
                "next_step": "Select one of the registered governed actions.",
            },
            "unlock_allowed": False,
            "execution_enabled": False,
            "network_request_performed": False,
            "body_read_allowed": False,
            "blocked_authority": _blocked_authority(),
            "blocked_authorities": _blocked_flags(),
        }

    label = str(action.get("label") or action.get("title") or action.get("name") or action_key)
    description = str(action.get("description") or "Review-only operator action selected.")
    preview = action.get("preview") if isinstance(action.get("preview"), dict) else {}

    return {
        "ok": True,
        "status": "review_preview_ready",
        "action_key": _normalize_key(action),
        "label": label,
        "generated_at": _utc_now(),
        "result": {
            "headline": str(preview.get("headline") or label),
            "body": str(preview.get("body") or description),
            "next_step": "Review this preview. Execution remains blocked until a future explicit governed approval gate exists.",
            "mode": "review_only",
        },
        "preview": {
            "headline": str(preview.get("headline") or label),
            "body": str(preview.get("body") or description),
        },
        "action": action,
        "review_only": True,
        "unlock_allowed": False,
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "blocked_authority": _blocked_authority(),
        "blocked_authorities": _blocked_flags(),
    }


@router.get("/dashboard/operator-action/result/{action_key}")
def dashboard_operator_action_result(action_key: str) -> dict[str, Any]:
    return build_operator_action_result(action_key)


@router.get("/api/dashboard/operator-action/result/{action_key}")
def api_dashboard_operator_action_result(action_key: str) -> dict[str, Any]:
    return build_operator_action_result(action_key)


@router.get("/dashboard/actions/result/{action_key}")
def dashboard_actions_result(action_key: str) -> dict[str, Any]:
    return build_operator_action_result(action_key)


@router.get("/api/dashboard/actions/result/{action_key}")
def api_dashboard_actions_result(action_key: str) -> dict[str, Any]:
    return build_operator_action_result(action_key)


def include_operator_action_click_result_routes(app: Any) -> None:
    app.include_router(router)
