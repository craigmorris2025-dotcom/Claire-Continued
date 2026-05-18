"""Metadata probe quarantine writer contract and helper.

S34R3 can write a metadata-only record only when explicitly called by a future
registered endpoint. It does not run on import and does not mutate runtime truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "data" / "internet_evidence" / "metadata_probe_quarantine_queue.json"


FORBIDDEN_FIELDS = {
    "response_body",
    "rendered_dom",
    "browser_screenshot",
    "script_execution",
    "runtime_truth_write",
}


def _load_queue() -> Dict[str, Any]:
    if not QUEUE_PATH.exists():
        return {"version": "v19.89.8-S34R3", "items": []}
    try:
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "v19.89.8-S34R3", "items": [], "recovered_from_invalid_json": True}


def write_metadata_probe_quarantine_record(record: Dict[str, Any]) -> Dict[str, Any]:
    if any(field in record for field in FORBIDDEN_FIELDS):
        raise ValueError("Forbidden body/browser/runtime field detected in quarantine record.")

    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    queue = _load_queue()
    items = queue.setdefault("items", [])

    safe_record = {
        "record_id": record.get("record_id") or f"metadata_probe_{len(items) + 1}",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "capture_type": "metadata_only_head",
        "promotion_state": "review_required",
        "runtime_truth_write_allowed": False,
        "response_body_read": False,
        "browser_execution": False,
        "automatic_update": False,
        "source": record.get("source", {}),
        "metadata": record.get("metadata", {}),
    }

    items.append(safe_record)
    queue["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    queue["runtime_truth_write_allowed"] = False
    queue["manual_promotion_required"] = True

    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return safe_record


def get_metadata_probe_quarantine_writer_status() -> Dict[str, Any]:
    queue_exists = QUEUE_PATH.exists()
    queue = _load_queue() if queue_exists else {"items": []}

    return {
        "version": "v19.89.8-S34R3",
        "status": "quarantine_writer_available_passive",
        "queue_path": str(QUEUE_PATH).replace("\\", "/"),
        "queue_exists": queue_exists,
        "queue_item_count": len(queue.get("items", [])),
        "writer_runs_on_import": False,
        "runtime_truth_write_allowed": False,
        "manual_promotion_required": True,
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
