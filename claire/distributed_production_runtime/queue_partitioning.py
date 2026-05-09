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
