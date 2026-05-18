from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_live_probe"
MANIFEST_PATH = RUNTIME_DIR / "last_single_head_probe_manifest.json"


def main() -> int:
    if not MANIFEST_PATH.exists():
        print("[S36-VERIFY][FAILED] No last_single_head_probe_manifest.json found.")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    qpath = manifest.get("last_probe_quarantine_path")
    if not qpath:
        print("[S36-VERIFY][FAILED] Manifest missing quarantine path.")
        return 1

    quarantine_path = Path(qpath)
    if not quarantine_path.exists():
        print(f"[S36-VERIFY][FAILED] Quarantine record not found: {quarantine_path}")
        return 1

    record = json.loads(quarantine_path.read_text(encoding="utf-8"))
    failures = []

    required_false = [
        "body_read",
        "browser_execution",
        "runtime_truth_mutation",
        "autonomous_execution",
    ]
    for key in required_false:
        if record.get(key) is not False:
            failures.append(f"{key} must be false")

    if record.get("probe_type") != "HEAD_METADATA_ONLY":
        failures.append("probe_type must be HEAD_METADATA_ONLY")
    if record.get("manual_promotion_required") is not True:
        failures.append("manual_promotion_required must be true")
    if record.get("quarantined") is not True:
        failures.append("quarantined must be true")
    if not isinstance(record.get("metadata"), dict):
        failures.append("metadata must exist")
    else:
        if "headers" not in record["metadata"]:
            failures.append("metadata.headers must exist")
        if "status" not in record["metadata"]:
            failures.append("metadata.status must exist")

    if failures:
        print("[S36-VERIFY][FAILED]")
        for item in failures:
            print(f" - {item}")
        return 1

    print("[S36-VERIFY] PASS")
    print(json.dumps({
        "quarantine_path": str(quarantine_path),
        "status": record.get("metadata", {}).get("status"),
        "content_type": record.get("metadata", {}).get("content_type"),
        "body_read": record.get("body_read"),
        "manual_promotion_required": record.get("manual_promotion_required"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
