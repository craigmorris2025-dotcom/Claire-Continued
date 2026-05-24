from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
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

PROVIDERS: list[dict[str, Any]] = [
    {
        "provider_id": "official_docs_metadata",
        "label": "Official documentation metadata",
        "source_family": "official_docs",
        "trust_tier": "tier_1_authoritative",
        "configured": "unknown_until_operator_config",
        "execution_state": "blocked_until_manual_metadata_probe_gate",
        "allowed_result_fields": ["title", "url", "source_family", "trust_tier", "published_at", "summary_hint"],
        "blocked_capabilities": ["body_read", "crawl", "download", "runtime_mutation", "automatic_update"],
    },
    {
        "provider_id": "news_market_metadata",
        "label": "Market/news metadata",
        "source_family": "market_and_news",
        "trust_tier": "tier_2_corroborrated",
        "configured": "unknown_until_operator_config",
        "execution_state": "blocked_until_manual_metadata_probe_gate",
        "allowed_result_fields": ["title", "url", "source_family", "trust_tier", "published_at", "summary_hint"],
        "blocked_capabilities": ["body_read", "crawl", "download", "runtime_mutation", "automatic_update"],
    },
    {
        "provider_id": "open_web_metadata",
        "label": "Open web metadata",
        "source_family": "open_web",
        "trust_tier": "tier_3_unverified_until_review",
        "configured": "unknown_until_operator_config",
        "execution_state": "blocked_until_manual_metadata_probe_gate",
        "allowed_result_fields": ["title", "url", "source_family", "trust_tier", "published_at", "summary_hint"],
        "blocked_capabilities": ["body_read", "crawl", "download", "runtime_mutation", "automatic_update"],
    },
]

@dataclass(frozen=True)
class ManualProbePreflight:
    probe_id: str
    query: str
    status: str
    execution_allowed: bool
    provider_execution_allowed: bool
    network_request_performed: bool
    result_contract: str
    reason: str
    blocked_authority: dict[str, bool]
    providers: list[dict[str, Any]]


def _probe_id(query: str) -> str:
    normalized = (query or "sample governed metadata probe").strip().lower()
    return "probe_" + sha256(normalized.encode("utf-8")).hexdigest()[:12]


def build_manual_probe_preflight(query: str | None = None) -> dict[str, Any]:
    clean_query = (query or "sample governed metadata probe").strip()
    preflight = ManualProbePreflight(
        probe_id=_probe_id(clean_query),
        query=clean_query,
        status="manual_metadata_probe_preflight_ready_but_execution_blocked",
        execution_allowed=False,
        provider_execution_allowed=False,
        network_request_performed=False,
        result_contract="metadata_only_quarantine_first",
        reason="S653-S659 prepares the manual probe gate only; provider execution remains blocked until a later explicit unlock.",
        blocked_authority=BLOCKED_AUTHORITY.copy(),
        providers=PROVIDERS,
    )
    return asdict(preflight)


def build_manual_probe_cards(query: str | None = None) -> list[dict[str, Any]]:
    preflight = build_manual_probe_preflight(query)
    return [
        {
            "card_id": "manual_probe_gate",
            "title": "Manual provider probe gate",
            "status": "ready_blocked",
            "summary": "Claire can prepare a metadata-only probe, but cannot execute the provider request yet.",
            "details": [
                "operator triggered only",
                "metadata contract only",
                "quarantine-first result path",
                "no response body reads",
                "no crawling or automatic update",
            ],
            "blocked_authority": preflight["blocked_authority"],
        },
        {
            "card_id": "provider_probe_scope",
            "title": "Provider probe scope",
            "status": "planned_not_executed",
            "summary": f"Prepared query scope for: {preflight['query']}",
            "providers": preflight["providers"],
        },
    ]


def build_manual_probe_actions(query: str | None = None) -> list[dict[str, Any]]:
    preflight = build_manual_probe_preflight(query)
    return [
        {
            "action_id": "manual_metadata_probe_preflight",
            "label": "Review manual metadata probe preflight",
            "status": "available_for_review",
            "executable": False,
            "endpoint": "/api/search/provider/manual-probe/preflight",
            "probe_id": preflight["probe_id"],
            "reason": "Action is visible for cockpit review only; execution remains blocked.",
        },
        {
            "action_id": "manual_metadata_probe_execute",
            "label": "Execute provider metadata probe",
            "status": "blocked",
            "executable": False,
            "endpoint": None,
            "reason": "Provider execution is deliberately not enabled in S653-S680.",
        },
    ]


def build_manual_probe_policy() -> dict[str, Any]:
    return {
        "policy_id": "s653_s659_manual_provider_probe_gate",
        "phase": "manual_probe_gate_preparation",
        "allowed": [
            "build_preflight",
            "show_provider_scope",
            "show_blocked_action_descriptors",
            "prepare_metadata_only_contract",
        ],
        "blocked": [name for name, value in BLOCKED_AUTHORITY.items() if value is False],
        "result_path": "metadata_result -> quarantine_store -> evidence_card -> operator_review",
    }


def build_manual_probe_status() -> dict[str, Any]:
    return {
        "status": "ready_blocked",
        "stage_range": "S653-S659",
        "manual_probe_gate_present": True,
        "network_request_performed": False,
        "provider_execution_allowed": False,
        "body_read_allowed": False,
        "stop_gate": "manual_probe_preflight_only",
    }


def build_manual_probe_payload(query: str | None = None) -> dict[str, Any]:
    return {
        "payload_id": "s653_s659_manual_provider_probe_gate",
        "preflight": build_manual_probe_preflight(query),
        "cards": build_manual_probe_cards(query),
        "actions": build_manual_probe_actions(query),
        "policy": build_manual_probe_policy(),
        "status": build_manual_probe_status(),
    }
