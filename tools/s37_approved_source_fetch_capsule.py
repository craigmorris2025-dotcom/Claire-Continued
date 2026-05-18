from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_web_evidence"

APPROVALS_REPORT = RUNTIME_DIR / "s37_manual_research_approvals.json"
QUEUE_REPORT = RUNTIME_DIR / "s37_governed_research_queue.json"
FETCH_PLAN = RUNTIME_DIR / "s37_approved_source_fetch_plan.json"
FETCH_PLAN_QUARANTINE = QUARANTINE_DIR / "s37_approved_source_fetch_plan_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _domain_allowed(url: str, allowed_domains: list[str]) -> bool:
    if not allowed_domains:
        return False
    host = urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in allowed_domains)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a governed fetch plan. Does not execute web fetch.")
    parser.add_argument("--approval-id", required=True)
    parser.add_argument("--operator-ack", required=True, choices=["YES"])
    args = parser.parse_args()

    if not APPROVALS_REPORT.exists():
        print("[S37-FETCH-CAPSULE][BLOCKED] Manual approval report missing.")
        return 1

    approvals = json.loads(APPROVALS_REPORT.read_text(encoding="utf-8")).get("approvals", [])
    approval = next((item for item in approvals if item.get("approval_id") == args.approval_id), None)
    if not approval:
        print("[S37-FETCH-CAPSULE][FAILED] Approval id not found.")
        return 1

    entry = approval.get("source_queue_entry", {})
    allowed_domains = entry.get("allowed_domains", [])
    candidate_url = approval.get("candidate_url")
    domain_allowed = _domain_allowed(candidate_url, allowed_domains)

    plan = {
        "version": "v19.89.8-S37R9-R16-review-export-fetch-capsule",
        "generated_at": _utc_now(),
        "approval_id": args.approval_id,
        "queue_id": approval.get("queue_id"),
        "candidate_url": candidate_url,
        "domain_allowed": domain_allowed,
        "allowed_domains": allowed_domains,
        "ready_for_s38_single_fetch": domain_allowed,
        "web_fetch_executed": False,
        "response_body_read": False,
        "browser_execution": False,
        "javascript_execution": False,
        "automatic_action_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "status": "ready_for_s38_single_fetch" if domain_allowed else "blocked_by_source_policy",
    }

    FETCH_PLAN.parent.mkdir(parents=True, exist_ok=True)
    FETCH_PLAN_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    FETCH_PLAN.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    FETCH_PLAN_QUARANTINE.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    if not domain_allowed:
        print("[S37-FETCH-CAPSULE][BLOCKED] Candidate URL is not allowed by source policy.")
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 1

    print("[S37-FETCH-CAPSULE] PASS")
    print(json.dumps({"ready_for_s38_single_fetch": True, "web_fetch_executed": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
