"""S35 quarantine verification report contract.

S35R9 verifies the quarantine path and expected safety invariants without
executing a probe.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.metadata_probe_quarantine_writer import (
    get_metadata_probe_quarantine_writer_status,
)
from runtime_core.api.metadata_probe_quarantine_store_contract import (
    get_metadata_probe_quarantine_store_contract,
)


def get_s35_quarantine_verification_report() -> Dict[str, Any]:
    writer = get_metadata_probe_quarantine_writer_status()
    store = get_metadata_probe_quarantine_store_contract()

    queue_path_matches = writer.get("queue_path") == store.get("quarantine_queue_path")
    ready = (
        writer.get("status") == "quarantine_writer_available_passive"
        and store.get("manual_promotion_required") is True
        and queue_path_matches
    )

    return {
        "version": "v19.89.8-S35R9",
        "status": "quarantine_verification_passed" if ready else "quarantine_verification_blocked",
        "quarantine_ready_for_first_probe": ready,
        "queue_path_matches_contract": queue_path_matches,
        "writer_status": writer,
        "store_contract": {
            "quarantine_queue_path": store.get("quarantine_queue_path"),
            "manual_promotion_required": store.get("manual_promotion_required"),
            "runtime_truth_write_allowed": store.get("runtime_truth_write_allowed"),
            "queue_write_enabled": store.get("queue_write_enabled"),
        },
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
