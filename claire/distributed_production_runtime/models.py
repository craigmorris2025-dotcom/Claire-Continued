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
