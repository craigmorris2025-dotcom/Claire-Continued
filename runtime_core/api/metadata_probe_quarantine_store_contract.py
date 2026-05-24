"""Metadata probe quarantine store contract.

S33R13 defines the quarantine record/store behavior without writing live evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
QUARANTINE_DIR = ROOT / "data" / "internet_evidence"
QUARANTINE_QUEUE = QUARANTINE_DIR / "metadata_probe_quarantine_queue.json"


QUARANTINE_RECORD_SCHEMA = {
    "required": [
        "record_id",
        "created_at_utc",
        "source",
        "capture_type",
        "allowed_capture_fields",
        "promotion_state",
    ],
    "forbidden": [
        "response_body",
        "rendered_dom",
        "browser_screenshot",
        "script_execution",
        "runtime_truth_write",
    ],
}


def get_metadata_probe_quarantine_store_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R13",
        "status": "quarantine_store_contract_visible",
        "quarantine_dir": str(QUARANTINE_DIR).replace("\\", "/"),
        "quarantine_queue_path": str(QUARANTINE_QUEUE).replace("\\", "/"),
        "queue_write_enabled": False,
        "live_evidence_write_enabled": False,
        "manual_promotion_required": True,
        "runtime_truth_write_allowed": False,
        "record_schema": QUARANTINE_RECORD_SCHEMA,
        "current_items": [],
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "Register a guarded HEAD-only endpoint only after router proof and "
            "operator-trigger gates are explicitly satisfied."
        ),
    }
