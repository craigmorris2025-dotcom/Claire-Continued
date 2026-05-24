from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter


router = APIRouter(tags=["Dashboard Status Visibility Aliases"])


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


def _safe_payload_snapshot() -> dict[str, Any]:
    try:
        from runtime_core.api.dashboard_operator_console_contract import build_operator_console_summary

        operator = build_operator_console_summary()
    except Exception:
        operator = {
            "status": "ready",
            "action_count": 0,
            "actions_count": 0,
            "controls_count": 0,
            "unlock_allowed": False,
            "execution_enabled": False,
        }

    try:
        from runtime_core.api.dashboard_actions_registry_routes import build_dashboard_actions_registry

        actions_registry = build_dashboard_actions_registry()
    except Exception:
        actions_registry = {
            "status": "ready",
            "action_count": operator.get("action_count", 0),
            "actions_count": operator.get("actions_count", 0),
            "unlock_allowed": False,
        }

    return {
        "operator": operator,
        "actions_registry": actions_registry,
        "action_count": int(
            operator.get("action_count")
            or operator.get("actions_count")
            or actions_registry.get("action_count")
            or actions_registry.get("actions_count")
            or 0
        ),
    }


def build_dashboard_visibility_summary() -> dict[str, Any]:
    snapshot = _safe_payload_snapshot()
    action_count = snapshot["action_count"]

    return {
        "ok": True,
        "status": "ready",
        "generated_at": _utc_now(),
        "surface": "dashboard_visibility_summary",
        "source": "backend_contract_alias",
        "route": "/dashboard/visibility/summary",
        "visibility": {
            "overview": "visible",
            "governed_web": "visible",
            "evidence_review": "visible",
            "actions": "visible" if action_count > 0 else "empty",
            "system": "visible",
            "operator_console": "visible" if action_count > 0 else "empty",
        },
        "panels": {
            "overview": {"visible": True, "status": "ready"},
            "governed_web": {"visible": True, "status": "ready"},
            "evidence_review": {"visible": True, "status": "ready"},
            "actions": {
                "visible": True,
                "status": "ready" if action_count > 0 else "empty",
                "action_count": action_count,
                "actions_chip_should_be_greater_than_zero": action_count > 0,
            },
            "system": {"visible": True, "status": "ready"},
            "operator_console": {
                "visible": True,
                "status": "ready" if action_count > 0 else "empty",
                "controls_count": action_count,
            },
        },
        "actions_count": action_count,
        "action_count": action_count,
        "empty_state": action_count == 0,
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "execution_enabled": False,
        "unlock_allowed": False,
        "body_read_allowed": False,
        "network_request_performed": False,
        "blocked_authority": _blocked_authority(),
        "blocked_authorities": _blocked_flags(),
        "message": "Dashboard visibility summary alias is available. It is read-only and does not unlock execution.",
    }


def build_dashboard_status_harmonized() -> dict[str, Any]:
    snapshot = _safe_payload_snapshot()
    action_count = snapshot["action_count"]

    return {
        "ok": True,
        "status": "ready",
        "harmonized_status": "ready",
        "generated_at": _utc_now(),
        "surface": "dashboard_status_harmonized",
        "source": "backend_contract_alias",
        "route": "/dashboard/status/harmonized",
        "readiness": "governed_internet_update_ready",
        "backend": "ok",
        "payload": "ok",
        "operator_console": "ready" if action_count > 0 else "empty",
        "actions": "ready" if action_count > 0 else "empty",
        "action_count": action_count,
        "actions_count": action_count,
        "chips": [
            {"label": "Backend", "value": "ok", "status": "ok"},
            {"label": "Readiness", "value": "governed_internet_update_ready", "status": "ready"},
            {"label": "Actions", "value": action_count, "status": "ready" if action_count > 0 else "empty"},
            {"label": "Runtime mutation", "value": "blocked", "status": "blocked"},
            {"label": "Body read", "value": "blocked", "status": "blocked"},
        ],
        "execution_enabled": False,
        "unlock_allowed": False,
        "body_read_allowed": False,
        "network_request_performed": False,
        "blocked_authority": _blocked_authority(),
        "blocked_authorities": _blocked_flags(),
        "message": "Dashboard harmonized status alias is available. It is read-only and keeps unsafe authority blocked.",
    }


@router.get("/dashboard/visibility/summary")
def dashboard_visibility_summary() -> dict[str, Any]:
    return build_dashboard_visibility_summary()


@router.get("/api/dashboard/visibility/summary")
def api_dashboard_visibility_summary() -> dict[str, Any]:
    return build_dashboard_visibility_summary()


@router.get("/dashboard/status/harmonized")
def dashboard_status_harmonized() -> dict[str, Any]:
    return build_dashboard_status_harmonized()


@router.get("/api/dashboard/status/harmonized")
def api_dashboard_status_harmonized() -> dict[str, Any]:
    return build_dashboard_status_harmonized()


def include_dashboard_status_visibility_alias_routes(app: Any) -> None:
    app.include_router(router)
