from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List

class ScenarioPackBuilder:
    def build_pack(self, scenario_id: str, title: str, steps: List[str]) -> Dict[str, Any]:
        return {
            "record_type": "scenario_pack",
            "scenario_id": scenario_id,
            "title": title,
            "steps": steps,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
