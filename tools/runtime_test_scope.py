#!/usr/bin/env python3
"""
Runtime Test Scope

Lists tests considered active runtime tests versus quarantined placeholder tests.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
TESTS = ROOT / "tests"


def main() -> int:
    active = []
    quarantined = []

    if TESTS.exists():
        for path in TESTS.rglob("test_*.py"):
            rel = str(path.relative_to(ROOT))
            if "placeholder_disabled" in rel:
                quarantined.append(rel)
            else:
                active.append(rel)

    payload = {
        "tool": "runtime_test_scope",
        "created_at": datetime.now().isoformat(),
        "active_test_count": len(active),
        "quarantined_placeholder_test_count": len(quarantined),
        "active_tests": active,
        "quarantined_placeholder_tests": quarantined,
    }

    out_dir = ROOT / ".claire_install" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"runtime_test_scope_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nReport written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
