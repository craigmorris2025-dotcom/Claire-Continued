from __future__ import annotations

from typing import Any

ROUTE_PREVIEWS: list[dict[str, Any]] = [
    {
        "route_id": "trend_discovery_preview",
        "label": "Trend / thesis route preview",
        "trigger_conditions": ["multiple corroborating metadata results", "source family diversity", "recency signal"],
        "terminal_state_preview": "trend_thesis_ready_after_operator_review",
        "enabled_now": False,
        "reason": "Preview only; evidence promotion and lifecycle mutation remain blocked.",
    },
    {
        "route_id": "portfolio_preview",
        "label": "Portfolio route preview",
        "trigger_conditions": ["market signal", "entity/ticker extraction", "source trust score above threshold"],
        "terminal_state_preview": "portfolio_action_ready_after_operator_review",
        "enabled_now": False,
        "reason": "Preview only; portfolio mutation/action remains blocked.",
    },
    {
        "route_id": "breakthrough_preview",
        "label": "Breakthrough route preview",
        "trigger_conditions": ["non-obvious structural advancement", "gap qualification", "evidence confidence threshold"],
        "terminal_state_preview": "breakthrough_classified_after_operator_review",
        "enabled_now": False,
        "reason": "Preview only; no autonomous escalation is enabled.",
    },
    {
        "route_id": "design_preview",
        "label": "Design / AutoDesign route preview",
        "trigger_conditions": ["technical construction opportunity", "buildability route signal", "component/dependency hints"],
        "terminal_state_preview": "design_output_ready_after_operator_review",
        "enabled_now": False,
        "reason": "Preview only; no automatic design generation is triggered by web evidence yet.",
    },
    {
        "route_id": "update_readiness_preview",
        "label": "Update readiness route preview",
        "trigger_conditions": ["official dependency docs", "version-policy match", "validation plan present"],
        "terminal_state_preview": "governed_update_readiness_review_after_operator_approval",
        "enabled_now": False,
        "reason": "Preview only; automatic updates, package downloads, and installs remain blocked.",
    },
]

BLOCKED_AUTHORITY: dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}


def build_evidence_lifecycle_routing_preview() -> dict[str, Any]:
    return {
        "preview_id": "s667_s673_evidence_to_lifecycle_routing_preview",
        "status": "routing_preview_ready_blocked",
        "route_preview_count": len(ROUTE_PREVIEWS),
        "route_previews": ROUTE_PREVIEWS,
        "selected_route": None,
        "lifecycle_mutated": False,
        "runtime_truth_mutated": False,
        "blocked_authority": BLOCKED_AUTHORITY.copy(),
    }


def build_lifecycle_preview_cards() -> list[dict[str, Any]]:
    cards = [
        {
            "card_id": "evidence_lifecycle_routing_preview",
            "title": "Evidence-to-lifecycle routing preview",
            "status": "preview_only",
            "summary": "Shows where reviewed search evidence could route without moving runtime state.",
            "route_count": len(ROUTE_PREVIEWS),
            "lifecycle_mutated": False,
        }
    ]
    for preview in ROUTE_PREVIEWS:
        cards.append(
            {
                "card_id": preview["route_id"],
                "title": preview["label"],
                "status": "blocked_preview",
                "summary": preview["reason"],
                "trigger_conditions": preview["trigger_conditions"],
                "terminal_state_preview": preview["terminal_state_preview"],
                "enabled_now": False,
            }
        )
    return cards


def build_lifecycle_preview_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": "review_evidence_lifecycle_routes",
            "label": "Review evidence-to-lifecycle route preview",
            "status": "available_for_review",
            "executable": False,
            "endpoint": "/api/evidence/lifecycle/routing-preview",
            "reason": "Review only; no lifecycle state changes are allowed.",
        },
        {
            "action_id": "apply_evidence_lifecycle_route",
            "label": "Apply evidence lifecycle route",
            "status": "blocked",
            "executable": False,
            "endpoint": None,
            "reason": "Lifecycle mutation remains blocked until a later explicit governed unlock.",
        },
    ]


def build_lifecycle_preview_status() -> dict[str, Any]:
    return {
        "status": "preview_ready",
        "stage_range": "S667-S673",
        "route_previews_present": True,
        "selected_route": None,
        "lifecycle_mutated": False,
        "runtime_truth_mutated": False,
    }


def build_lifecycle_preview_payload() -> dict[str, Any]:
    return {
        "payload_id": "s667_s673_evidence_lifecycle_routing_preview",
        "preview": build_evidence_lifecycle_routing_preview(),
        "cards": build_lifecycle_preview_cards(),
        "actions": build_lifecycle_preview_actions(),
        "status": build_lifecycle_preview_status(),
    }
