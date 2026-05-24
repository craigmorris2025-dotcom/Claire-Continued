"""S34 first live metadata plateau status.

S34R12 summarizes whether Claire is ready for the first true governed metadata probe.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.cockpit_metadata_probe_trigger_contract import (
    get_cockpit_metadata_probe_trigger_contract,
)
from runtime_core.api.metadata_probe_quarantine_writer import (
    get_metadata_probe_quarantine_writer_status,
)
from runtime_core.api.cockpit_manual_review_gate import get_cockpit_manual_review_gate


def get_s34_first_live_metadata_plateau_status() -> Dict[str, Any]:
    trigger = get_cockpit_metadata_probe_trigger_contract()
    quarantine = get_metadata_probe_quarantine_writer_status()
    review = get_cockpit_manual_review_gate()

    ready = (
        trigger.get("trigger_enabled") is True
        and quarantine.get("runtime_truth_write_allowed") is False
        and review.get("review_required") is True
    )

    return {
        "version": "v19.89.8-S34R12",
        "status": "ready_for_operator_metadata_probe" if ready else "blocked_before_first_live_probe",
        "ready_for_first_live_metadata_probe": ready,
        "endpoint_trigger": trigger,
        "quarantine_status": quarantine,
        "manual_review_gate": review,
        "live_update_apply_enabled": False,
        "automatic_updates": "blocked",
        "autonomous_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "network_request": "blocked_until_operator_trigger" if ready else "blocked",
        "next_safe_step": (
            "If ready, perform one operator-triggered HEAD-only probe and write "
            "metadata to quarantine. Otherwise resolve blocked gates first."
        ),
    }
