from __future__ import annotations

from typing import Dict, List


class RuntimeHealthDashboard:
    def build(
        self,
        workers: List[dict],
        shards: List[dict],
        partitions: List[dict],
        telemetry: Dict[str, object],
    ) -> Dict[str, object]:
        degraded_workers = [worker for worker in workers if worker.get("status") in {"degraded", "error"}]
        inactive_shards = [shard for shard in shards if shard.get("status") != "active"]
        total_queue_depth = sum(int(partition.get("queue_depth", 0)) for partition in partitions)

        if degraded_workers or inactive_shards:
            status = "attention_required"
        elif total_queue_depth > 100:
            status = "backlog_warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "worker_count": len(workers),
            "degraded_worker_count": len(degraded_workers),
            "shard_count": len(shards),
            "inactive_shard_count": len(inactive_shards),
            "partition_count": len(partitions),
            "total_queue_depth": total_queue_depth,
            "telemetry_summary": telemetry,
        }
