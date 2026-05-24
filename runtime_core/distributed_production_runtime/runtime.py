from __future__ import annotations

from typing import Any, Dict, List

from .cross_campaign_fusion import CrossCampaignMemoryFusion
from .daemon_contract import RuntimeDaemonContract
from .health_dashboard import RuntimeHealthDashboard
from .production_regression_lock import ProductionRuntimeRegressionLock
from .queue_partitioning import QueuePartitioner
from .runtime_sharding import RuntimeShardManager
from .streaming_pipeline import StreamingIngestionPipeline
from .telemetry import ProductionTelemetry
from .worker_pool import DistributedWorkerPool
from .workload_balancer import WorkloadBalancer


class DistributedProductionRuntime:
    def __init__(self) -> None:
        self.shards = RuntimeShardManager()
        self.workers = DistributedWorkerPool()
        self.partitions = QueuePartitioner()
        self.streaming = StreamingIngestionPipeline()
        self.daemon = RuntimeDaemonContract()
        self.telemetry = ProductionTelemetry()
        self.fusion = CrossCampaignMemoryFusion()
        self.dashboard = RuntimeHealthDashboard()
        self.regression = ProductionRuntimeRegressionLock()

    def bootstrap(self, shard_count: int = 2, workers_per_shard: int = 2) -> None:
        for index in range(shard_count):
            shard = self.shards.create_shard(region=f"local-{index+1}", capacity=workers_per_shard * 5)
            for _ in range(workers_per_shard):
                self.workers.add_worker(shard_id=shard.shard_id)

    def run_cycle(
        self,
        topic: str,
        payload: Dict[str, object],
        campaigns: List[Dict[str, object]] | None = None,
    ) -> Dict[str, Any]:
        if not self.shards.shards:
            self.bootstrap()

        daemon_state = self.daemon.start()
        stream_event = self.streaming.accept(topic, payload)
        partition = self.partitions.assign_topic(topic)

        shard = self.shards.least_loaded_shard()
        if shard is not None:
            partition.assigned_shard_id = shard.shard_id
            self.shards.assign_partition(shard.shard_id, partition.partition_id)

        balancer = WorkloadBalancer(self.shards, self.workers)
        assignment = balancer.select_worker(topic)

        self.telemetry.record("stream_events_accepted", 1, tags={"topic": topic})
        self.telemetry.record("queue_depth", float(partition.queue_depth), tags={"partition_id": partition.partition_id})

        if assignment["status"] == "assigned" and assignment["worker_id"]:
            self.workers.record_processed(str(assignment["worker_id"]))
            self.telemetry.record("worker_assignments", 1, tags={"worker_id": assignment["worker_id"]})
        else:
            self.telemetry.record("assignment_failures", 1)

        daemon_tick = self.daemon.tick()
        fusion = self.fusion.fuse(campaigns or [])
        telemetry_summary = self.telemetry.summarize()
        health = self.dashboard.build(
            workers=self.workers.snapshot(),
            shards=self.shards.snapshot(),
            partitions=self.partitions.snapshot(),
            telemetry=telemetry_summary,
        )

        output: Dict[str, Any] = {
            "layer": "distributed_production_runtime",
            "versions": {
                "distributed_worker_pool": "v17.31",
                "queue_partitioning": "v17.32",
                "runtime_sharding": "v17.33",
                "workload_balancer": "v17.34",
                "streaming_pipeline": "v17.35",
                "daemon_contract": "v17.36",
                "cross_campaign_fusion": "v17.37",
                "production_telemetry": "v17.38",
                "runtime_health_dashboard": "v17.39",
                "production_regression_lock": "v17.40",
            },
            "governance_boundary": "production_contract_no_unreviewed_external_action",
            "daemon": {
                "start": daemon_state,
                "tick": daemon_tick,
            },
            "streaming": {
                "accepted": stream_event.to_dict(),
                "recent_batch": self.streaming.batch(),
            },
            "partitions": self.partitions.snapshot(),
            "shards": self.shards.snapshot(),
            "workers": self.workers.snapshot(),
            "workload_assignment": assignment,
            "cross_campaign_fusion": fusion,
            "telemetry": telemetry_summary,
            "health": health,
        }

        output["regression"] = self.regression.validate(output)
        return output
