from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_system_inventory"

NEED_REPORT = RUNTIME_DIR / "s37_web_need_classifier.json"
QUEUE_REPORT = RUNTIME_DIR / "s37_governed_research_queue.json"
QUEUE_QUARANTINE = QUARANTINE_DIR / "s37_governed_research_queue_quarantine.json"


SOURCE_POLICY = {
    "official_python_docs": {
        "allowed_domains": ["docs.python.org"],
        "requires_official_source": True,
    },
    "official_fastapi_docs": {
        "allowed_domains": ["fastapi.tiangolo.com"],
        "requires_official_source": True,
    },
    "official_target_or_provider_policy": {
        "allowed_domains": [],
        "requires_official_source": True,
        "operator_must_select_target": True,
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_queue(needs: list[dict]) -> list[dict]:
    queue = []
    for index, need in enumerate(needs, start=1):
        if need.get("web_research_allowed") is not True:
            continue

        source_type = need.get("allowed_source_type", "unclassified")
        policy = SOURCE_POLICY.get(source_type, {
            "allowed_domains": [],
            "requires_official_source": True,
            "operator_review_required": True,
        })

        queue.append({
            "queue_id": f"S37-WEB-NEED-{index:03d}",
            "classification": need.get("classification"),
            "topic": need.get("topic"),
            "reason": need.get("reason"),
            "allowed_source_type": source_type,
            "allowed_domains": policy.get("allowed_domains", []),
            "requires_official_source": policy.get("requires_official_source", True),
            "operator_must_select_target": policy.get("operator_must_select_target", False),
            "web_search_executed": False,
            "automatic_action_allowed": False,
            "runtime_truth_mutation_allowed": False,
            "manual_promotion_required": True,
            "quarantine_required": True,
            "status": "queued_for_manual_governed_research",
        })
    return queue


def main() -> int:
    if not NEED_REPORT.exists():
        print("[S37-RESEARCH-QUEUE][BLOCKED] Need classifier report missing. Run tools/s37_web_need_classifier.py first.")
        return 1

    need_report = json.loads(NEED_REPORT.read_text(encoding="utf-8"))
    queue = _build_queue(need_report.get("needs", []))

    report = {
        "version": "v19.89.8-S37R5-R8-research-queue-source-policy",
        "generated_at": _utc_now(),
        "source_need_report": str(NEED_REPORT),
        "live_web_execution": False,
        "web_search_executed": False,
        "automatic_updates_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "queue_count": len(queue),
        "source_policy": SOURCE_POLICY,
        "queue": queue,
    }

    QUEUE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    QUEUE_QUARANTINE.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("[S37-RESEARCH-QUEUE] PASS")
    print(json.dumps({
        "queue_count": len(queue),
        "web_search_executed": False,
        "manual_promotion_required": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
