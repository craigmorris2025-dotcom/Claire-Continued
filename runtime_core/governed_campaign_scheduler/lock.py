from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .time_utils import utc_now


class SchedulerLock:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "governed_campaign_scheduler"
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "scheduler.lock"

    def acquire(self, owner: str) -> Dict[str, object]:
        if self.path.exists():
            try:
                existing = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                existing = {"owner": "unknown"}
            return {
                "acquired": False,
                "reason": "Scheduler lock already exists.",
                "existing": existing,
            }

        payload = {"owner": owner, "acquired_at": utc_now()}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return {"acquired": True, "lock": payload}

    def release(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def status(self) -> Dict[str, object]:
        if not self.path.exists():
            return {"locked": False}
        try:
            return {"locked": True, "lock": json.loads(self.path.read_text(encoding="utf-8"))}
        except Exception:
            return {"locked": True, "lock": {"error": "unreadable lock"}}
