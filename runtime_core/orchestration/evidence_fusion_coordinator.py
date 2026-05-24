
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

FUSION_STATE_PATH = Path("data/orchestration/evidence_fusion_state.json")

SOURCE_PATHS = {
    "approved_live_ingestion": Path("data/live/approved_live_ingestion_records.json"),
    "quarantine": Path("data/live/live_ingestion_quarantine.json"),
    "proof_records": Path("data/proof/proof_records.json"),
    "strategic_memory": Path("data/memory/strategic_memory_registry.json"),
}

def _load_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def build_evidence_fusion_state() -> Dict[str, Any]:
    loaded = {name: _load_list(path) for name, path in SOURCE_PATHS.items()}

    total_records = sum(len(records) for records in loaded.values())
    status_counter = Counter()
    source_counts = {}

    for name, records in loaded.items():
        source_counts[name] = len(records)
        for record in records:
            status_counter[str(record.get("status", record.get("record_type", "unknown")))] += 1

    fusion = {
        "version": "16.83",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "total_records": total_records,
        "source_counts": source_counts,
        "status_counts": dict(status_counter),
        "fusion_notes": [
            "Fusion state summarizes governed records only.",
            "Quarantined records are visible but not eligible for high-confidence scoring.",
            "Strategic memory and proof records provide continuity across runs.",
        ],
    }

    FUSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FUSION_STATE_PATH.write_text(json.dumps(fusion, indent=2), encoding="utf-8")
    return fusion
