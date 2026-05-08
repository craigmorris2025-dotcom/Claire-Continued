"""Claire v16.49 Master Control Action Log.

Append-only action trace for governed command attempts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = ROOT / "data" / "runtime"
ACTION_LOG_PATH = RUNTIME_DIR / "master_control_action_log.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_action_log() -> Dict[str, Any]:
    if not ACTION_LOG_PATH.exists():
        return {"version": "v16.49", "layer": "master_control_action_log", "actions": []}
    try:
        data = json.loads(ACTION_LOG_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("actions"), list):
            return data
    except Exception:
        pass
    return {"version": "v16.49", "layer": "master_control_action_log", "actions": []}


def append_master_control_action(action: Dict[str, Any]) -> Dict[str, Any]:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    log = read_action_log()
    entry = {
        "timestamp": _now(),
        "command": action.get("command", "unknown"),
        "status": action.get("status", "unknown"),
        "accepted": bool(action.get("accepted", False)),
        "reason": action.get("reason"),
        "rollback_linkage": action.get("rollback_linkage", "installer_backup"),
        "mutation_performed": bool(action.get("mutation_performed", False)),
        "protected_runtime_spine": "preserved",
    }
    log["actions"].append(entry)
    log["latest"] = entry
    ACTION_LOG_PATH.write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log

if __name__ == "__main__":
    print(json.dumps(append_master_control_action({"command": "bootstrap", "status": "recorded"}), indent=2))
