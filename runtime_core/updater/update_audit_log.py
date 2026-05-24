"""
Claire update audit log.

v5.48 bootstrap:
- Writes append-only JSON logs for update attempts, installs, and rollback actions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timezone
import json
import uuid


class UpdateAuditLog:
    """Append JSON audit events to data/update_logs."""

    def __init__(self, project_root: Path) -> None:
        self.log_dir = project_root / "data" / "update_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write(self, event_type: str, payload: Dict[str, Any]) -> Path:
        event = {
            "event_id": "upd_" + uuid.uuid4().hex[:12],
            "event_type": event_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        path = self.log_dir / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event['event_id']}.json"
        path.write_text(json.dumps(event, indent=2, default=str), encoding="utf-8")
        return path


__all__ = ["UpdateAuditLog"]
