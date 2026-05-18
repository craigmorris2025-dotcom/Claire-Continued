from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUEUE_REPORT = RUNTIME_DIR / "s37_governed_research_queue.json"
EXPORT_JSON = RUNTIME_DIR / "s37_research_queue_operator_review.json"
EXPORT_MD = RUNTIME_DIR / "S37_RESEARCH_QUEUE_OPERATOR_REVIEW.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    if not QUEUE_REPORT.exists():
        print("[S37-REVIEW-EXPORT][BLOCKED] Research queue missing. Run tools/s37_build_governed_research_queue.py first.")
        return 1

    queue_report = json.loads(QUEUE_REPORT.read_text(encoding="utf-8"))
    queue = queue_report.get("queue", [])

    review = {
        "version": "v19.89.8-S37R9-R16-review-export-fetch-capsule",
        "generated_at": _utc_now(),
        "source_queue": str(QUEUE_REPORT),
        "review_required": True,
        "manual_promotion_required": True,
        "web_search_executed": False,
        "automatic_action_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "items": queue,
    }

    lines = [
        "# S37 Governed Research Queue Operator Review",
        "",
        "No web search has been executed by this export.",
        "No automatic update is allowed.",
        "Manual approval is required before any fetch capsule may run.",
        "",
    ]
    for item in queue:
        lines.extend([
            f"## {item.get('queue_id')}",
            f"- Classification: {item.get('classification')}",
            f"- Topic: {item.get('topic')}",
            f"- Allowed source type: {item.get('allowed_source_type')}",
            f"- Allowed domains: {', '.join(item.get('allowed_domains', [])) or 'operator target required'}",
            f"- Manual promotion required: {item.get('manual_promotion_required')}",
            "",
        ])

    EXPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_JSON.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")
    EXPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("[S37-REVIEW-EXPORT] PASS")
    print(json.dumps({"items": len(queue), "web_search_executed": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
