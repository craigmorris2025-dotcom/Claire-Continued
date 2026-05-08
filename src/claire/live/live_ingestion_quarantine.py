
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from claire.live.source_registry import evaluate_source


QUARANTINE_PATH = Path("data/live/live_ingestion_quarantine.json")
APPROVED_INGESTION_PATH = Path("data/live/approved_live_ingestion_records.json")


def _load_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def ingest_live_candidate(source_url: str, title: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    source_eval = evaluate_source(source_url)

    record = {
        "version": "16.63",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "title": title,
        "source_evaluation": source_eval,
        "payload": payload,
    }

    if source_eval.get("may_score") is True:
        APPROVED_INGESTION_PATH.parent.mkdir(parents=True, exist_ok=True)
        approved = _load_list(APPROVED_INGESTION_PATH)
        record["status"] = "approved_for_low_risk_ingestion"
        record["scoring_status"] = "eligible_after_replay_and_operator_review"
        approved.append(record)
        APPROVED_INGESTION_PATH.write_text(json.dumps(approved, indent=2), encoding="utf-8")
        return record

    QUARANTINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    quarantined = _load_list(QUARANTINE_PATH)
    record["status"] = "quarantined"
    record["scoring_status"] = "not_eligible_for_scoring"
    quarantined.append(record)
    QUARANTINE_PATH.write_text(json.dumps(quarantined, indent=2), encoding="utf-8")
    return record
