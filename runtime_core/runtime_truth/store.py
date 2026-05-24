from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

VERSION = "v19.84.1"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def default_state() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "runtime_name": "Claire Syntalion Runtime Truth",
        "state": "idle",
        "mode": "deterministic",
        "app_boots": True,
        "active_route": None,
        "terminal_state": "no_active_run",
        "governance_state": "ready",
        "continuous_runtime": {
            "status": "not_started",
            "implemented": False,
            "truthful_note": "Continuous runtime loop is not claimed active by this endpoint layer."
        },
        "web_governance": {
            "provider_status": "unverified",
            "live_available": False,
            "fail_closed": True,
            "truthful_note": "Live web must be proven by governed provider routes before being marked active."
        },
        "lifecycle": {
            "stage_count": 30,
            "route_graph": "signal_governance_to_trend_thesis_to_route_selection",
            "current_stage": None,
            "selected_route_stages": [],
            "skipped_by_route": []
        },
        "latest_output_summary": None,
        "errors": [],
        "updated_at": utc_now()
    }

class RuntimeTruthStore:
    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / "data" / "runtime_truth"
        self.state_path = self.data_dir / "runtime_state.json"
        self.queue_path = self.data_dir / "review_queue.json"

    def ensure(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.state_path.write_text(json.dumps(default_state(), indent=2), encoding="utf-8")
        if not self.queue_path.exists():
            self.queue_path.write_text(json.dumps({
                "version": VERSION,
                "queue": [],
                "count": 0,
                "truthful_note": "Review queue exists but contains no fabricated review items.",
                "updated_at": utc_now()
            }, indent=2), encoding="utf-8")

    def read_state(self) -> Dict[str, Any]:
        self.ensure()
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            data = default_state()
            data["governance_state"] = "degraded"
            data["errors"] = [{"type": "runtime_state_read_error", "detail": str(exc)}]
        data["updated_at"] = utc_now()
        return data

    def write_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.ensure()
        payload = dict(data)
        payload["updated_at"] = utc_now()
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def read_queue(self) -> Dict[str, Any]:
        self.ensure()
        try:
            data = json.loads(self.queue_path.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {
                "version": VERSION,
                "queue": [],
                "count": 0,
                "errors": [{"type": "review_queue_read_error", "detail": str(exc)}],
            }
        data["count"] = len(data.get("queue", []))
        data["updated_at"] = utc_now()
        return data
