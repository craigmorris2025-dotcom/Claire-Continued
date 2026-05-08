#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def audit(root: Path) -> Dict[str, object]:
    tests = root / "tests"
    active_placeholder_tests: List[str] = []
    underscored_placeholder_tests: List[str] = []

    for path in tests.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        has_placeholder = "NotImplementedError" in text and "Import target class" in text
        if not has_placeholder:
            continue

        rel = str(path.relative_to(root))
        if path.name.startswith("_"):
            underscored_placeholder_tests.append(rel)
        else:
            active_placeholder_tests.append(rel)

    baseline = root / "tests" / "regression" / "test_baseline_runner.py"
    baseline_guarded = None
    if baseline.exists():
        text = baseline.read_text(encoding="utf-8", errors="ignore")
        baseline_guarded = any(
            marker in text
            for marker in [
                "CLAIRE_ALLOW_BASELINE_FAILURES",
                "known_placeholder",
                "baseline_runner_guard",
                "expected_failures",
            ]
        )

    status = "pass" if not active_placeholder_tests and baseline_guarded is not False else "needs_attention"

    return {
        "record_type": "pytest_consistency_audit",
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "active_placeholder_tests": active_placeholder_tests,
        "underscored_placeholder_tests": underscored_placeholder_tests,
        "baseline_runner_exists": baseline.exists(),
        "baseline_runner_guarded": baseline_guarded,
        "rule": "Generic placeholder stage tests must not remain active in full pytest. Bind them or underscore-disable them.",
        "recommended_commands": [
            "pytest tests/consistency -v",
            "pytest tests/operational_proof -v",
            "pytest tests/consistency tests/operational_proof -v",
            "pytest",
        ],
    }


def main() -> int:
    root = Path.cwd()
    report = audit(root)
    out = root / "data" / "testing" / "consistency_audits" / (
        "pytest_consistency_audit_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"
Report written: {out}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
