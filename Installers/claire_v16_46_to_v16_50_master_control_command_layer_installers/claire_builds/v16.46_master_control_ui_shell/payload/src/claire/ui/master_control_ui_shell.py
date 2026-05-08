"""Claire v16.46 Master Control UI Shell.

Read-only renderer for governed runtime/intelligence state files.
This module intentionally performs no runtime mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = ROOT / "data" / "runtime"
INTELLIGENCE_DIR = ROOT / "data" / "intelligence"
OUTPUT_PATH = RUNTIME_DIR / "master_control_ui_shell.json"

STATE_FILES = {
    "master_control_state": RUNTIME_DIR / "master_control_state.json",
    "runtime_state": RUNTIME_DIR / "runtime_state.json",
    "unified_runtime_dashboard": RUNTIME_DIR / "unified_runtime_dashboard.json",
    "runtime_control_center": RUNTIME_DIR / "runtime_control_center.json",
    "runtime_intelligence": RUNTIME_DIR / "runtime_intelligence.json",
    "runtime_recovery_state": RUNTIME_DIR / "runtime_recovery_state.json",
    "lifecycle_quality_score": INTELLIGENCE_DIR / "lifecycle_quality_score.json",
    "trend_thesis_intelligence": INTELLIGENCE_DIR / "trend_thesis_intelligence.json",
    "portfolio_breakthrough_routing": INTELLIGENCE_DIR / "portfolio_breakthrough_routing.json",
}

@dataclass
class UISourceStatus:
    name: str
    path: str
    exists: bool
    readable: bool
    status: str
    summary: Dict[str, Any]


def _read_json(path: Path) -> tuple[bool, Dict[str, Any]]:
    if not path.exists():
        return False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return True, data if isinstance(data, dict) else {"value": data}
    except Exception as exc:  # defensive: UI shell must not crash runtime
        return False, {"error": str(exc)}


def _summarize(data: Dict[str, Any]) -> Dict[str, Any]:
    keys = list(data.keys())[:12]
    return {
        "keys": keys,
        "status": data.get("status") or data.get("state") or data.get("runtime_status") or "unknown",
        "terminal_state": data.get("terminal_state"),
        "version": data.get("version"),
    }


def build_master_control_ui_shell() -> Dict[str, Any]:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    sources: List[UISourceStatus] = []
    for name, path in STATE_FILES.items():
        readable, data = _read_json(path)
        exists = path.exists()
        status = "ready" if exists and readable else ("missing" if not exists else "unreadable")
        sources.append(UISourceStatus(name, str(path), exists, readable, status, _summarize(data)))
    payload = {
        "version": "v16.46",
        "layer": "master_control_ui_shell",
        "mode": "read_only",
        "mutation_allowed": False,
        "protected_runtime_spine": "preserved",
        "sources": [asdict(s) for s in sources],
        "ready": all(s.status in {"ready", "missing"} for s in sources),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

if __name__ == "__main__":
    print(json.dumps(build_master_control_ui_shell(), indent=2))
