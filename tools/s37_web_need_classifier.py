from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_system_inventory"

INVENTORY_REPORT = RUNTIME_DIR / "s37_system_self_inventory.json"
NEED_REPORT = RUNTIME_DIR / "s37_web_need_classifier.json"
NEED_QUARANTINE = QUARANTINE_DIR / "s37_web_need_classifier_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _infer_web_needs(inventory: dict) -> list[dict]:
    needs = []
    for gap in inventory.get("local_gaps", []):
        needs.append({
            "source_gap": gap,
            "classification": "local_repair_first",
            "web_research_allowed": False,
            "automatic_action_allowed": False,
            "manual_promotion_required": True,
            "reason": gap.get("reason", "Local issue should be resolved locally before web research."),
        })

    surfaces = inventory.get("expected_surfaces", {})
    routes = inventory.get("routes", [])

    if surfaces.get("governed_live_probe_router", {}).get("exists"):
        needs.append({
            "classification": "official_docs_needed",
            "topic": "Python stdlib http.client HEAD request behavior and header-only metadata handling",
            "web_research_allowed": True,
            "allowed_source_type": "official_python_docs",
            "automatic_action_allowed": False,
            "manual_promotion_required": True,
            "reason": "Validate HEAD-only metadata behavior against official docs before expanding providers.",
        })

    if any(r.get("path") == "/api/governed/live-probe/head" for r in routes):
        needs.append({
            "classification": "framework_behavior_uncertain",
            "topic": "FastAPI APIRouter nested include_router behavior and OpenAPI visibility",
            "web_research_allowed": True,
            "allowed_source_type": "official_fastapi_docs",
            "automatic_action_allowed": False,
            "manual_promotion_required": True,
            "reason": "Validate route mounting behavior from official docs only.",
        })

    needs.append({
        "classification": "provider_policy_check",
        "topic": "Target site robots and provider policy checks before broader metadata probing",
        "web_research_allowed": True,
        "allowed_source_type": "official_target_or_provider_policy",
        "automatic_action_allowed": False,
        "manual_promotion_required": True,
        "reason": "Before expanding beyond one-shot probes, policy evidence should be quarantined.",
    })
    return needs


def main() -> int:
    if not INVENTORY_REPORT.exists():
        print("[S37-NEED-CLASSIFIER][BLOCKED] Inventory missing. Run tools/s37_system_self_inventory.py first.")
        return 1

    inventory = json.loads(INVENTORY_REPORT.read_text(encoding="utf-8"))
    needs = _infer_web_needs(inventory)

    report = {
        "version": "v19.89.8-S37R1-R4-self-inventory-need-classifier",
        "generated_at": _utc_now(),
        "source_inventory": str(INVENTORY_REPORT),
        "live_web_execution": False,
        "web_search_executed": False,
        "automatic_updates_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "web_need_count": len(needs),
        "web_allowed_count": len([n for n in needs if n.get("web_research_allowed") is True]),
        "needs": needs,
    }

    NEED_REPORT.parent.mkdir(parents=True, exist_ok=True)
    NEED_QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    NEED_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    NEED_QUARANTINE.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("[S37-NEED-CLASSIFIER] PASS")
    print(json.dumps({
        "web_need_count": report["web_need_count"],
        "web_allowed_count": report["web_allowed_count"],
        "web_search_executed": False,
        "manual_promotion_required": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
