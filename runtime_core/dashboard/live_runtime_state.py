from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_live_runtime_state(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()
    path = base / "data" / "runtime" / "live_runtime_dashboard_state.json"
    if not path.exists():
        return {"status": "not_available", "message": "Run python tools/live_runtime_dashboard_state.py first."}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
