from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/orchestration/intelligence_task_registry.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

TASK_REGISTRY_PATH = Path("data/orchestration/intelligence_task_registry.json")

VALID_TASK_TYPES = {
    "source_probe",
    "live_ingestion",
    "evidence_review",
    "signal_analysis",
    "thesis_update",
    "portfolio_review",
    "buyer_readiness_review",
}

VALID_STATES = {"queued", "running", "completed", "blocked", "failed", "quarantined"}

def _load_tasks() -> List[Dict[str, Any]]:
    if not TASK_REGISTRY_PATH.exists():
        return []
    try:
        data = json.loads(TASK_REGISTRY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def register_intelligence_task(
    task_type: str,
    title: str,
    payload: Dict[str, Any] | None = None,
    priority: int = 5,
    owner: str = "runtime",
) -> Dict[str, Any]:
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"Invalid intelligence task type: {task_type}")

    priority = max(1, min(10, int(priority)))

    task = {
        "version": "16.81",
        "task_id": f"task_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "title": title,
        "payload": payload or {},
        "priority": priority,
        "owner": owner,
        "state": "queued",
        "attempts": 0,
    }

    TASK_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tasks = _load_tasks()
    tasks.append(task)
    TASK_REGISTRY_PATH.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    return task

def list_intelligence_tasks(state: str | None = None) -> List[Dict[str, Any]]:
    tasks = _load_tasks()
    if state is None:
        return tasks
    return [task for task in tasks if task.get("state") == state]

def update_intelligence_task_state(task_id: str, state: str, note: str | None = None) -> Dict[str, Any]:
    if state not in VALID_STATES:
        raise ValueError(f"Invalid task state: {state}")

    tasks = _load_tasks()
    for task in tasks:
        if task.get("task_id") == task_id:
            task["state"] = state
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            if note:
                task["note"] = note
            TASK_REGISTRY_PATH.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
            return task

    raise ValueError(f"Task not found: {task_id}")
""")

print("v16.81 intelligence task registry installed.")
