from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class PilotRunRegistry:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def create_pilot_run(self, pilot_id: str, objective: str, owner: str = "operator") -> Dict[str, Any]:
        return {
            "record_type": "pilot_run",
            "pilot_id": pilot_id,
            "objective": objective,
            "owner": owner,
            "status": "created",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_run(self, run: Dict[str, Any]) -> Path:
        out = self.root / "data" / "pilot_operations" / "pilot_runs" / f"{run['pilot_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(run, indent=2, sort_keys=True), encoding="utf-8")
        return out
