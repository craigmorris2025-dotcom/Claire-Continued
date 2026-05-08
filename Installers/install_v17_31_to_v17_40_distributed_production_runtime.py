# Claire Syntalion Installer
# v17.31-v17.40 Distributed Intelligence & Production Runtime Infrastructure
#
# Place this file in the Claire project root and run:
#
#     python install_v17_31_to_v17_40_distributed_production_runtime.py
#
# Then test:
#
#     python -m pytest tests/distributed_production_runtime -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "distributed_production_runtime"
TESTS = ROOT / "tests" / "distributed_production_runtime"
DATA = ROOT / "data" / "distributed_production_runtime"
DOCS = ROOT / "docs" / "distributed_production_runtime"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v17.31-v17.40 Distributed Production Runtime Infrastructure...")

    write_file(LAYER / "__init__.py", """
from .runtime import DistributedProductionRuntime
from .worker_pool import DistributedWorkerPool
from .queue_partitioning import QueuePartitioner
from .runtime_sharding import RuntimeShardManager
from .workload_balancer import WorkloadBalancer
from .streaming_pipeline import StreamingIngestionPipeline
from .daemon_contract import RuntimeDaemonContract
from .cross_campaign_fusion import CrossCampaignMemoryFusion
from .telemetry import ProductionTelemetry
from .health_dashboard import RuntimeHealthDashboard
from .production_regression_lock import ProductionRuntimeRegressionLock

__all__ = [
    "DistributedProductionRuntime",
    "DistributedWorkerPool",
    "QueuePartitioner",
    "RuntimeShardManager",
    "WorkloadBalancer",
    "StreamingIngestionPipeline",
    "RuntimeDaemonContract",
    "CrossCampaignMemoryFusion",
    "ProductionTelemetry",
    "RuntimeHealthDashboard",
    "ProductionRuntimeRegressionLock",
]
""")

    write_file(LAYER / "models.py", """
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class DistributedWorker:
    worker_id: str
    shard_id: str
    worker_type: str = "distributed_ingestion_worker"
    status: str = "idle"
    load: float = 0.0
    processed: int = 0
    errors: int = 0
    last_seen_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueuePartition:
    partition_id: str
    topic_prefix: str
    queue_depth: int = 0
    assigned_shard_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeShard:
    shard_id: str
    region: str = "local"
    status: str = "active"
    capacity: int = 10
    current_load: float = 0.0
    assigned_partitions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StreamEvent:
    stream_id: str
    topic: str
    payload: Dict[str, Any]
    sequence: int
    status: str = "accepted"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TelemetryMetric:
    name: str
    value: float
    unit: str = "count"
    tags: Dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
""")

    write_file(LAYER / "worker_pool.py", """
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
""")

    write_file(LAYER / "queue_partitioning.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import QueuePartition


class QueuePartitioner:
    def __init__(self) -> None:
        self.partitions: Dict[str, QueuePartition] = {}

    def create_partition(self, topic_prefix: str, assigned_shard_id: str | None = None) -> QueuePartition:
        partition_id = "partition_" + hashlib.sha256(topic_prefix.encode("utf-8")).hexdigest()[:12]
        partition = QueuePartition(
            partition_id=partition_id,
            topic_prefix=topic_prefix,
            assigned_shard_id=assigned_shard_id,
        )
        self.partitions[partition_id] = partition
        return partition

    def assign_topic(self, topic: str) -> QueuePartition:
        for partition in self.partitions.values():
            if topic.startswith(partition.topic_prefix):
                partition.queue_depth += 1
                return partition

        prefix = topic[:3].lower() if topic else "gen"
        partition = self.create_partition(prefix)
        partition.queue_depth += 1
        return partition

    def snapshot(self) -> List[dict]:
        return [partition.to_dict() for partition in self.partitions.values()]
""")

    write_file(LAYER / "runtime_sharding.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import RuntimeShard


class RuntimeShardManager:
    def __init__(self) -> None:
        self.shards: Dict[str, RuntimeShard] = {}

    def create_shard(self, region: str = "local", capacity: int = 10) -> RuntimeShard:
        shard_id = "shard_" + hashlib.sha256(f"{region}|{len(self.shards)}".encode("utf-8")).hexdigest()[:12]
        shard = RuntimeShard(shard_id=shard_id, region=region, capacity=capacity)
        self.shards[shard_id] = shard
        return shard

    def assign_partition(self, shard_id: str, partition_id: str) -> None:
        shard = self.shards[shard_id]
        if partition_id not in shard.assigned_partitions:
            shard.assigned_partitions.append(partition_id)

    def least_loaded_shard(self) -> RuntimeShard | None:
        active = [shard for shard in self.shards.values() if shard.status == "active"]
        if not active:
            return None
        return sorted(active, key=lambda shard: shard.current_load)[0]

    def update_load(self, shard_id: str, current_load: float) -> None:
        self.shards[shard_id].current_load = max(0.0, min(1.0, current_load))

    def snapshot(self) -> List[dict]:
        return [shard.to_dict() for shard in self.shards.values()]
""")

    write_file(LAYER / "workload_balancer.py", """
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
""")

    write_file(LAYER / "streaming_pipeline.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import StreamEvent


class StreamingIngestionPipeline:
    def __init__(self) -> None:
        self.sequence = 0
        self.events: List[StreamEvent] = []

    def accept(self, topic: str, payload: Dict[str, object]) -> StreamEvent:
        self.sequence += 1
        stream_id = "stream_" + hashlib.sha256(f"{topic}|{self.sequence}".encode("utf-8")).hexdigest()[:12]
        event = StreamEvent(stream_id=stream_id, topic=topic, payload=payload, sequence=self.sequence)
        self.events.append(event)
        return event

    def batch(self, limit: int = 10) -> List[dict]:
        return [event.to_dict() for event in self.events[-limit:]]

    def snapshot(self) -> List[dict]:
        return [event.to_dict() for event in self.events]
""")

    write_file(LAYER / "daemon_contract.py", """
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
""")

    write_file(LAYER / "cross_campaign_fusion.py", """
from __future__ import annotations

from typing import Dict, List


class CrossCampaignMemoryFusion:
    def fuse(self, campaigns: List[Dict[str, object]]) -> Dict[str, object]:
        topic_counts: Dict[str, int] = {}
        total_confidence = 0.0

        for campaign in campaigns:
            total_confidence += float(campaign.get("confidence", 0.0))
            for topic in campaign.get("topics", []):
                topic_counts[str(topic)] = topic_counts.get(str(topic), 0) + 1

        repeated_topics = [topic for topic, count in topic_counts.items() if count > 1]
        avg_confidence = total_confidence / len(campaigns) if campaigns else 0.0

        return {
            "campaign_count": len(campaigns),
            "topic_counts": topic_counts,
            "repeated_topics": repeated_topics,
            "average_confidence": round(avg_confidence, 4),
            "fusion_status": "ready" if campaigns else "empty",
        }
""")

    write_file(LAYER / "telemetry.py", """
from __future__ import annotations

from typing import Dict, List

from .models import TelemetryMetric


class ProductionTelemetry:
    def __init__(self) -> None:
        self.metrics: List[TelemetryMetric] = []

    def record(self, name: str, value: float, unit: str = "count", tags: Dict[str, object] | None = None) -> TelemetryMetric:
        metric = TelemetryMetric(name=name, value=value, unit=unit, tags=tags or {})
        self.metrics.append(metric)
        return metric

    def summarize(self) -> Dict[str, object]:
        totals: Dict[str, float] = {}
        for metric in self.metrics:
            totals[metric.name] = totals.get(metric.name, 0.0) + metric.value
        return {
            "metric_count": len(self.metrics),
            "totals": totals,
            "metrics": [metric.to_dict() for metric in self.metrics],
        }
""")

    write_file(LAYER / "health_dashboard.py", """
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
""")

    write_file(LAYER / "production_regression_lock.py", """
from __future__ import annotations

from typing import Dict, List


class ProductionRuntimeRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "distributed_production_runtime":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "production_contract_no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        required = [
            "workers",
            "shards",
            "partitions",
            "streaming",
            "workload_assignment",
            "daemon",
            "telemetry",
            "health",
        ]
        for key in required:
            if key not in output:
                errors.append(f"Missing required output key: {key}")

        health = output.get("health", {})
        if isinstance(health, dict) and health.get("status") != "healthy":
            warnings.append(f"Health dashboard status: {health.get('status')}")

        return {
            "version": "v17.40",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "distributed_workers_present": "workers" in output,
                "sharding_present": "shards" in output,
                "partitioning_present": "partitions" in output,
                "telemetry_present": "telemetry" in output,
                "health_dashboard_present": "health" in output,
                "bounded_external_action": output.get("governance_boundary") == "production_contract_no_unreviewed_external_action",
            },
        }
""")

    write_file(LAYER / "runtime.py", """
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
""")

    write_file(TESTS / "test_distributed_production_runtime.py", """
from claire.distributed_production_runtime import DistributedProductionRuntime


def test_distributed_runtime_cycle_passes_regression():
    runtime = DistributedProductionRuntime()
    result = runtime.run_cycle(
        topic="governed research systems",
        payload={"confidence": 0.72, "signal": "demand increasing"},
        campaigns=[
            {"name": "campaign a", "topics": ["governed research systems"], "confidence": 0.7},
            {"name": "campaign b", "topics": ["governed research systems", "ai infra"], "confidence": 0.8},
        ],
    )

    assert result["layer"] == "distributed_production_runtime"
    assert result["regression"]["regression_status"] == "passed"
    assert result["workload_assignment"]["status"] == "assigned"
    assert result["health"]["status"] == "healthy"
    assert result["governance_boundary"] == "production_contract_no_unreviewed_external_action"


def test_bootstrap_creates_workers_and_shards():
    runtime = DistributedProductionRuntime()
    runtime.bootstrap(shard_count=3, workers_per_shard=2)

    assert len(runtime.shards.snapshot()) == 3
    assert len(runtime.workers.snapshot()) == 6


def test_cross_campaign_fusion_detects_repeated_topic():
    runtime = DistributedProductionRuntime()
    result = runtime.run_cycle(
        topic="market structure",
        payload={"confidence": 0.6},
        campaigns=[
            {"topics": ["market structure"], "confidence": 0.5},
            {"topics": ["market structure"], "confidence": 0.7},
        ],
    )

    assert "market structure" in result["cross_campaign_fusion"]["repeated_topics"]
""")

    write_file(DOCS / "v17_31_to_v17_40_distributed_production_runtime.md", """
# Claire v17.31-v17.40 Distributed Intelligence & Production Runtime Infrastructure

This build moves Claire from continuous orchestration foundations toward production-grade distributed runtime contracts.

## Included Builds

- v17.31 Distributed Worker Pool
- v17.32 Queue Partitioning
- v17.33 Runtime Sharding
- v17.34 Workload Balancer
- v17.35 Streaming Ingestion Pipeline
- v17.36 Runtime Daemon Contract
- v17.37 Cross-Campaign Memory Fusion
- v17.38 Production Telemetry
- v17.39 Runtime Health Dashboard
- v17.40 Production Runtime Regression Lock

## Governance Boundary

This layer creates production runtime structure but does not start background services, cloud workers, or unreviewed external actions.

The daemon module is a contract object only. The installer does not create a persistent process.
""")

    write_json(DATA / "distributed_production_runtime_manifest.json", {
        "installed_at": utc_now(),
        "layer": "distributed_production_runtime",
        "version_range": "v17.31-v17.40",
        "status": "installed",
        "governance_boundary": "production_contract_no_unreviewed_external_action",
        "capabilities": [
            "distributed_worker_pool",
            "queue_partitioning",
            "runtime_sharding",
            "workload_balancer",
            "streaming_ingestion_pipeline",
            "runtime_daemon_contract",
            "cross_campaign_memory_fusion",
            "production_telemetry",
            "runtime_health_dashboard",
            "production_regression_lock"
        ],
        "not_included_yet": [
            "real_cloud_deployment",
            "production_message_broker",
            "kubernetes_or_container_orchestration",
            "external_service_credentials",
            "unreviewed_external_actions",
            "persistent_background_process_started_by_installer"
        ],
        "tests": [
            "tests/distributed_production_runtime/test_distributed_production_runtime.py"
        ],
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.31-v17.40 Distributed Production Runtime Infrastructure")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/distributed_production_runtime -q")
    print("")
    print("Optional smoke test:")
    print("    python -c \"from claire.distributed_production_runtime import DistributedProductionRuntime; print(DistributedProductionRuntime().run_cycle('ai', {'confidence':0.7})['regression']['regression_status'])\"")


if __name__ == "__main__":
    main()
