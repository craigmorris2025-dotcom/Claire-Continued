from __future__ import annotations
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional
import uuid

class RunEventStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._runs: Dict[str, Dict[str, Any]] = {}

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_run(self, label: str = "Claire run", metadata: Optional[Dict[str, Any]] = None) -> str:
        run_id = "evt_" + uuid.uuid4().hex[:12]
        now = self.now()
        with self._lock:
            self._runs[run_id] = {
                "event_run_id": run_id,
                "label": label,
                "status": "created",
                "created_at": now,
                "updated_at": now,
                "metadata": metadata or {},
                "events": [],
                "result": None,
                "error": None,
            }
        self.add(run_id, "created", "Run event stream created.", "launcher", 0)
        return run_id

    def add(self, run_id: str, event_type: str, message: str, stage: str = "runtime", progress: int | None = None, details: Optional[Dict[str, Any]] = None, level: str = "info") -> Dict[str, Any]:
        now = self.now()
        event = {
            "id": "ev_" + uuid.uuid4().hex[:10],
            "timestamp": now,
            "event_type": event_type,
            "stage": stage,
            "message": message,
            "progress": progress,
            "details": details or {},
            "level": level,
        }
        with self._lock:
            run = self._runs.setdefault(run_id, {
                "event_run_id": run_id, "label": "Claire run", "status": "created",
                "created_at": now, "updated_at": now, "metadata": {}, "events": [], "result": None, "error": None,
            })
            run["events"].append(event)
            run["updated_at"] = now
            if event_type in {"started", "running", "stage_started", "stage_complete"}:
                run["status"] = "running"
            elif event_type == "complete":
                run["status"] = "complete"
            elif event_type == "error":
                run["status"] = "error"
                run["error"] = message
        return event

    def set_result(self, run_id: str, result: Dict[str, Any]) -> None:
        with self._lock:
            if run_id in self._runs:
                self._runs[run_id]["result"] = result
                self._runs[run_id]["updated_at"] = self.now()

    def get(self, run_id: str, since: int | None = None) -> Dict[str, Any]:
        with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return {"status": "not_found", "event_run_id": run_id, "events": []}
            events = list(run["events"])
            if since is not None and since >= 0:
                events = events[since:]
            return {
                "status": run["status"],
                "event_run_id": run_id,
                "label": run["label"],
                "created_at": run["created_at"],
                "updated_at": run["updated_at"],
                "event_count": len(run["events"]),
                "events": events,
                "result": run["result"],
                "error": run["error"],
            }

    def list(self, limit: int = 25) -> Dict[str, Any]:
        with self._lock:
            runs = sorted(self._runs.values(), key=lambda r: r["created_at"], reverse=True)[:limit]
            return {
                "status": "success",
                "run_count": len(runs),
                "runs": [{
                    "event_run_id": r["event_run_id"], "label": r["label"], "status": r["status"],
                    "created_at": r["created_at"], "updated_at": r["updated_at"],
                    "event_count": len(r["events"]), "result": r["result"], "error": r["error"],
                } for r in runs],
            }

RUN_EVENTS = RunEventStore()
