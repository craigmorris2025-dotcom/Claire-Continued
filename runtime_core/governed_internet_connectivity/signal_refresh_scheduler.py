from __future__ import annotations

from typing import Dict, List


class SignalRefreshScheduler:
    CADENCE_HOURS = {
        "hourly": 1,
        "daily": 24,
        "weekly": 168,
        "monthly": 720,
    }

    def build_schedule(self, watchlist_items: List[dict]) -> Dict[str, object]:
        schedule = []
        for item in watchlist_items:
            cadence = item.get("cadence", "daily")
            schedule.append(
                {
                    "watch_id": item.get("watch_id"),
                    "topic": item.get("topic"),
                    "cadence": cadence,
                    "refresh_hours": self.CADENCE_HOURS.get(cadence, 24),
                    "status": item.get("status", "active"),
                }
            )
        return {
            "status": "schedule_ready",
            "schedule": schedule,
            "boundary": "schedule contract only; external scheduling requires runtime integration",
        }
