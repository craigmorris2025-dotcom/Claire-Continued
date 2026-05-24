from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUOUS_DIR = ROOT / "data" / "continuous_runtime"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: dict) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback
    return fallback


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    installed = "--installed" in argv
    task_name = "ClaireContinuousRuntimeTick"
    now = utc_now()

    scheduler_state = read_json(CONTINUOUS_DIR / "scheduler_state.json", {})
    scheduler_state["task_runner_installed"] = installed
    scheduler_state["task_runner_name"] = task_name if installed else None
    scheduler_state["heartbeat_status"] = "windows_task_scheduler_registered" if installed else "external_runner_not_installed"
    scheduler_state["updated_at"] = now
    write_json(CONTINUOUS_DIR / "scheduler_state.json", scheduler_state)

    status = read_json(CONTINUOUS_DIR / "status.json", {})
    scheduler_policy = status.get("scheduler_policy", {}) if isinstance(status.get("scheduler_policy"), dict) else {}
    scheduler_policy["task_runner_installed"] = installed
    scheduler_policy["task_runner_name"] = task_name if installed else None
    scheduler_policy["status"] = "windows_task_scheduler_registered" if installed else scheduler_policy.get("status", "bounded_scheduler_available_not_daemonized")
    scheduler_policy["manual_tick_endpoint"] = "/runtime/continuous/scheduler/tick"
    status["scheduler_policy"] = scheduler_policy
    status["updated_at"] = now
    write_json(CONTINUOUS_DIR / "status.json", status)

    print(json.dumps({"task_runner_installed": installed, "task_runner_name": task_name}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
