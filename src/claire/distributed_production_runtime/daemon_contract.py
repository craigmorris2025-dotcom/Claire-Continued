from __future__ import annotations

from typing import Dict

from .models import utc_now


class RuntimeDaemonContract:
    def __init__(self) -> None:
        self.status = "stopped"
        self.started_at = None
        self.last_tick_at = None
        self.tick_count = 0

    def start(self) -> Dict[str, object]:
        self.status = "running"
        self.started_at = utc_now()
        self.last_tick_at = self.started_at
        return self.snapshot()

    def tick(self) -> Dict[str, object]:
        if self.status != "running":
            return {"status": "not_running", "tick_count": self.tick_count}
        self.tick_count += 1
        self.last_tick_at = utc_now()
        return self.snapshot()

    def stop(self) -> Dict[str, object]:
        self.status = "stopped"
        self.last_tick_at = utc_now()
        return self.snapshot()

    def snapshot(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "started_at": self.started_at,
            "last_tick_at": self.last_tick_at,
            "tick_count": self.tick_count,
            "boundary": "contract_only_no_background_process_started_by_installer",
        }
