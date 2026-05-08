from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/orchestration/bounded_orchestration_scheduler.py", r"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.orchestration.intelligence_task_registry import (
    list_intelligence_tasks,
    update_intelligence_task_state,
)

SCHEDULER_STATE_PATH = Path("data/orchestration/bounded_orchestration_scheduler.json")

async def _execute_task(task: Dict[str, Any]) -> Dict[str, Any]:
    task_id = task["task_id"]
    update_intelligence_task_state(task_id, "running", "Scheduler started task.")
    await asyncio.sleep(0)
    update_intelligence_task_state(task_id, "completed", "Scheduler completed bounded placeholder execution.")
    return {
        "task_id": task_id,
        "title": task.get("title"),
        "task_type": task.get("task_type"),
        "status": "completed",
        "priority": task.get("priority", 5),
    }

async def run_bounded_orchestration_scheduler_async(max_concurrent: int = 3, max_tasks: int = 10) -> Dict[str, Any]:
    max_concurrent = max(1, min(10, int(max_concurrent)))
    max_tasks = max(1, min(50, int(max_tasks)))

    queued = sorted(
        list_intelligence_tasks("queued"),
        key=lambda t: int(t.get("priority", 5)),
        reverse=True,
    )[:max_tasks]

    semaphore = asyncio.Semaphore(max_concurrent)

    async def guarded(task: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            try:
                return await _execute_task(task)
            except Exception as exc:
                try:
                    update_intelligence_task_state(task["task_id"], "failed", str(exc))
                except Exception:
                    pass
                return {"task_id": task.get("task_id"), "status": "failed", "error": str(exc)}

    records = await asyncio.gather(*(guarded(task) for task in queued)) if queued else []

    state = {
        "version": "16.82",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "max_concurrent": max_concurrent,
        "selected_task_count": len(queued),
        "records": records,
        "note": "Bounded scheduler uses controlled concurrency and placeholder execution only.",
    }

    SCHEDULER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULER_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state

def run_bounded_orchestration_scheduler(max_concurrent: int = 3, max_tasks: int = 10) -> Dict[str, Any]:
    return asyncio.run(run_bounded_orchestration_scheduler_async(max_concurrent=max_concurrent, max_tasks=max_tasks))
""")

print("v16.82 bounded orchestration scheduler installed.")
