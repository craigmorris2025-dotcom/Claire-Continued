from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_portfolio_breakthrough_routing(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()
    path = base / "data" / "intelligence" / "portfolio_breakthrough_routing.json"
    if not path.exists():
        return {"status": "not_available", "message": "Run python tools/portfolio_breakthrough_routing_upgrade.py first."}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
