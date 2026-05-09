
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ACTION_LOG_PATH = Path("data/runtime/master_control_action_log.json")

def append_master_control_action(entry: Dict[str, Any]) -> Dict[str, Any]:
    ACTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if ACTION_LOG_PATH.exists():
        try:
            log = json.loads(ACTION_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            log = []
    else:
        log = []

    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **entry}
    log.append(record)
    ACTION_LOG_PATH.write_text(json.dumps(log, indent=2), encoding="utf-8")
    return record
