from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class ResumePointWriter:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_resume_point(self, version: str, next_focus: List[str]) -> Dict[str, Any]:
        return {"record_type": "resume_point", "version": version, "next_focus": next_focus, "created_at_utc": datetime.now(timezone.utc).isoformat()}

    def export_resume_point(self, point: Dict[str, Any]) -> Path:
        out = self.root / "data" / "ops_closeout" / "resume_points" / f"resume_{point['version'].replace('.','_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(point, indent=2, sort_keys=True), encoding="utf-8")
        return out
