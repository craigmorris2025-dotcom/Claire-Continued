from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_system_inventory"

QUEUE_REPORT = RUNTIME_DIR / "s37_governed_research_queue.json"
POLICY_REPORT = RUNTIME_DIR / "s37_source_policy_gate.json"
POLICY_QUARANTINE = QUARANTINE_DIR / "s37_source_policy_gate_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _domain_allowed(url: str, allowed_domains: list[str]) -> bool:
    if not allowed_domains:
        return False
    host = urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in allowed_domains)


def evaluate_candidate(queue_id: str, candidate_url: str) -> dict:
    if not QUEUE_REPORT.exists():
        return {
            "allowed": False,
            "reason": "Research queue missing.",
            "web_search_executed": False,
        }

    queue_report = json.loads(QUEUE_REPORT.read_text(encoding="utf-8"))
    entries = {item.get("queue_id"): item for item in queue_report.get("queue", [])}
    entry = entries.get(queue_id)
    if not entry:
        return {
            "allowed": False,
            "reason": "Queue id not found.",
            "web_search_executed": False,
        }

    allowed_domains = entry.get("allowed_domains", [])
    allowed = _domain_allowed(candidate_url, allowed_domains)
    return {
        "allowed": allowed,
        "queue_id": queue_id,
        "candidate_url": candidate_url,
        "allowed_domains": allowed_domains,
        "reason": "Candidate source is within allowed official domains." if allowed else "Candidate source is not within allowed official domains or requires operator target selection.",
        "web_search_executed": False,
        "automatic_action_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def main() -> int:
    if not QUEUE_REPORT.exists():
        print("[S37-SOURCE-POLICY][BLOCKED] Research queue missing. Run tools/s37_build_governed_research_queue.py first.")
        return 1

    queue_report = json.loads(QUEUE_REPORT.read_text(encoding="utf-8"))
    evaluations = []
    for item in queue_report.get("queue", []):
        domains = item.get("allowed_domains", [])
        candidate = "https://" + domains[0] if domains else "operator_target_required"
        evaluations.append(evaluate_candidate(item.get("queue_id"), candidate))

    report = {
        "version": "v19.89.8-S37R5-R8-research-queue-source-policy",
        "generated_at": _utc_now(),
        "source_queue": str(QUEUE_REPORT),
        "live_web_execution": False,
        "web_search_executed": False,
        "automatic_updates_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "evaluations": evaluations,
    }

    POLICY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    POLICY_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    POLICY_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    POLICY_QUARANTINE.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("[S37-SOURCE-POLICY] PASS")
    print(json.dumps({
        "evaluations": len(evaluations),
        "web_search_executed": False,
        "manual_promotion_required": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
