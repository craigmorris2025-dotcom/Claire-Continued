from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import WorkerState
from .models import utc_now


class WorkerRegistry:
    def __init__(self) -> None:
        self.workers: Dict[str, WorkerState] = {}

    def register(self, worker_type: str, assigned_topic: Optional[str] = None) -> WorkerState:
        seed = f"{worker_type}|{assigned_topic}|{len(self.workers)}"
        worker_id = "worker_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        worker = WorkerState(
            worker_id=worker_id,
            worker_type=worker_type,
            assigned_topic=assigned_topic,
            last_heartbeat_at=utc_now(),
        )
        self.workers[worker_id] = worker
        return worker

    def set_status(self, worker_id: str, status: str) -> None:
        self.workers[worker_id].status = status

    def record_success(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.processed_count += 1
        worker.status = "idle"
        worker.last_heartbeat_at = utc_now()

    def record_error(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.error_count += 1
        worker.status = "error"
        worker.last_heartbeat_at = utc_now()

    def snapshot(self) -> List[dict]:
        return [worker.to_dict() for worker in self.workers.values()]
