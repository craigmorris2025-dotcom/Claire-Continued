from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/enterprise/runtime_health_recovery_diagnostics.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


HEALTH_DIAGNOSTICS_PATH = Path("data/enterprise/runtime_health_recovery_diagnostics.json")

RUNTIME_FILES = [
    "data/runtime/master_control_state.json",
    "data/runtime/runtime_state.json",
    "data/runtime/unified_runtime_dashboard.json",
    "data/runtime/runtime_control_center.json",
    "data/runtime/runtime_intelligence.json",
    "data/runtime/runtime_recovery_state.json",
]

INTELLIGENCE_FILES = [
    "data/intelligence/lifecycle_quality_score.json",
    "data/intelligence/trend_thesis_intelligence.json",
    "data/intelligence/portfolio_breakthrough_routing.json",
]


def _inspect_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"path": path, "exists": False, "readable": False}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {
            "path": path,
            "exists": True,
            "readable": True,
            "top_level_type": type(data).__name__,
        }
    except Exception as exc:
        return {
            "path": path,
            "exists": True,
            "readable": False,
            "error": str(exc),
        }


def build_runtime_health_recovery_diagnostics() -> Dict[str, Any]:
    runtime = [_inspect_json(path) for path in RUNTIME_FILES]
    intelligence = [_inspect_json(path) for path in INTELLIGENCE_FILES]

    all_checks = runtime + intelligence
    readable = len([c for c in all_checks if c.get("readable") is True])
    missing = len([c for c in all_checks if c.get("exists") is False])

    report = {
        "version": "16.77",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "healthy_or_partial" if readable else "blocked",
        "readable_count": readable,
        "missing_count": missing,
        "checked_count": len(all_checks),
        "runtime_files": runtime,
        "intelligence_files": intelligence,
        "recovery_notes": [
            "Missing files may be acceptable if the runtime has not generated them yet.",
            "Unreadable files should be treated as recovery or corruption risks.",
            "This diagnostic does not mutate runtime state.",
        ],
    }

    HEALTH_DIAGNOSTICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_DIAGNOSTICS_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
""")

print("v16.77 runtime health + recovery diagnostics installed.")
