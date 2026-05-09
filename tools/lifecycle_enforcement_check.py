#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
            imported = importlib.import_module(module)
            results.append(
                {
                    "module": module,
                    "status": "success",
                    "origin": getattr(imported, "__file__", None),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "module": module,
                    "status": "failed",
                    "error": repr(exc),
                }
            )

    payload = {
        "check": "lifecycle_enforcement_check",
        "version": "v16.29-phase4e",
        "created_at": datetime.now().isoformat(),
        "status": (
            "success"
            if all(r["status"] == "success" for r in results)
            else "failed"
        ),
        "modules": results,
        "canonical_runtime_root": "claire",
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