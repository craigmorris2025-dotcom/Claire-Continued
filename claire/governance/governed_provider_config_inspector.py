from __future__ import annotations

from dataclasses import asdict, dataclass
from os import getenv
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

PROVIDER_CONFIGS: list[dict[str, Any]] = [
    {"provider_id": "google_custom_search_metadata", "label": "Google Custom Search metadata provider", "source_family": "open_web_or_official_docs", "trust_tier": "tier_depends_on_result_source", "required_env_keys": ["CLAIRE_GOOGLE_SEARCH_API_KEY", "CLAIRE_GOOGLE_SEARCH_CX"], "blocked_until": "manual_metadata_probe_execution_unlock"},
    {"provider_id": "bing_search_metadata", "label": "Bing Search metadata provider", "source_family": "open_web_or_news", "trust_tier": "tier_depends_on_result_source", "required_env_keys": ["CLAIRE_BING_SEARCH_API_KEY"], "blocked_until": "manual_metadata_probe_execution_unlock"},
    {"provider_id": "official_docs_seed_metadata", "label": "Official docs seeded metadata provider", "source_family": "official_docs", "trust_tier": "tier_1_authoritative_when_domain_allowed", "required_env_keys": [], "blocked_until": "manual_metadata_probe_execution_unlock"},
]

@dataclass(frozen=True)
class ProviderInspection:
    provider_id: str
    label: str
    source_family: str
    trust_tier: str
    configured: bool
    missing_env_keys: list[str]
    secrets_exposed: bool
    execution_allowed: bool
    network_request_performed: bool
    status: str
    blocked_until: str


def _is_set(name: str) -> bool:
    value = getenv(name)
    return bool(value and value.strip())


def inspect_provider_configurations() -> list[dict[str, Any]]:
    inspected: list[dict[str, Any]] = []
    for provider in PROVIDER_CONFIGS:
        required = list(provider["required_env_keys"])
        missing = [key for key in required if not _is_set(key)]
        configured = len(missing) == 0
        status = "configured_but_execution_blocked" if configured else "configuration_missing_execution_blocked"
        inspected.append(asdict(ProviderInspection(provider_id=provider["provider_id"], label=provider["label"], source_family=provider["source_family"], trust_tier=provider["trust_tier"], configured=configured, missing_env_keys=missing, secrets_exposed=False, execution_allowed=False, network_request_performed=False, status=status, blocked_until=provider["blocked_until"])))
    return inspected


def build_provider_configuration_cards() -> list[dict[str, Any]]:
    return [
        {
            "card_id": f"provider_config_{item['provider_id']}",
            "title": item["label"],
            "status": item["status"],
            "summary": "Configuration is inspected without exposing secrets and without making a request.",
            "configured": item["configured"],
            "missing_env_keys": item["missing_env_keys"],
            "source_family": item["source_family"],
            "trust_tier": item["trust_tier"],
            "execution_allowed": False,
            "network_request_performed": False,
        }
        for item in inspect_provider_configurations()
    ]


def build_provider_configuration_actions() -> list[dict[str, Any]]:
    return [
        {"action_id": "inspect_provider_configuration", "label": "Inspect provider configuration", "status": "available_for_review", "executable": False, "endpoint": "/api/search/providers/configuration", "reason": "Inspection only; no secret display and no provider request."},
        {"action_id": "execute_configured_provider_search", "label": "Execute configured provider search", "status": "blocked", "executable": False, "endpoint": None, "reason": "Provider execution is not unlocked in S681-S708."},
    ]


def build_provider_configuration_status() -> dict[str, Any]:
    inspected = inspect_provider_configurations()
    configured_count = sum(1 for item in inspected if item["configured"])
    return {"status": "provider_configuration_inspected_execution_blocked", "stage_range": "S688-S694", "providers_total": len(inspected), "providers_configured": configured_count, "secrets_exposed": False, "execution_allowed": False, "network_request_performed": False, "blocked_authority": BLOCKED_AUTHORITY.copy()}


def build_provider_configuration_payload() -> dict[str, Any]:
    return {"payload_id": "s688_s694_provider_configuration_inspector", "providers": inspect_provider_configurations(), "cards": build_provider_configuration_cards(), "actions": build_provider_configuration_actions(), "status": build_provider_configuration_status(), "blocked_authority": BLOCKED_AUTHORITY.copy()}
