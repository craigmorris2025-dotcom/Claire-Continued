from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_runtime_intelligence(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()
    path = base / "data" / "runtime" / "runtime_intelligence.json"
    if not path.exists():
        return {"status": "not_available", "message": "Run python tools/runtime_intelligence_layer.py first."}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
