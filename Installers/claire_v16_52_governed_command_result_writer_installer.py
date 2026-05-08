from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/runtime/governed_command_result_writer.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


COMMAND_RESULTS_PATH = Path("data/runtime/runtime_command_results.json")


def _load_results() -> List[Dict[str, Any]]:
    if not COMMAND_RESULTS_PATH.exists():
        return []
    try:
        data = json.loads(COMMAND_RESULTS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def write_governed_command_result(result: Dict[str, Any]) -> Dict[str, Any]:
    COMMAND_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **result,
    }

    results = _load_results()
    results.append(record)
    COMMAND_RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return record
""")

print("v16.52 governed command result writer installed.")
