from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class OutcomeLabelAdjudicator:
    """Creates adjudicated outcome labels for benchmark and replay learning."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def adjudicate(self, item_id: str, proposed_label: str, reviewer: str = "operator", notes: str = "") -> Dict[str, Any]:
        return {
            "record_type": "outcome_label_adjudication",
            "item_id": item_id,
            "label": proposed_label,
            "reviewer": reviewer,
            "notes": notes,
            "adjudicated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "adjudicated",
        }

    def export_label(self, label: Dict[str, Any]) -> Path:
        out = self.root / "data" / "operational_proof" / "outcome_labels" / f"{label['item_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(label, indent=2, sort_keys=True), encoding="utf-8")
        return out
