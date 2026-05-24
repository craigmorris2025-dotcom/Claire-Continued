from __future__ import annotations

from typing import Dict

from .event_bus import SignalEventBus
from .heartbeat_monitor import HeartbeatMonitor
from .worker_registry import WorkerRegistry


class RuntimeSupervisor:
    def __init__(self, workers: WorkerRegistry, bus: SignalEventBus) -> None:
        self.workers = workers
        self.bus = bus
        self.heartbeat = HeartbeatMonitor()

    def tick(self) -> Dict[str, object]:
        worker_snapshot = self.workers.snapshot()
        heartbeat = self.heartbeat.assess(worker_snapshot)

        event = self.bus.next_event()
        if event is None:
            return {
                "status": "idle",
                "heartbeat": heartbeat,
                "processed_event": None,
                "boundary": "supervisor does not perform unreviewed external action",
            }

        available = [worker for worker in self.workers.workers.values() if worker.status == "idle"]
        if not available:
            return {
                "status": "no_available_worker",
                "heartbeat": heartbeat,
                "processed_event": None,
            }

        worker = available[0]
        self.workers.set_status(worker.worker_id, "processing")
        self.bus.mark_processing(event.event_id)

        # Foundation-only processing. Real ingestion is delegated through governed adapters.
        self.bus.mark_done(event.event_id)
        self.workers.record_success(worker.worker_id)

        return {
            "status": "processed",
            "worker_id": worker.worker_id,
            "event_id": event.event_id,
            "topic": event.topic,
            "heartbeat": heartbeat,
            "boundary": "bounded internal orchestration only",
        }
