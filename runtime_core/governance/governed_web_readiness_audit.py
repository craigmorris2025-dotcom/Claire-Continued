from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

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

READINESS_COMPONENTS: list[dict[str, Any]] = [
    {"component_id": "source_registry", "label": "Governed source registry", "required_before_execution": True, "expected_state": "present_from_s576_s582", "failure_mode": "search_scope_unknown"},
    {"component_id": "query_compiler", "label": "Governed query compiler", "required_before_execution": True, "expected_state": "present_from_s618_s624", "failure_mode": "query_not_policy_scoped"},
    {"component_id": "source_policy_controls", "label": "Source policy controls", "required_before_execution": True, "expected_state": "present_from_s632_s638", "failure_mode": "allow_deny_quarantine_not_enforced"},
    {"component_id": "metadata_result_contract", "label": "Metadata-only result contract", "required_before_execution": True, "expected_state": "present_from_s646_s652", "failure_mode": "body_read_boundary_unclear"},
    {"component_id": "quarantine_review_store", "label": "Quarantine evidence store", "required_before_execution": True, "expected_state": "present_from_s639_s645", "failure_mode": "unreviewed_result_could_be_misread_as_truth"},
    {"component_id": "cockpit_consolidation", "label": "Cockpit source/search consolidation", "required_before_execution": True, "expected_state": "present_from_s674_s680", "failure_mode": "operator_cannot_see_source_search_state"},
]

@dataclass(frozen=True)
class ReadinessAudit:
    audit_id: str
    stage_range: str
    status: str
    activation_state: str
    execution_allowed: bool
    network_request_performed: bool
    blocker_summary: list[str]
    components: list[dict[str, Any]]
    blocked_authority: dict[str, bool]


def build_readiness_audit() -> dict[str, Any]:
    audit = ReadinessAudit(
        audit_id="s681_s687_search_web_readiness_audit",
        stage_range="S681-S687",
        status="readiness_preflight_ready_execution_blocked",
        activation_state="metadata_activation_preflight_only",
        execution_allowed=False,
        network_request_performed=False,
        blocker_summary=[
            "provider execution remains disabled",
            "network requests remain disabled",
            "body reads remain disabled",
            "results must remain quarantine-first",
            "operator approval is required before any later live probe unlock",
        ],
        components=READINESS_COMPONENTS,
        blocked_authority=BLOCKED_AUTHORITY.copy(),
    )
    return asdict(audit)


def build_readiness_cards() -> list[dict[str, Any]]:
    return [
        {
            "card_id": "search_web_activation_preflight",
            "title": "Search/web activation preflight",
            "status": "ready_blocked",
            "summary": "Claire has the source/search governance surfaces needed to inspect readiness, but execution remains blocked.",
            "details": [component["label"] for component in READINESS_COMPONENTS],
            "blocked_authority": BLOCKED_AUTHORITY.copy(),
        },
        {
            "card_id": "metadata_activation_blockers",
            "title": "Metadata activation blockers",
            "status": "blocked_by_policy",
            "summary": "The next activation work is adapter/probe preparation, not open-web unlocking.",
            "details": ["no provider execution", "no network request", "no response body read", "no crawling", "no automatic update", "no runtime mutation"],
        },
    ]


def build_readiness_actions() -> list[dict[str, Any]]:
    return [
        {"action_id": "review_search_web_readiness_audit", "label": "Review search/web readiness audit", "status": "available_for_review", "executable": False, "endpoint": "/api/search/readiness/audit", "reason": "Visible for cockpit review only."},
        {"action_id": "unlock_metadata_probe_execution", "label": "Unlock metadata probe execution", "status": "blocked", "executable": False, "endpoint": None, "reason": "S681-S708 does not enable live provider execution."},
    ]


def build_activation_preflight() -> dict[str, Any]:
    audit = build_readiness_audit()
    return {
        "preflight_id": "s681_s687_activation_preflight",
        "status": "preflight_ready_execution_blocked",
        "can_execute_provider_probe": False,
        "can_perform_network_request": False,
        "can_read_body": False,
        "can_mutate_runtime": False,
        "required_before_future_unlock": ["operator-selected provider configuration", "explicit metadata-only environment gate", "rate limit policy", "quarantine persistence proof", "cockpit visible review actions"],
        "audit": audit,
    }


def build_readiness_payload() -> dict[str, Any]:
    return {"payload_id": "s681_s687_search_web_readiness_audit_payload", "audit": build_readiness_audit(), "preflight": build_activation_preflight(), "cards": build_readiness_cards(), "actions": build_readiness_actions(), "blocked_authority": BLOCKED_AUTHORITY.copy()}
