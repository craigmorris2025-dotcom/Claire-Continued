from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class BuyerFeedbackCollector:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def collect_feedback(self, pilot_id: str, buyer_segment: str, feedback: str, rating: int = 0) -> Dict[str, Any]:
        return {
            "record_type": "buyer_feedback",
            "pilot_id": pilot_id,
            "buyer_segment": buyer_segment,
            "feedback": feedback,
            "rating": rating,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_feedback(self, record: Dict[str, Any]) -> Path:
        out = self.root / "data" / "pilot_operations" / "buyer_feedback" / f"{record['pilot_id']}_{record['collected_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return out
