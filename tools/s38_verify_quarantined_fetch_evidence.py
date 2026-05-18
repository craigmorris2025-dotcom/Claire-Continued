from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "runtime" / "governed_web_fetch" / "s38_last_single_fetch_manifest.json"
REPORT = ROOT / "runtime" / "governed_web_fetch" / "s38_fetch_evidence_verification.json"


def main() -> int:
    if not MANIFEST.exists():
        print("[S38-VERIFY][BLOCKED] Fetch manifest missing.")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    qpath = Path(manifest.get("quarantine_path", ""))
    if not qpath.exists():
        print("[S38-VERIFY][FAILED] Quarantine evidence file missing.")
        return 1

    record = json.loads(qpath.read_text(encoding="utf-8"))
    evidence = record.get("evidence", {})
    failures = []

    required_false = [
        "browser_execution",
        "javascript_execution",
        "autonomous_execution",
        "runtime_truth_mutation",
        "automatic_update_applied",
    ]
    for key in required_false:
        if record.get(key) is not False:
            failures.append(key + " must be false")

    if record.get("manual_promotion_required") is not True:
        failures.append("manual_promotion_required must be true")
    if record.get("quarantined") is not True:
        failures.append("quarantined must be true")
    if record.get("single_fetch_only") is not True:
        failures.append("single_fetch_only must be true")
    if not evidence.get("body_sha256"):
        failures.append("body_sha256 missing")
    if evidence.get("body_bytes_captured", 0) > record.get("max_bytes", 0):
        failures.append("captured bytes exceed max_bytes")

    report = {
        "passed": not failures,
        "failures": failures,
        "manifest": manifest,
        "quarantine_path": str(qpath),
        "manual_promotion_required": record.get("manual_promotion_required"),
        "runtime_truth_mutation": record.get("runtime_truth_mutation"),
        "automatic_update_applied": record.get("automatic_update_applied"),
        "status": evidence.get("status"),
        "content_type": evidence.get("content_type"),
        "body_bytes_captured": evidence.get("body_bytes_captured"),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        print("[S38-VERIFY][FAILED]")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print("[S38-VERIFY] PASS")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
