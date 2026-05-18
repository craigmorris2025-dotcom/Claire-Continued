#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

RUNTIME_FILES = [
    "runtime_state.json",
    "unified_runtime_dashboard.json",
    "runtime_control_center.json",
    "runtime_intelligence.json",
    "runtime_recovery_state.json",
    "route_activity_monitor.json",
    "install_governance_dashboard.json",
]

INTELLIGENCE_FILES = [
    "lifecycle_quality_score.json",
    "trend_thesis_intelligence.json",
    "portfolio_breakthrough_routing.json",
]


def load(path: Path):
    if not path.exists():
        return {
            "status": "missing",
            "path": str(path),
        }

    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {
            "status": "error",
            "path": str(path),
            "error": repr(exc),
        }


def main() -> int:
    runtime_dir = ROOT / "data" / "runtime"
    intelligence_dir = ROOT / "data" / "intelligence"

    runtime = {
        name: load(runtime_dir / name)
        for name in RUNTIME_FILES
    }

    intelligence = {
        name: load(intelligence_dir / name)
        for name in INTELLIGENCE_FILES
    }

    payload = {
        "layer": "master_control_state",
        "version": "v16.45",
        "created_at": datetime.now().isoformat(),
        "runtime": runtime,
        "intelligence": intelligence,
        "status": "available",
        "recommendations": [
            "continue protecting runtime spine",
            "keep install governance mandatory",
            "connect intelligence outputs to lifecycle runtime gradually",
            "avoid direct uncontrolled feature expansion",
            "preserve portfolio-first routing policy",
        ],
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "master_control_state.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "layer": payload["layer"],
        "status": payload["status"],
        "runtime_sections": list(runtime.keys()),
        "intelligence_sections": list(intelligence.keys()),
    }, indent=2))

    print("Master control state written:", out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
