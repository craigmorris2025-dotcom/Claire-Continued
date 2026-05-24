from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeGraphState:
    version: str = "v19.84.0"
    runtime_name: str = "Claire Syntalion Runtime Graph"
    enabled: bool = False
    state: str = "idle"
    mode: str = "deterministic"
    last_cycle_at: Optional[str] = None
    active_route: Optional[str] = None
    terminal_state: str = "no_active_run"
    governance_state: str = "ready"
    continuous_runtime: Dict[str, Any] = field(default_factory=lambda: {
        "implemented": False,
        "reason": "continuous loop is not started by this endpoint contract build",
        "safe_state": "idle"
    })
    lifecycle: Dict[str, Any] = field(default_factory=lambda: {
        "stage_count": 30,
        "current_stage": None,
        "completed_stages": [],
        "skipped_by_route": [],
        "evidence_required": True,
        "confidence_required": True
    })
    route_graph: Dict[str, Any] = field(default_factory=lambda: {
        "root": "signal_governance_to_trend_thesis",
        "routes": [
            "portfolio_intelligence",
            "acquisition_intelligence",
            "breakthrough_system_transformation"
        ],
        "default_path": "portfolio_intelligence",
        "breakthrough_escalation": "conditional"
    })
    web_governance: Dict[str, Any] = field(default_factory=lambda: {
        "live_web_claimed": False,
        "provider_status": "unverified",
        "dry_run_available": None,
        "live_available": None,
        "fail_closed": True,
        "note": "live web state must be supplied by governed provider routes, not fabricated here"
    })
    latest_output_summary: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        self.updated_at = utc_now()
        return asdict(self)


class RuntimeGraphStore:
    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / "data" / "runtime_graph"
        self.state_path = self.data_dir / "runtime_state.json"
        self.queue_path = self.data_dir / "review_queue.json"

    def ensure(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.write_state(RuntimeGraphState())
        if not self.queue_path.exists():
            self.queue_path.write_text(json.dumps({
                "version": "v19.84.0",
                "queue": [],
                "count": 0,
                "updated_at": utc_now(),
                "note": "review queue exists; no fake reviews are inserted"
            }, indent=2), encoding="utf-8")

    def read_state(self) -> Dict[str, Any]:
        self.ensure()
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeGraphState(
                governance_state="degraded",
                errors=[{"type": "state_read_error", "detail": str(exc)}],
            ).to_dict()

    def write_state(self, state: RuntimeGraphState | Dict[str, Any]) -> Dict[str, Any]:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = state.to_dict() if isinstance(state, RuntimeGraphState) else dict(state)
        payload["updated_at"] = utc_now()
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def read_queue(self) -> Dict[str, Any]:
        self.ensure()
        try:
            payload = json.loads(self.queue_path.read_text(encoding="utf-8"))
            payload["count"] = len(payload.get("queue", []))
            payload["updated_at"] = utc_now()
            return payload
        except Exception as exc:
            return {
                "version": "v19.84.0",
                "queue": [],
                "count": 0,
                "updated_at": utc_now(),
                "errors": [{"type": "queue_read_error", "detail": str(exc)}],
            }
