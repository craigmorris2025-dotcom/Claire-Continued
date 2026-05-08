from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/proof/proof_record_store.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROOF_RECORD_PATH = Path("data/proof/proof_records.json")

VALID_RECORD_TYPES = {
    "benchmark_replay",
    "operator_review",
    "outcome_label",
    "false_positive",
    "source_lineage",
    "demo_run",
    "pilot_readiness_gate",
}

def _load_records() -> List[Dict[str, Any]]:
    if not PROOF_RECORD_PATH.exists():
        return []
    try:
        data = json.loads(PROOF_RECORD_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def add_proof_record(record_type: str, title: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if record_type not in VALID_RECORD_TYPES:
        raise ValueError(f"Invalid proof record type: {record_type}")

    PROOF_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "version": "16.58",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "record_type": record_type,
        "title": title,
        "payload": payload,
    }

    records = _load_records()
    records.append(record)
    PROOF_RECORD_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return record

def list_proof_records() -> List[Dict[str, Any]]:
    return _load_records()
""")

print("v16.58 proof record store installed.")
