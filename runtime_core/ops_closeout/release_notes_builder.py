from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class ReleaseNotesBuilder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_notes(self, version: str, highlights: List[str]) -> Dict[str, Any]:
        return {"record_type": "release_notes", "version": version, "highlights": highlights, "created_at_utc": datetime.now(timezone.utc).isoformat()}

    def export_notes(self, notes: Dict[str, Any]) -> Path:
        out = self.root / "data" / "ops_closeout" / "release_notes" / f"release_notes_{notes['version'].replace('.','_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(notes, indent=2, sort_keys=True), encoding="utf-8")
        return out
