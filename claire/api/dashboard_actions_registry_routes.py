from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter


router = APIRouter()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def build_dashboard_actions() -> list[dict[str, Any]]:
    definitions = [
        ("plan_search", "Plan a governed search", "Prepare a governed search plan without provider execution."),
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
                "network_request_performed": False,
                "body_read_allowed": False,
                "authority": "review_only",
                "button_label": label,
                "description": description,
                "preview": {
                    "headline": label,
                    "body": description + " This is review-only and keeps execution authority blocked.",
                },
                "blocked_authorities": _blocked_authorities(),
            }
        )
    return actions


def build_dashboard_actions_registry() -> dict[str, Any]:
    actions = build_dashboard_actions()
    return {
        "ok": True,
        "status": "ready",
        "ready": True,
        "registered": True,
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


def build_dashboard_actions_summary() -> dict[str, Any]:
    registry = build_dashboard_actions_registry()
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


def build_dashboard_action_preview(action_key: str = "plan_search") -> dict[str, Any]:
    actions = build_dashboard_actions()
    selected = next((a for a in actions if a["action_key"] == action_key or a["id"] == action_key or a["key"] == action_key), None)
    if selected is None:
        return {
            "ok": False,
            "status": "unknown_action",
            "action_key": action_key,
            "execution_enabled": False,
            "network_request_performed": False,
            "body_read_allowed": False,
            "blocked_authorities": _blocked_authorities(),
            "available_actions": [a["action_key"] for a in actions],
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


def build_dashboard_actions_payload() -> dict[str, Any]:
    return build_dashboard_actions_registry()


get_dashboard_actions = build_dashboard_actions
get_governed_dashboard_actions = build_dashboard_actions
get_dashboard_actions_registry = build_dashboard_actions_registry
get_dashboard_actions_summary = build_dashboard_actions_summary
get_dashboard_action_preview = build_dashboard_action_preview


@router.get("/dashboard/actions/registry")
def dashboard_actions_registry() -> dict[str, Any]:
    return build_dashboard_actions_registry()


@router.get("/api/dashboard/actions/registry")
def api_dashboard_actions_registry() -> dict[str, Any]:
    return build_dashboard_actions_registry()


@router.get("/dashboard/actions/summary")
def dashboard_actions_summary() -> dict[str, Any]:
    return build_dashboard_actions_summary()


@router.get("/api/dashboard/actions/summary")
def api_dashboard_actions_summary() -> dict[str, Any]:
    return build_dashboard_actions_summary()


@router.get("/dashboard/actions/preview/{action_key}")
def dashboard_actions_preview(action_key: str) -> dict[str, Any]:
    return build_dashboard_action_preview(action_key)


@router.get("/api/dashboard/actions/preview/{action_key}")
def api_dashboard_actions_preview(action_key: str) -> dict[str, Any]:
    return build_dashboard_action_preview(action_key)


def include_dashboard_actions_registry_routes(app: Any) -> None:
    app.include_router(router)


__all__ = [
    "router",
    "build_dashboard_actions",
    "build_dashboard_actions_registry",
    "build_dashboard_actions_summary",
    "build_dashboard_action_preview",
    "build_dashboard_actions_payload",
    "get_dashboard_actions",
    "get_governed_dashboard_actions",
    "get_dashboard_actions_registry",
    "get_dashboard_actions_summary",
    "get_dashboard_action_preview",
    "include_dashboard_actions_registry_routes",
]
