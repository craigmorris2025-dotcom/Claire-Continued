#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import importlib, json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
MODULES = [
    "claire.app",
    "claire.api.routes_pipeline",
    "claire.orchestrator.pipeline_v4",
    "claire.lifecycle.lifecycle_runner",
    "claire.lifecycle.stage_registry",
    "claire.output.core_output_builder",
    "claire.dashboard.dashboard_state_builder",
    "claire.technology.technology_intelligence",
]

def main() -> int:
    records = []
    for module in MODULES:
        try:
            imported = importlib.import_module(module)
            records.append({"module": module, "status": "active", "file": getattr(imported, "__file__", None)})
        except Exception as exc:
            records.append({"module": module, "status": "failed", "error": repr(exc)})
    payload = {
        "registry": "active_module_registry",
        "version": "v16.28",
        "created_at": datetime.now().isoformat(),
        "module_count": len(records),
        "failed_count": len([r for r in records if r["status"] != "active"]),
        "modules": records,
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "active_module_registry.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nRegistry written: {out_path}")
    return 0 if payload["failed_count"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())

