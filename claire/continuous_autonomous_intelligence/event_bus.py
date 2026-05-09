from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import SignalEvent


class SignalEventBus:
    def __init__(self) -> None:
        self.events: Dict[str, SignalEvent] = {}

    def publish(self, event_type: str, topic: str, payload: Optional[dict] = None, priority: int = 5) -> SignalEvent:
        seed = f"{event_type}|{topic}|{payload}|{len(self.events)}"
        event_id = "event_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        event = SignalEvent(
            event_id=event_id,
            event_type=event_type,
            topic=topic,
            payload=payload or {},
            priority=priority,
        )
        self.events[event_id] = event
        return event

    def next_event(self) -> Optional[SignalEvent]:
        candidates = [event for event in self.events.values() if event.status == "new"]
        if not candidates:
            return None
        return sorted(candidates, key=lambda event: event.priority, reverse=True)[0]

    def mark_processing(self, event_id: str) -> None:
        self.events[event_id].status = "processing"

    def mark_done(self, event_id: str) -> None:
        self.events[event_id].status = "done"

    def snapshot(self) -> List[dict]:
        return [event.to_dict() for event in self.events.values()]
