from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import QueueItem


class AsyncIngestionQueue:
    def __init__(self) -> None:
        self.items: Dict[str, QueueItem] = {}

    def enqueue(self, query: str, priority: int = 5) -> QueueItem:
        item_id = "queue_" + hashlib.sha256(f"{query}|{priority}".encode("utf-8")).hexdigest()[:12]
        item = QueueItem(item_id=item_id, query=query, priority=priority)
        self.items[item_id] = item
        return item

    def next_item(self) -> Optional[QueueItem]:
        queued = [item for item in self.items.values() if item.status == "queued"]
        if not queued:
            return None
        return sorted(queued, key=lambda item: item.priority, reverse=True)[0]

    def mark_processing(self, item_id: str) -> None:
        self.items[item_id].status = "processing"
        self.items[item_id].attempts += 1

    def mark_done(self, item_id: str) -> None:
        self.items[item_id].status = "done"

    def mark_failed(self, item_id: str) -> None:
        item = self.items[item_id]
        item.status = "failed" if item.attempts >= item.max_attempts else "queued"

    def snapshot(self) -> List[dict]:
        return [item.__dict__.copy() for item in self.items.values()]
