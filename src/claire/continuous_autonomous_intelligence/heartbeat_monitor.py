from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List


class HeartbeatMonitor:
    def assess(self, workers: List[dict]) -> Dict[str, object]:
        stale = []
        healthy = []

        for worker in workers:
            heartbeat = worker.get("last_heartbeat_at")
            if not heartbeat:
                stale.append(worker.get("worker_id"))
                continue

            try:
                dt = datetime.fromisoformat(str(heartbeat).replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
            except Exception:
                age_seconds = 999999

            if age_seconds > 300:
                stale.append(worker.get("worker_id"))
            else:
                healthy.append(worker.get("worker_id"))

        return {
            "healthy_workers": healthy,
            "stale_workers": stale,
            "status": "healthy" if not stale else "attention_required",
        }
