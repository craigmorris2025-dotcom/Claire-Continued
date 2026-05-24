#!/usr/bin/env python3
"""
Forward Install Guard

Checks that future Claire installers do not break the active runtime.
This tool is intentionally read-only.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


ROOT = Path.cwd()

PROTECTED_PATHS = [
    "main.py",
    "src/claire/app.py",
    "src/claire/api",
    "src/claire/orchestrator",
    "src/claire/lifecycle",
    "src/claire/engines",
    "src/claire/output",
    "src/claire/dashboard",
    "src/claire/technology/technology_intelligence.py",
]

PROTECTED_IMPORTS = [
    "runtime_core.app",
    "runtime_core.api.routes_pipeline",
    "claire.orchestrator.pipeline_v4",
    "claire.technology.technology_intelligence",
]


def _result(name: str, status: str, **extra):
    payload = {"name": name, "status": status}
    payload.update(extra)
    return payload


def check_protected_paths() -> Dict:
    missing = []
    for rel in PROTECTED_PATHS:
        if not (ROOT / rel).exists():
            missing.append(rel)
    return _result(
        "protected_paths",
        "success" if not missing else "failed",
        missing=missing,
        checked_count=len(PROTECTED_PATHS),
    )


def check_nested_repo_pollution() -> Dict:
    nested = []
    for path in [
        ROOT / "src" / "claire" / ".git",
        ROOT / "src" / "claire" / "Claire" / ".git",
        ROOT / "src" / "claire" / "Claire",
    ]:
        if path.exists():
            nested.append(str(path.relative_to(ROOT)))
    return _result(
        "nested_repo_pollution",
        "success" if not nested else "failed",
        nested=nested,
    )


def check_placeholder_tests() -> Dict:
    offenders = []
    tests_dir = ROOT / "tests"
    if tests_dir.exists():
        for path in tests_dir.rglob("test_*.py"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if 'raise NotImplementedError("Import target class")' in text or "raise NotImplementedError('Import target class')" in text:
                offenders.append(str(path.relative_to(ROOT)))

    return _result(
        "active_placeholder_tests",
        "success" if not offenders else "failed",
        offenders=offenders,
        offender_count=len(offenders),
    )


def check_syntax_fast() -> Dict:
    src = ROOT / "src"
    failures = []
    if src.exists():
        for path in src.rglob("*.py"):
            try:
                ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
            except SyntaxError as exc:
                failures.append({
                    "path": str(path.relative_to(ROOT)),
                    "line": exc.lineno,
                    "error": exc.msg,
                })
            except Exception as exc:
                failures.append({
                    "path": str(path.relative_to(ROOT)),
                    "line": None,
                    "error": f"read_or_parse_error: {exc}",
                })

    return _result(
        "syntax_fast",
        "success" if not failures else "failed",
        failure_count=len(failures),
        failures=failures[:50],
    )


def check_protected_imports() -> Dict:
    code = "\n".join([f"import {module}" for module in PROTECTED_IMPORTS])
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return _result(
        "protected_imports",
        "success" if completed.returncode == 0 else "failed",
        returncode=completed.returncode,
        stdout=completed.stdout[-2000:],
        stderr=completed.stderr[-4000:],
        imports=PROTECTED_IMPORTS,
    )


def run_guard() -> Dict:
    checks = [
        check_protected_paths(),
        check_nested_repo_pollution(),
        check_placeholder_tests(),
        check_syntax_fast(),
        check_protected_imports(),
    ]

    failed = [c for c in checks if c["status"] != "success"]

    return {
        "guard": "forward_install_guard",
        "version": "v16.26",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "failed",
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
    }


def main() -> int:
    payload = run_guard()
    out_dir = ROOT / ".claire_install" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"forward_install_guard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nReport written: {out_path}")
    return 0 if payload["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
