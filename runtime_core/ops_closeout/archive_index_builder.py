from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class ArchiveIndexBuilder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_index(self, archive_paths: List[str]) -> Dict[str, Any]:
        return {"record_type": "archive_index", "archive_paths": archive_paths, "created_at_utc": datetime.now(timezone.utc).isoformat()}

    def export_index(self, index: Dict[str, Any]) -> Path:
        out = self.root / "data" / "ops_closeout" / "archive_indexes" / "archive_index.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
        return out
