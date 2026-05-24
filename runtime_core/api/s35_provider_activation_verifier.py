"""S35 provider activation verifier.

This module verifies whether the explicit provider gates are configured for a
first controlled metadata-only probe. It performs no network request.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


SUPPORTED_PROVIDERS = {"manual_stub", "google_custom_search", "serpapi"}


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _enabled(name: str) -> bool:
    return _env(name).lower() in {"1", "true", "yes", "on"}


def get_s35_provider_activation_verifier() -> Dict[str, Any]:
    provider = _env("PLATFORM_SEARCH_PROVIDER")
    provider_declared = bool(provider)
    provider_supported = provider in SUPPORTED_PROVIDERS

    gates = {
        "provider_declared": provider_declared,
        "provider_supported": provider_supported,
        "controlled_head_probe_allowed": _enabled("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE"),
        "one_shot_metadata_probe_allowed": _enabled("PLATFORM_ALLOW_ONE_SHOT_METADATA_PROBE"),
        "controlled_metadata_get_allowed": _enabled("PLATFORM_ALLOW_CONTROLLED_METADATA_GET"),
    }

    ready = (
        gates["provider_declared"]
        and gates["provider_supported"]
        and gates["controlled_head_probe_allowed"]
        and gates["one_shot_metadata_probe_allowed"]
        and not gates["controlled_metadata_get_allowed"]
    )

    missing = [key for key, value in gates.items() if key != "controlled_metadata_get_allowed" and not value]
    if gates["controlled_metadata_get_allowed"]:
        missing.append("controlled_metadata_get_must_remain_disabled_for_head_only_plateau")

    return {
        "version": "v19.89.8-S35R1",
        "status": "provider_activation_ready" if ready else "provider_activation_blocked",
        "ready": ready,
        "provider_id": provider or None,
        "supported_providers": sorted(SUPPORTED_PROVIDERS),
        "gates": gates,
        "missing_or_blocking_gates": missing,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
