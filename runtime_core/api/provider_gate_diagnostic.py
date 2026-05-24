"""Provider gate diagnostic for first governed metadata probe.

S34R13 reports exact environment gates needed for the first probe.
It does not execute network requests.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


GATES = [
    "PLATFORM_SEARCH_PROVIDER",
    "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE",
    "PLATFORM_ALLOW_ONE_SHOT_METADATA_PROBE",
]


def _value_state(name: str) -> Dict[str, Any]:
    value = os.environ.get(name, "")
    present = bool(value.strip())
    enabled = value.strip().lower() in {"1", "true", "yes", "on"}
    return {
        "name": name,
        "present": present,
        "enabled": enabled,
        "masked_value": "***" if present and "KEY" in name else (value if present else None),
    }


def get_provider_gate_diagnostic() -> Dict[str, Any]:
    gate_states: List[Dict[str, Any]] = [_value_state(name) for name in GATES]
    provider_present = gate_states[0]["present"]
    head_enabled = gate_states[1]["enabled"]
    one_shot_enabled = gate_states[2]["enabled"]

    ready = provider_present and head_enabled and one_shot_enabled

    return {
        "version": "v19.89.8-S34R13",
        "status": "provider_gates_ready" if ready else "provider_gates_incomplete",
        "ready_for_operator_probe_after_endpoint_registration": ready,
        "gate_states": gate_states,
        "required_gates": GATES,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
