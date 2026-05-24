from __future__ import annotations

from typing import Dict

from .runtime_sharding import RuntimeShardManager
from .worker_pool import DistributedWorkerPool


class WorkloadBalancer:
    def __init__(self, shards: RuntimeShardManager, workers: DistributedWorkerPool) -> None:
        self.shards = shards
        self.workers = workers

    def select_worker(self, topic: str) -> Dict[str, object]:
        shard = self.shards.least_loaded_shard()
        if shard is None:
            return {
                "status": "no_shard_available",
                "worker_id": None,
                "shard_id": None,
                "reason": "No active shard available.",
            }

        worker = self.workers.least_loaded(shard.shard_id)
        if worker is None:
            return {
                "status": "no_worker_available",
                "worker_id": None,
                "shard_id": shard.shard_id,
                "reason": "No available worker on selected shard.",
            }

        worker.status = "active"
        worker.load = min(1.0, worker.load + 0.1)
        shard.current_load = min(1.0, shard.current_load + 0.05)

        return {
            "status": "assigned",
            "topic": topic,
            "worker_id": worker.worker_id,
            "shard_id": shard.shard_id,
            "reason": "Least-loaded active shard and worker selected.",
        }
