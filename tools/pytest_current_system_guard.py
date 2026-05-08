#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def is_placeholder_stage_test(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "NotImplementedError" in text and "Import target class" in text


def find_active_placeholders(root: Path) -> List[Path]:
    found: List[Path] = []
    tests_root = root / "tests"
    if not tests_root.exists():
        return found

    for path in tests_root.rglob("test_*.py"):
        if "consistency" in path.parts:
            continue
        if is_placeholder_stage_test(path):
            found.append(path)

    return sorted(found)


def quarantine_name(path: Path) -> Path:
    if path.name.startswith("_"):
        return path
    candidate = path.with_name("_" + path.stem + "_placeholder" + path.suffix)
    if not candidate.exists():
        return candidate

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return path.with_name("_" + path.stem + "_placeholder_" + timestamp + path.suffix)


def audit(root: Path) -> Dict[str, object]:
    active = find_active_placeholders(root)
    underscored = []

    for path in (root / "tests").rglob("_test*.py"):
        if is_placeholder_stage_test(path):
            underscored.append(path)

    return {
        "record_type": "current_system_pytest_guard_audit",
        "status": "pass" if not active else "needs_quarantine",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "active_placeholder_tests": [str(p.relative_to(root)) for p in active],
        "quarantined_placeholder_tests": [str(p.relative_to(root)) for p in sorted(underscored)],
        "rule": "Old Import target class placeholders must be quarantined until bound to real current-system classes.",
    }


def write_report(root: Path, payload: Dict[str, object], prefix: str) -> Path:
    out = root / "data" / "testing" / "consistency_audits" / (
        prefix + "_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out


def quarantine(root: Path) -> Dict[str, object]:
    active = find_active_placeholders(root)
    moves = []

    for src in active:
        dest = quarantine_name(src)
        src.rename(dest)
        moves.append({
            "from": str(src.relative_to(root)),
            "to": str(dest.relative_to(root)),
            "reason": "active placeholder contained NotImplementedError('Import target class')",
        })

    payload = {
        "record_type": "current_system_placeholder_quarantine",
        "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "move_count": len(moves),
        "moves": moves,
        "rule": "Files were renamed, not deleted, so they can be rebound later.",
    }

    manifest = root / "data" / "testing" / "quarantined_placeholders" / (
        "quarantined_placeholders_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".json"
    )
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["manifest_path"] = str(manifest.relative_to(root))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Claire current-system pytest guard")
    parser.add_argument("--root", default=".", help="Claire project root")
    parser.add_argument("--audit", action="store_true", help="Audit active placeholder tests")
    parser.add_argument("--quarantine", action="store_true", help="Rename active placeholder tests so pytest ignores them")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if not (root / "tests").exists():
        print("[ERROR] Missing tests folder. Run from Claire project root.")
        return 2

    if args.quarantine:
        payload = quarantine(root)
        report = write_report(root, payload, "pytest_current_system_quarantine")
        print(json.dumps(payload, indent=2, sort_keys=True))
        print(f"Report written: {report}")
        return 0

    payload = audit(root)
    report = write_report(root, payload, "pytest_current_system_audit")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Report written: {report}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
