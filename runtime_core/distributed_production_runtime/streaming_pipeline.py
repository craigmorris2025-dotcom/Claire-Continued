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
