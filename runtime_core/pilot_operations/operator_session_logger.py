from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class OperatorSessionLogger:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def log_session(self, session_id: str, action: str, notes: str = "") -> Dict[str, Any]:
        return {
            "record_type": "operator_session",
            "session_id": session_id,
            "action": action,
            "notes": notes,
            "logged_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_session(self, record: Dict[str, Any]) -> Path:
        out = self.root / "data" / "pilot_operations" / "operator_sessions" / f"{record['session_id']}_{record['logged_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return out
