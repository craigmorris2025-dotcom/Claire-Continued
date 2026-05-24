"""Governed provider readiness validator.

S33R9 is passive validation only.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from runtime_core.api.governed_provider_configuration_contract import (
    get_governed_provider_configuration_contract,
)


def _flag_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_governed_provider_readiness_validator() -> Dict[str, Any]:
    contract = get_governed_provider_configuration_contract()

    provider_declared = bool(contract.get("provider_declared"))
    provider_supported = bool(contract.get("provider_supported"))
    head_allowed = _flag_enabled("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE")
    metadata_get_allowed = _flag_enabled("PLATFORM_ALLOW_CONTROLLED_METADATA_GET")
    one_shot_allowed = _flag_enabled("PLATFORM_ALLOW_ONE_SHOT_METADATA_PROBE")

    readiness_passed = (
        provider_declared
        and provider_supported
        and head_allowed
        and not metadata_get_allowed
        and not one_shot_allowed
    )

    missing_gates = []
    if not provider_declared:
        missing_gates.append("provider_declared")
    if provider_declared and not provider_supported:
        missing_gates.append("provider_supported")
    if not head_allowed:
        missing_gates.append("controlled_head_probe_allowed")
    if metadata_get_allowed:
        missing_gates.append("metadata_get_must_remain_disabled_for_this_stage")
    if one_shot_allowed:
        missing_gates.append("one_shot_probe_must_remain_disabled_for_this_stage")

    return {
        "version": "v19.89.8-S33R9",
        "status": "provider_readiness_passed" if readiness_passed else "blocked_provider_readiness_incomplete",
        "readiness_passed": readiness_passed,
        "provider_declared": provider_declared,
        "provider_supported": provider_supported,
        "controlled_head_probe_allowed": head_allowed,
        "controlled_metadata_get_allowed": metadata_get_allowed,
        "one_shot_metadata_probe_allowed": one_shot_allowed,
        "missing_gates": missing_gates,
        "execution_enabled": False,
        "route_registered": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
    }
