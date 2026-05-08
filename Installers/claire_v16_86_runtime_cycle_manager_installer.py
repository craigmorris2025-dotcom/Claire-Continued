from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/autonomy/runtime_cycle_manager.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


RUNTIME_CYCLE_STATE_PATH = Path("data/autonomy/runtime_cycle_state.json")

TERMINAL_REASONS = {
    "max_cycles_reached",
    "no_queued_tasks",
    "operator_stop",
    "blocked_by_governance",
    "cycle_completed",
}


def _load_cycle_history() -> List[Dict[str, Any]]:
    if not RUNTIME_CYCLE_STATE_PATH.exists():
        return []
    try:
        data = json.loads(RUNTIME_CYCLE_STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("cycles", [])
        return data if isinstance(data, list) else []
    except Exception:
        return []


def start_runtime_cycle(
    cycle_name: str = "autonomous_runtime_cycle",
    max_cycles: int = 3,
    operator_approved: bool = True,
) -> Dict[str, Any]:
    max_cycles = max(1, min(25, int(max_cycles)))

    cycles = _load_cycle_history()
    active_cycle = {
        "version": "16.86",
        "cycle_id": f"cycle_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "cycle_name": cycle_name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "max_cycles": max_cycles,
        "current_cycle": 0,
        "operator_approved": operator_approved,
        "status": "running" if operator_approved else "blocked",
        "stop_reason": None if operator_approved else "blocked_by_governance",
        "events": [],
    }

    cycles.append(active_cycle)
    RUNTIME_CYCLE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_CYCLE_STATE_PATH.write_text(json.dumps({"version": "16.86", "cycles": cycles}, indent=2), encoding="utf-8")
    return active_cycle


def advance_runtime_cycle(cycle_id: str, event: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cycles = _load_cycle_history()

    for cycle in cycles:
        if cycle.get("cycle_id") == cycle_id:
            if cycle.get("status") != "running":
                return cycle

            cycle["current_cycle"] = int(cycle.get("current_cycle", 0)) + 1
            cycle.setdefault("events", []).append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": event or {"type": "cycle_advanced"},
            })

            if cycle["current_cycle"] >= int(cycle.get("max_cycles", 1)):
                cycle["status"] = "completed"
                cycle["stop_reason"] = "max_cycles_reached"
                cycle["completed_at"] = datetime.now(timezone.utc).isoformat()

            RUNTIME_CYCLE_STATE_PATH.write_text(json.dumps({"version": "16.86", "cycles": cycles}, indent=2), encoding="utf-8")
            return cycle

    raise ValueError(f"Cycle not found: {cycle_id}")


def stop_runtime_cycle(cycle_id: str, reason: str = "operator_stop") -> Dict[str, Any]:
    if reason not in TERMINAL_REASONS:
        raise ValueError(f"Invalid stop reason: {reason}")

    cycles = _load_cycle_history()

    for cycle in cycles:
        if cycle.get("cycle_id") == cycle_id:
            cycle["status"] = "stopped"
            cycle["stop_reason"] = reason
            cycle["stopped_at"] = datetime.now(timezone.utc).isoformat()
            RUNTIME_CYCLE_STATE_PATH.write_text(json.dumps({"version": "16.86", "cycles": cycles}, indent=2), encoding="utf-8")
            return cycle

    raise ValueError(f"Cycle not found: {cycle_id}")
""")

print("v16.86 runtime cycle manager installed.")
