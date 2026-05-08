from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class ProofRecordSeeder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def seed_record(self, record_id: str, category: str, summary: str) -> Dict[str, Any]:
        return {
            "record_type": "proof_seed",
            "record_id": record_id,
            "category": category,
            "summary": summary,
            "status": "seeded_needs_review",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_seed(self, record: Dict[str, Any]) -> Path:
        out = self.root / "data" / "evidence_population" / "seed_records" / f"{record['record_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return out
