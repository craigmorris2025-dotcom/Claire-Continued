from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def _load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))

def build_unified_runtime_dashboard(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()
    runtime = base / "data" / "runtime"
    return {
        "dashboard": "unified_runtime_dashboard",
        "status": "available",
        "runtime_state": _load(runtime / "runtime_state.json"),
        "live_runtime_dashboard_state": _load(runtime / "live_runtime_dashboard_state.json"),
        "runtime_manifest": _load(runtime / "runtime_manifest.json"),
        "active_module_registry": _load(runtime / "active_module_registry.json"),
        "core_runtime_lock": _load(runtime / "core_runtime_lock.json"),
        "rollback_validation": _load(runtime / "rollback_validation.json"),
    }
