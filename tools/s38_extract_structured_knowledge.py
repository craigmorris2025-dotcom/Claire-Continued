from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_web_fetch"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_web_evidence"

BASKET_REPORT = RUNTIME_DIR / "s38_quarantined_evidence_basket.json"
STRUCTURED_REPORT = RUNTIME_DIR / "s38_structured_knowledge_extraction.json"
STRUCTURED_QUARANTINE = QUARANTINE_DIR / "s38_structured_knowledge_extraction_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_title(text: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:300]


def _extract_headings(text: str) -> list[str]:
    headings = []
    for match in re.finditer(r"<h[1-3][^>]*>(.*?)</h[1-3]>", text, flags=re.IGNORECASE | re.DOTALL):
        clean = re.sub(r"<[^>]+>", " ", match.group(1))
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean:
            headings.append(clean[:300])
        if len(headings) >= 20:
            break
    return headings


def main() -> int:
    if not BASKET_REPORT.exists():
        print("[S38-KNOWLEDGE-EXTRACT][BLOCKED] Evidence basket missing.")
        return 1

    basket = json.loads(BASKET_REPORT.read_text(encoding="utf-8"))
    items = basket.get("evidence_items", [])

    extractions = []
    for item in items:
        text = item.get("text_preview", "")
        extractions.append({
            "item_id": item.get("item_id"),
            "url": item.get("url"),
            "title": _extract_title(text),
            "headings": _extract_headings(text),
            "body_sha256": item.get("body_sha256"),
            "content_type": item.get("content_type"),
            "extraction_scope": "bounded_preview_only",
            "manual_promotion_required": True,
            "quarantined": True,
        })

    report = {
        "version": "v19.89.8-S38R5-R8-evidence-basket-extraction",
        "generated_at": _utc_now(),
        "source_basket": str(BASKET_REPORT),
        "extraction_count": len(extractions),
        "web_fetch_executed": False,
        "runtime_truth_mutation": False,
        "automatic_update_applied": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "extractions": extractions,
    }

    STRUCTURED_REPORT.parent.mkdir(parents=True, exist_ok=True)
    STRUCTURED_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    STRUCTURED_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    STRUCTURED_QUARANTINE.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("[S38-KNOWLEDGE-EXTRACT] PASS")
    print(json.dumps({
        "extraction_count": len(extractions),
        "web_fetch_executed": False,
        "manual_promotion_required": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
