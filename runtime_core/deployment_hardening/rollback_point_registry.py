from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class RollbackPointRegistry:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def create_point(self, version: str, commit: str = "unknown") -> Dict[str, Any]:
        return {
            "record_type": "rollback_point",
            "version": version,
            "commit": commit,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_point(self, point: Dict[str, Any]) -> Path:
        out = self.root / "data" / "deployment_hardening" / "rollback_points" / f"rollback_{point['version'].replace('.','_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(point, indent=2, sort_keys=True), encoding="utf-8")
        return out
