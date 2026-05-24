from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
STORE_ROOT = ROOT / "data" / "operator_workflows"

COLLECTIONS = {
    "review_queue": STORE_ROOT / "review_queue.json",
    "bounded_web_jobs": STORE_ROOT / "bounded_web_jobs.json",
    "exports": STORE_ROOT / "exports.json",
    "audit_trail": STORE_ROOT / "audit_trail.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    STORE_ROOT.mkdir(parents=True, exist_ok=True)
    for path in COLLECTIONS.values():
        if not path.exists():
            path.write_text("[]\n", encoding="utf-8")


def _read_collection(name: str) -> List[Dict[str, object]]:
    if name not in COLLECTIONS:
        raise ValueError(f"Unknown collection: {name}")
    _ensure_store()
    text = COLLECTIONS[name].read_text(encoding="utf-8").strip()
    if not text:
        return []
    return json.loads(text)


def _write_collection(name: str, records: List[Dict[str, object]]) -> None:
    if name not in COLLECTIONS:
        raise ValueError(f"Unknown collection: {name}")
    _ensure_store()
    COLLECTIONS[name].write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def append_workflow_record(collection: str, record: Dict[str, object]) -> Dict[str, object]:
    if collection not in COLLECTIONS:
        raise ValueError(f"Unknown collection: {collection}")

    safe_record = dict(record)
    safe_record.setdefault("created_at", _now())
    safe_record["runtime_truth_write"] = False
    safe_record["runtime_mutation"] = False
    safe_record["storage_scope"] = "operator_workflow_only"

    records = _read_collection(collection)
    records.append(safe_record)
    _write_collection(collection, records)

    return {
        "collection": collection,
        "count": len(records),
        "stored": True,
        "runtime_truth_write": False,
        "runtime_mutation": False,
    }


def list_workflow_records(collection: str) -> List[Dict[str, object]]:
    return _read_collection(collection)


def get_workflow_counts() -> Dict[str, object]:
    _ensure_store()
    counts = {name: len(_read_collection(name)) for name in COLLECTIONS}
    return {
        "version": "v19.89.8-S268-S274",
        "counts": counts,
        "runtime_truth_write_enabled": False,
        "storage_scope": "operator_workflow_only",
    }


def get_storage_adapter_contract() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S268-S274",
        "store_root": str(STORE_ROOT),
        "collections": sorted(COLLECTIONS.keys()),
        "append_only_audit_trail": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "persistence_ready": True,
    }
