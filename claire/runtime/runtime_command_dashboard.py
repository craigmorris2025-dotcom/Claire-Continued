
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


RESULTS_PATH = Path("data/runtime/runtime_command_results.json")
DASHBOARD_PATH = Path("data/runtime/runtime_command_dashboard.json")


def _load_results() -> List[Dict[str, Any]]:
    if not RESULTS_PATH.exists():
        return []
    try:
        data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def build_runtime_command_dashboard() -> Dict[str, Any]:
    results = _load_results()
    blocked = [r for r in results if r.get("status") == "blocked"]
    accepted = [r for r in results if r.get("status") in {"accepted", "ok"}]

    dashboard = {
        "version": "16.54",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_commands": len(results),
        "accepted_or_ok_commands": len(accepted),
        "blocked_commands": len(blocked),
        "latest_command": results[-1] if results else None,
        "status": "ready",
    }

    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    return dashboard
