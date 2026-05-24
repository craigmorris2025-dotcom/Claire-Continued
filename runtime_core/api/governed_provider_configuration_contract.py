"""Governed provider configuration contract.

S33R8 is passive configuration governance.
It does not execute network requests or enable live updates.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


REQUIRED_ENV_VARS = [
    "PLATFORM_SEARCH_PROVIDER",
]

OPTIONAL_ENV_VARS = [
    "PLATFORM_SEARCH_PROVIDER_BASE_URL",
    "PLATFORM_SEARCH_PROVIDER_API_KEY",
    "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE",
    "PLATFORM_ALLOW_CONTROLLED_METADATA_GET",
    "PLATFORM_ALLOW_ONE_SHOT_METADATA_PROBE",
    "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER",
    "PLATFORM_ALLOW_DUCKDUCKGO_FALLBACK",
    "PLATFORM_SEARCH_PROVIDER_STACK",
    "BING_SEARCH_API_KEY",
    "BRAVE_SEARCH_API_KEY",
    "SEARCHGOV_ACCESS_KEY",
    "SEARCHGOV_AFFILIATE",
    "SERPAPI_API_KEY",
    "TAVILY_API_KEY",
]

SUPPORTED_PROVIDERS = [
    {
        "id": "brave",
        "provider_type": "search_api",
        "required_env_vars": ["BRAVE_SEARCH_API_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "bing",
        "provider_type": "search_api",
        "required_env_vars": ["BING_SEARCH_API_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "searchgov",
        "provider_type": "search_api",
        "required_env_vars": ["SEARCHGOV_AFFILIATE", "SEARCHGOV_ACCESS_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "google_custom_search",
        "provider_type": "search_api",
        "required_env_vars": ["PLATFORM_SEARCH_PROVIDER_API_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "serpapi",
        "provider_type": "search_api",
        "required_env_vars": ["SERPAPI_API_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "tavily",
        "provider_type": "search_api",
        "required_env_vars": ["TAVILY_API_KEY"],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": True,
    },
    {
        "id": "duckduckgo",
        "provider_type": "fallback_metadata_search",
        "required_env_vars": [],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": False,
        "fallback_only": True,
    },
    {
        "id": "manual_stub",
        "provider_type": "offline_stub",
        "required_env_vars": [],
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
        "research_grade": False,
    },
]


def _present(name: str) -> bool:
    value = os.environ.get(name)
    return bool(value and value.strip())


def get_governed_provider_configuration_contract() -> Dict[str, Any]:
    provider = os.environ.get("PLATFORM_SEARCH_PROVIDER", "").strip()
    provider_declared = bool(provider)
    supported_ids = {item["id"] for item in SUPPORTED_PROVIDERS}
    provider_supported = provider in supported_ids if provider_declared else False

    missing_required = [name for name in REQUIRED_ENV_VARS if not _present(name)]

    return {
        "version": "v19.89.8-S33R8",
        "status": "provider_declared" if provider_declared else "blocked_missing_provider_configuration",
        "provider_declared": provider_declared,
        "provider_id": provider or None,
        "provider_supported": provider_supported,
        "missing_required_env_vars": missing_required,
        "required_env_vars": REQUIRED_ENV_VARS,
        "optional_env_vars": OPTIONAL_ENV_VARS,
        "supported_providers": SUPPORTED_PROVIDERS,
        "execution_enabled": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "next_safe_step": "validate provider readiness without executing a probe",
    }
