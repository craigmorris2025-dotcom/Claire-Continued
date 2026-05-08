#!/usr/bin/env python3
from __future__ import annotations
import importlib, json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
MODULES = [
    "claire.lifecycle.lifecycle_runner",
    "claire.lifecycle.stage_registry",
    "claire.lifecycle.stage_contracts",
    "claire.lifecycle.stage_status",
]

def main() -> int:
    results = []
    for module in MODULES:
        try:
            importlib.import_module(module)
            results.append({"module": module, "status": "success"})
        except Exception as exc:
            results.append({"module": module, "status": "failed", "error": repr(exc)})
    payload = {
        "check": "lifecycle_enforcement_check",
        "version": "v16.29",
        "created_at": datetime.now().isoformat(),
        "status": "success" if all(r["status"] == "success" for r in results) else "failed",
        "modules": results,
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lifecycle_enforcement_check.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nLifecycle enforcement check written: {out_path}")
    return 0 if payload["status"] == "success" else 1

if __name__ == "__main__":
    raise SystemExit(main())
