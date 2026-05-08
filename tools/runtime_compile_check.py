#!/usr/bin/env python3
"""
Runtime Compile Check

Fast syntax check for active runtime source.
"""

from __future__ import annotations

import ast
import json
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
SRC = ROOT / "src"


def main() -> int:
    failures = []

    for path in SRC.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8-sig", errors="strict")
            ast.parse(text, filename=str(path))
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
                "error": repr(exc),
            })

    payload = {
        "check": "runtime_compile_check",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failures else "failed",
        "failure_count": len(failures),
        "failures": failures[:100],
    }

    out_dir = ROOT / ".claire_install" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"runtime_compile_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nReport written: {out_path}")
    return 0 if payload["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
