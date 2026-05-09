#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if SRC.exists() and str(SRC) not in sys.path:
    sys.path.append(str(SRC))

PROTECTED_CONTRACTS = [
    {"path": "main.py", "type": "launch_entrypoint"},
    {"path": "claire/app.py", "type": "app_factory"},
    {"path": "claire/api/routes_pipeline.py", "type": "api_route"},
    {"path": "claire/orchestrator/pipeline_v4.py", "type": "runtime_orchestrator"},
    {
        "path": "claire/technology/technology_intelligence.py",
        "type": "runtime_dependency",
    },
]

REQUIRED_IMPORTS = [
    "claire.app",
    "claire.api.routes_pipeline",
    "claire.orchestrator.pipeline_v4",
    "claire.technology.technology_intelligence",
]


def main() -> int:
    path_results = []

    for item in PROTECTED_CONTRACTS:
        p = ROOT / item["path"]

        path_results.append(
            {
                **item,
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
            }
        )

    import_results = []

    for module in REQUIRED_IMPORTS:
        try:
            imported = importlib.import_module(module)

            import_results.append(
                {
                    "module": module,
                    "status": "success",
                    "origin": getattr(imported, "__file__", None),
                }
            )

        except Exception as exc:
            import_results.append(
                {
                    "module": module,
                    "status": "failed",
                    "error": repr(exc),
                }
            )

    payload = {
        "lock": "core_runtime_lock",
        "version": "v16.29-phase4d",
        "created_at": datetime.now().isoformat(),
        "status": (
            "locked"
            if all(p["exists"] for p in path_results)
            and all(i["status"] == "success" for i in import_results)
            else "failed"
        ),
        "protected_contracts": path_results,
        "required_imports": import_results,
        "canonical_runtime_root": "claire",
        "legacy_src_compatibility": SRC.exists(),
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "core_runtime_lock.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nRuntime lock written: {out_path}")

    return 0 if payload["status"] == "locked" else 1


if __name__ == "__main__":
    raise SystemExit(main())