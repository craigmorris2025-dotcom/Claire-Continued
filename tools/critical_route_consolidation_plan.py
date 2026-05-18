#!/usr/bin/env python3
"""
Claire v19.84.6 Critical Route Consolidation Plan

Reads:
- data/runtime_authority/canonical_route_owner_registry.json
- audits/v19_84_5_duplicate_route_fail_test/duplicate_route_fail_test_report.json

Writes:
- audits/v19_84_6_critical_route_consolidation_plan/critical_route_consolidation_plan.json
- audits/v19_84_6_critical_route_consolidation_plan/critical_route_consolidation_plan.md

This is read-only. It does not change route mounts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "runtime_authority" / "canonical_route_owner_registry.json"
FAIL_REPORT_PATH = ROOT / "audits" / "v19_84_5_duplicate_route_fail_test" / "duplicate_route_fail_test_report.json"
OUT_DIR = ROOT / "audits" / "v19_84_6_critical_route_consolidation_plan"
OUT_JSON = OUT_DIR / "critical_route_consolidation_plan.json"
OUT_MD = OUT_DIR / "critical_route_consolidation_plan.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def build_action_for_failure(failure: Dict[str, Any], registry_routes: Dict[str, Any]) -> Dict[str, Any]:
    route = failure.get("route")
    spec = registry_routes.get(route, {})
    failure_type = failure.get("failure")

    if failure_type == "duplicate_route_owner":
        action = "demote_duplicate_owners"
        required_change = (
            "Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, "
            "rename duplicate paths, or remove their router mount from create_app."
        )
        safety = "Do not change payload schema or cockpit fetch route."
    elif failure_type == "missing_route":
        action = "restore_or_map_missing_route"
        required_change = (
            "Restore the canonical backend route or update the registry/cockpit contract if the route was intentionally replaced."
        )
        safety = "Do not create frontend fallback truth to compensate for missing backend route."
    else:
        action = "inspect_route_state"
        required_change = "Inspect manually before modifying."
        safety = "No route mutation until owner is identified."

    return {
        "route": route,
        "method": failure.get("method"),
        "key": failure.get("key"),
        "failure": failure_type,
        "owner_count": failure.get("owner_count"),
        "canonical_owner": spec.get("canonical_owner", "unknown"),
        "truth_owner": spec.get("truth_owner", "backend"),
        "cockpit_role": spec.get("cockpit_role", "presentation_only"),
        "action": action,
        "required_change": required_change,
        "safety_rule": safety,
        "owners_seen": failure.get("owners", []),
        "next_build_target": "v19.84.7" if failure_type else "manual_inspection",
    }


def build_plan() -> Dict[str, Any]:
    registry = load_json(REGISTRY_PATH)
    fail_report = load_json(FAIL_REPORT_PATH)
    registry_routes = registry.get("routes", {}) if isinstance(registry, dict) else {}
    evaluation = fail_report.get("evaluation", {}) if isinstance(fail_report, dict) else {}
    failures = evaluation.get("failures", []) if isinstance(evaluation, dict) else []
    passing = evaluation.get("passing", []) if isinstance(evaluation, dict) else []

    actions = [build_action_for_failure(item, registry_routes) for item in failures]

    if failures:
        status = "consolidation_required"
        recommendation = "Do not proceed to cockpit binding lock until critical route failures are resolved."
        next_build = "v19.84.7 Critical Route Owner Demotion"
    else:
        status = "ready_for_cockpit_binding_lock"
        recommendation = "No critical route failures reported. Proceed to cockpit fetch-map/binding lock."
        next_build = "v19.84.7 Cockpit Canonical Fetch Map"

    return {
        "version": "v19.84.6",
        "build": "Critical Route Consolidation Plan",
        "generated_at": utc_now(),
        "status": status,
        "read_only": True,
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "inputs": {
            "registry": str(REGISTRY_PATH.relative_to(ROOT)),
            "duplicate_route_report": str(FAIL_REPORT_PATH.relative_to(ROOT)),
            "registry_present": REGISTRY_PATH.exists(),
            "duplicate_route_report_present": FAIL_REPORT_PATH.exists(),
        },
        "summary": {
            "critical_route_count": len(registry_routes),
            "passing_critical_routes": len(passing),
            "failing_critical_routes": len(failures),
            "duplicate_failures": len([f for f in failures if f.get("failure") == "duplicate_route_owner"]),
            "missing_failures": len([f for f in failures if f.get("failure") == "missing_route"]),
        },
        "actions": actions,
        "passing": passing,
        "recommendation": recommendation,
        "next_build": next_build,
    }


def write_markdown(plan: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Claire v19.84.6 Critical Route Consolidation Plan")
    lines.append("")
    lines.append(f"- Generated: `{plan['generated_at']}`")
    lines.append(f"- Status: `{plan['status']}`")
    lines.append(f"- Read-only: `{plan['read_only']}`")
    lines.append(f"- Backend owns truth: `{plan['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{plan['cockpit_owns_presentation_only']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in plan["summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Required Actions")
    lines.append("")
    if plan["actions"]:
        for item in plan["actions"]:
            lines.append(f"### `{item['key']}`")
            lines.append(f"- Failure: `{item['failure']}`")
            lines.append(f"- Canonical owner: `{item['canonical_owner']}`")
            lines.append(f"- Action: `{item['action']}`")
            lines.append(f"- Required change: {item['required_change']}")
            lines.append(f"- Safety rule: {item['safety_rule']}")
            if item["owners_seen"]:
                lines.append("- Owners seen:")
                for owner in item["owners_seen"]:
                    lines.append(f"  - `{owner.get('endpoint', '')}`")
            lines.append("")
    else:
        lines.append("No critical route consolidation actions required by v19.84.5.")
        lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(plan["recommendation"])
    lines.append("")
    lines.append(f"Next build: `{plan['next_build']}`")
    lines.append("")
    return "\n".join(lines)


def write_plan() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(plan), encoding="utf-8")
    return plan


def main() -> int:
    plan = write_plan()
    print(json.dumps({
        "status": plan["status"],
        "version": plan["version"],
        "failing_critical_routes": plan["summary"]["failing_critical_routes"],
        "duplicate_failures": plan["summary"]["duplicate_failures"],
        "missing_failures": plan["summary"]["missing_failures"],
        "next_build": plan["next_build"],
        "report": {
            "json": str(OUT_JSON.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
