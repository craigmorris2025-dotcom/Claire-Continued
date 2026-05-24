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
