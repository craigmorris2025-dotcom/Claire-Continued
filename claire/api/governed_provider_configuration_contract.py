"""Governed provider configuration contract.

S33R8 is passive configuration governance.
It does not execute network requests or enable live updates.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


REQUIRED_ENV_VARS = [
    "CLAIRE_SEARCH_PROVIDER",
]

OPTIONAL_ENV_VARS = [
    "CLAIRE_SEARCH_PROVIDER_BASE_URL",
    "CLAIRE_SEARCH_PROVIDER_API_KEY",
    "CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE",
    "CLAIRE_ALLOW_CONTROLLED_METADATA_GET",
    "CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE",
]

SUPPORTED_PROVIDERS = [
    {
        "id": "google_custom_search",
        "provider_type": "search_api",
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
    },
    {
        "id": "serpapi",
        "provider_type": "search_api",
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
    },
    {
        "id": "manual_stub",
        "provider_type": "offline_stub",
        "metadata_only_supported": True,
        "body_read_required": False,
        "browser_required": False,
        "runtime_truth_write_allowed": False,
    },
]


def _present(name: str) -> bool:
    value = os.environ.get(name)
    return bool(value and value.strip())


def get_governed_provider_configuration_contract() -> Dict[str, Any]:
    provider = os.environ.get("CLAIRE_SEARCH_PROVIDER", "").strip()
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
