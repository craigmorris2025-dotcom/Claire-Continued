from __future__ import annotations

from typing import Dict, List

from .async_ingestion_queue import AsyncIngestionQueue


class ContinuousMonitor:
    def __init__(self, queue: AsyncIngestionQueue | None = None) -> None:
        self.queue = queue or AsyncIngestionQueue()

    def seed_campaign(self, topics: List[str]) -> Dict[str, object]:
        created = [self.queue.enqueue(topic, priority=5).__dict__.copy() for topic in topics]
        return {
            "status": "seeded",
            "mode": "bounded_monitoring_foundation",
            "created_items": created,
            "governance": "queued_only_no_external_fetch_without_policy",
        }

    def tick(self) -> Dict[str, object]:
        item = self.queue.next_item()
        if item is None:
            return {"status": "idle", "message": "No queued monitoring items."}

        self.queue.mark_processing(item.item_id)
        self.queue.mark_done(item.item_id)
        return {
            "status": "processed_stub",
            "item_id": item.item_id,
            "query": item.query,
            "boundary": "foundation tick only; no autonomous external action",
        }
