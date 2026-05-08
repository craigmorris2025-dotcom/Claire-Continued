from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class InternetAuditLog:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_event(self, url: str, decision: str, reason: str) -> Dict[str, Any]:
        return {
            "record_type": "internet_audit_event",
            "url": url,
            "decision": decision,
            "reason": reason,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_event(self, event: Dict[str, Any]) -> Path:
        safe = event["created_at_utc"].replace(":", "-")
        out = self.root / "data" / "live_connectivity" / "internet_audit_logs" / f"internet_audit_{safe}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(event, indent=2, sort_keys=True), encoding="utf-8")
        return out
