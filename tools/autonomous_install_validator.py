#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

PROTECTED = [
    "main.py",
    "claire/app.py",
    "claire/api/routes_pipeline.py",
    "claire/orchestrator/pipeline_v4.py",
    "claire/technology/technology_intelligence.py",
]


def validate_installer(path: Path):
    issues = []

    if not path.exists():
        return {
            "path": str(path),
            "status": "failed",
            "issues": ["installer_missing"],
        }

    text = path.read_text(encoding="utf-8", errors="ignore")

    try:
        ast.parse(text)
    except SyntaxError as exc:
        issues.append(f"syntax_error:{exc.lineno}:{exc.msg}")

    if ".claire_install" not in text:
        issues.append("missing_install_report_pattern")

    if "backup" not in text.lower():
        issues.append("missing_backup_pattern")

    touched_protected = [p for p in PROTECTED if p in text]

    return {
        "path": str(path),
        "status": "approved" if not issues else "blocked",
        "issues": issues,
        "mentions_protected_paths": touched_protected,
        "risk": "elevated" if touched_protected else "normal",
    }


def main() -> int:
    targets = [Path(arg) for arg in sys.argv[1:]]

    if not targets:
        targets = sorted(ROOT.glob("*installer*.py"))[-10:]

    results = [
        validate_installer(t if t.is_absolute() else ROOT / t)
        for t in targets
    ]

    payload = {
        "validator": "autonomous_install_validator",
        "version": "v16.33",
        "created_at": datetime.now().isoformat(),
        "status": "approved"
        if all(r["status"] == "approved" for r in results)
        else "blocked",
        "validated_count": len(results),
        "results": results,
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "autonomous_install_validation.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nInstall validation written: {out}")

    return 0 if payload["status"] == "approved" else 1


if __name__ == "__main__":
    raise SystemExit(main())