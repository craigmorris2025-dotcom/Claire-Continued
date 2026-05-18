"""S35 first one-shot metadata execution readiness.

This module reports readiness for a first operator-triggered metadata-only HEAD
probe. It performs no network request.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.api.s35_endpoint_registration_preflight import (
    get_s35_endpoint_registration_preflight,
)
from claire.api.cockpit_metadata_probe_trigger_contract import (
    get_cockpit_metadata_probe_trigger_contract,
)
from claire.api.metadata_probe_quarantine_writer import (
    get_metadata_probe_quarantine_writer_status,
)


def get_s35_one_shot_metadata_execution_readiness() -> Dict[str, Any]:
    preflight = get_s35_endpoint_registration_preflight()
    trigger = get_cockpit_metadata_probe_trigger_contract()
    quarantine = get_metadata_probe_quarantine_writer_status()

    ready = (
        preflight.get("registration_allowed") is True
        and trigger.get("trigger_enabled") is True
        and quarantine.get("runtime_truth_write_allowed") is False
    )

    return {
        "version": "v19.89.8-S35R3",
        "status": "one_shot_metadata_probe_ready" if ready else "one_shot_metadata_probe_blocked",
        "ready_for_operator_triggered_probe": ready,
        "registration_allowed": preflight.get("registration_allowed"),
        "trigger_enabled": trigger.get("trigger_enabled"),
        "quarantine_available": quarantine.get("status") == "quarantine_writer_available_passive",
        "operator_trigger_required": True,
        "metadata_only": True,
        "method": "HEAD",
        "network_request": "blocked_until_operator_trigger" if ready else "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "If ready, run exactly one operator-triggered HEAD-only probe and store "
            "metadata-only output in quarantine."
        ),
    }
