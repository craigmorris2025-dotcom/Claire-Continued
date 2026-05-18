from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_live_probe"
MANIFEST_PATH = RUNTIME_DIR / "last_single_head_probe_manifest.json"
OUTPUT_REPORT = RUNTIME_DIR / "s36_first_probe_operator_report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    if not MANIFEST_PATH.exists():
        print("[S36-FIRST-PROBE-REPORT][BLOCKED] No probe manifest found. Run one operator-triggered probe first.")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    qpath = manifest.get("last_probe_quarantine_path")
    if not qpath:
        print("[S36-FIRST-PROBE-REPORT][FAILED] Manifest missing quarantine path.")
        return 1

    quarantine_path = Path(qpath)
    if not quarantine_path.exists():
        print(f"[S36-FIRST-PROBE-REPORT][FAILED] Quarantine record missing: {quarantine_path}")
        return 1

    record = json.loads(quarantine_path.read_text(encoding="utf-8"))
    metadata = record.get("metadata", {})

    failures = []
    for key in ["body_read", "browser_execution", "runtime_truth_mutation", "autonomous_execution"]:
        if record.get(key) is not False:
            failures.append(f"{key} must be false")
    if record.get("probe_type") != "HEAD_METADATA_ONLY":
        failures.append("probe_type must be HEAD_METADATA_ONLY")
    if record.get("manual_promotion_required") is not True:
        failures.append("manual_promotion_required must be true")
    if record.get("quarantined") is not True:
        failures.append("quarantined must be true")
    if not isinstance(metadata, dict):
        failures.append("metadata object missing")
    else:
        if "status" not in metadata:
            failures.append("metadata.status missing")
        if "headers" not in metadata:
            failures.append("metadata.headers missing")

    report = {
        "version": "v19.89.8-S36R12-R14-probe-guard-quarantine-report",
        "compiled_at": _utc_now(),
        "passed": not failures,
        "failures": failures,
        "quarantine_path": str(quarantine_path),
        "url": record.get("url"),
        "status": metadata.get("status") if isinstance(metadata, dict) else None,
        "content_type": metadata.get("content_type") if isinstance(metadata, dict) else None,
        "latency_ms": metadata.get("latency_ms") if isinstance(metadata, dict) else None,
        "metadata_only": True,
        "body_read": record.get("body_read"),
        "browser_execution": record.get("browser_execution"),
        "runtime_truth_mutation": record.get("runtime_truth_mutation"),
        "autonomous_execution": record.get("autonomous_execution"),
        "manual_promotion_required": record.get("manual_promotion_required"),
        "quarantined": record.get("quarantined"),
        "runtime_truth_mutated": False,
        "automatic_update_applied": False,
        "continuous_crawl_started": False,
    }

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        print("[S36-FIRST-PROBE-REPORT][FAILED]")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print("[S36-FIRST-PROBE-REPORT] PASS")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
