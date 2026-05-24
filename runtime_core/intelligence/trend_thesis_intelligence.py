from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_trend_thesis_intelligence(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()
    path = base / "data" / "intelligence" / "trend_thesis_intelligence.json"
    if not path.exists():
        return {"status": "not_available", "message": "Run python tools/trend_thesis_intelligence_upgrade.py first."}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
