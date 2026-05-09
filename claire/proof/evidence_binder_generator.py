
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.proof.proof_record_store import list_proof_records

EVIDENCE_BINDER_PATH = Path("data/proof/evidence_binder.json")

def build_evidence_binder() -> Dict[str, Any]:
    records = list_proof_records()
    type_counts = Counter(record.get("record_type", "unknown") for record in records)

    binder = {
        "version": "16.59",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "record_count": len(records),
        "record_type_counts": dict(type_counts),
        "minimum_targets": {
            "benchmark_replay": 25,
            "operator_review": 25,
            "outcome_label": 25,
            "false_positive": 10,
            "source_lineage": 10,
            "complete_demo_runs": 5,
            "polished_pilot_scenarios": 3,
        },
        "readiness_notes": [
            "Binder is structurally ready.",
            "Acquisition confidence depends on filling proof targets with real records.",
            "Live internet evidence should remain gated until lineage, rights, and review are recorded.",
        ],
        "records": records,
    }

    EVIDENCE_BINDER_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_BINDER_PATH.write_text(json.dumps(binder, indent=2), encoding="utf-8")
    return binder
