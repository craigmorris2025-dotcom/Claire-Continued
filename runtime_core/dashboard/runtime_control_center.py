from __future__ import annotations
import json
from pathlib import Path

def load_runtime_control_center(root=None):
    base = Path(root) if root else Path.cwd()
    path = base / "data" / "runtime" / "runtime_control_center.json"
    if not path.exists():
        return {"status": "not_available"}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
