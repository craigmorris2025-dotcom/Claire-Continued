from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_master_control_state(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()

    path = base / "data" / "runtime" / "master_control_state.json"

    if not path.exists():
        return {
            "status": "not_available",
            "message": "Run python tools/master_control_layer_builder.py first.",
        }

    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
