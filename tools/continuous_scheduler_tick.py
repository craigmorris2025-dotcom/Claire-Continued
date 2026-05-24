from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.api.routes_continuous_runtime import run_scheduler_tick


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    query = os.environ.get(
        "PLATFORM_SCHEDULER_QUERY",
        "scheduled AI market signal existing system gap discovery breakthrough design portfolio acquirer",
    )
    result = run_scheduler_tick({"query": query})
    cycle = result.get("cycle", {})
    heartbeat = {
        "schema_version": "claire.scheduler_heartbeat.v1",
        "status": "tick_completed",
        "updated_at": utc_now(),
        "cycle_id": cycle.get("cycle_id"),
        "route": cycle.get("run_spine", {}).get("route_selected"),
        "stage_count": cycle.get("run_spine", {}).get("stage_count"),
        "scheduler_tick_count": result.get("scheduler_state", {}).get("tick_count"),
        "authority": result.get("authority", {}),
    }
    write_json(ROOT / "data" / "continuous_runtime" / "scheduler_heartbeat.json", heartbeat)
    print(json.dumps(heartbeat, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
