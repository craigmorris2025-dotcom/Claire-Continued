from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class ROIObservationTracker:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_observation(self, pilot_id: str, time_saved_minutes: float = 0, value_note: str = "") -> Dict[str, Any]:
        return {
            "record_type": "roi_observation",
            "pilot_id": pilot_id,
            "time_saved_minutes": time_saved_minutes,
            "value_note": value_note,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_observation(self, obs: Dict[str, Any]) -> Path:
        out = self.root / "data" / "pilot_operations" / "roi_observations" / f"{obs['pilot_id']}_{obs['observed_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(obs, indent=2, sort_keys=True), encoding="utf-8")
        return out
