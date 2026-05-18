from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FETCH_MANIFEST = ROOT / "runtime" / "governed_web_fetch" / "s38_last_single_fetch_manifest.json"
RUNTIME_DIR = ROOT / "runtime" / "governed_web_fetch"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_web_evidence"
BASKET_REPORT = RUNTIME_DIR / "s38_quarantined_evidence_basket.json"
BASKET_QUARANTINE = QUARANTINE_DIR / "s38_quarantined_evidence_basket_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    if not FETCH_MANIFEST.exists():
        print("[S38-EVIDENCE-BASKET][BLOCKED] Fetch manifest missing. Run the approved-source fetch first.")
        return 1

    manifest = json.loads(FETCH_MANIFEST.read_text(encoding="utf-8"))
    qpath = Path(manifest.get("quarantine_path", ""))
    if not qpath.exists():
        print("[S38-EVIDENCE-BASKET][FAILED] Quarantined evidence file missing.")
        return 1

    record = json.loads(qpath.read_text(encoding="utf-8"))
    evidence = record.get("evidence", {})
    preview = evidence.get("text_preview", "")

    basket = {
        "version": "v19.89.8-S38R5-R8-evidence-basket-extraction",
        "generated_at": _utc_now(),
        "source_manifest": str(FETCH_MANIFEST),
        "source_quarantine_path": str(qpath),
        "url": record.get("url"),
        "approval_id": record.get("approval_id"),
        "queue_id": record.get("queue_id"),
        "source_policy_passed": record.get("source_policy_passed"),
        "status": evidence.get("status"),
        "content_type": evidence.get("content_type"),
        "latency_ms": evidence.get("latency_ms"),
        "body_sha256": evidence.get("body_sha256"),
        "body_bytes_captured": evidence.get("body_bytes_captured"),
        "body_truncated": evidence.get("body_truncated"),
        "preview_character_count": len(preview),
        "manual_promotion_required": True,
        "quarantined": True,
        "runtime_truth_mutation": False,
        "automatic_update_applied": False,
        "evidence_items": [
            {
                "item_id": "S38-EVIDENCE-001",
                "type": "approved_source_fetch_preview",
                "url": record.get("url"),
                "content_type": evidence.get("content_type"),
                "body_sha256": evidence.get("body_sha256"),
                "text_preview": preview,
                "quarantined": True,
                "manual_promotion_required": True,
            }
        ],
    }

    BASKET_REPORT.parent.mkdir(parents=True, exist_ok=True)
    BASKET_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    BASKET_REPORT.write_text(json.dumps(basket, indent=2, sort_keys=True), encoding="utf-8")
    BASKET_QUARANTINE.write_text(json.dumps(basket, indent=2, sort_keys=True), encoding="utf-8")

    print("[S38-EVIDENCE-BASKET] PASS")
    print(json.dumps({
        "evidence_items": len(basket["evidence_items"]),
        "manual_promotion_required": True,
        "runtime_truth_mutation": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
