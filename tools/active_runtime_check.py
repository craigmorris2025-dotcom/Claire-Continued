#!/usr/bin/env python3
"""
Active Runtime Check

Checks the minimum import path needed for Claire to launch.
This does not start the server.
"""

from __future__ import annotations

import importlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

IMPORTS = [
    "claire.app",
    "claire.api.routes_pipeline",
    "claire.orchestrator.pipeline_v4",
    "claire.technology.technology_intelligence",
]


def main() -> int:
    results = []
    for module in IMPORTS:
        try:
            importlib.import_module(module)
            results.append({"module": module, "status": "success"})
        except Exception as exc:
            results.append({"module": module, "status": "failed", "error": repr(exc)})

    failed = [r for r in results if r["status"] != "success"]

    payload = {
        "check": "active_runtime_check",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "failed",
        "failed_count": len(failed),
        "imports": results,
    }

    out_dir = ROOT / ".claire_install" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"active_runtime_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nReport written: {out_path}")
    return 0 if payload["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
