from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import DistributedWorker
from .models import utc_now


class DistributedWorkerPool:
    def __init__(self) -> None:
        self.workers: Dict[str, DistributedWorker] = {}

    def add_worker(self, shard_id: str, worker_type: str = "distributed_ingestion_worker") -> DistributedWorker:
        worker_id = "dist_worker_" + hashlib.sha256(
            f"{shard_id}|{worker_type}|{len(self.workers)}".encode("utf-8")
        ).hexdigest()[:12]
        worker = DistributedWorker(worker_id=worker_id, shard_id=shard_id, worker_type=worker_type)
        self.workers[worker_id] = worker
        return worker

    def update_load(self, worker_id: str, load: float) -> None:
        worker = self.workers[worker_id]
        worker.load = max(0.0, min(1.0, load))
        worker.last_seen_at = utc_now()

    def record_processed(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.processed += 1
        worker.status = "idle"
        worker.last_seen_at = utc_now()

    def record_error(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.errors += 1
        worker.status = "degraded"
        worker.last_seen_at = utc_now()

    def least_loaded(self, shard_id: str | None = None) -> DistributedWorker | None:
        workers = list(self.workers.values())
        if shard_id is not None:
            workers = [worker for worker in workers if worker.shard_id == shard_id]
        available = [worker for worker in workers if worker.status in {"idle", "active"}]
        if not available:
            return None
        return sorted(available, key=lambda worker: worker.load)[0]

    def snapshot(self) -> List[dict]:
        return [worker.to_dict() for worker in self.workers.values()]
