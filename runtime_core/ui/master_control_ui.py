
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path.cwd()

RUNTIME_FILES = {
    "master_control_state": "data/runtime/master_control_state.json",
    "runtime_state": "data/runtime/runtime_state.json",
    "unified_runtime_dashboard": "data/runtime/unified_runtime_dashboard.json",
    "runtime_control_center": "data/runtime/runtime_control_center.json",
    "runtime_intelligence": "data/runtime/runtime_intelligence.json",
    "runtime_recovery_state": "data/runtime/runtime_recovery_state.json",
}

INTELLIGENCE_FILES = {
    "lifecycle_quality_score": "data/intelligence/lifecycle_quality_score.json",
    "trend_thesis_intelligence": "data/intelligence/trend_thesis_intelligence.json",
    "portfolio_breakthrough_routing": "data/intelligence/portfolio_breakthrough_routing.json",
}

def _read_json(relative_path: str) -> Dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        return {"status": "missing", "path": relative_path}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "unreadable", "path": relative_path, "error": str(exc)}

def build_master_control_ui_state() -> Dict[str, Any]:
    return {
        "version": "16.46",
        "mode": "read_only",
        "runtime": {name: _read_json(path) for name, path in RUNTIME_FILES.items()},
        "intelligence": {name: _read_json(path) for name, path in INTELLIGENCE_FILES.items()},
    }
