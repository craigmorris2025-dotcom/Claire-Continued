#!/usr/bin/env python3
"""
Claire v19.84.9 Cockpit Binding Contract Lock

Purpose:
- Create the canonical cockpit fetch contract.
- Lock the cockpit to backend-owned truth routes.
- Flag unapproved frontend fetch dependencies.
- Flag frontend truth-synthesis risk patterns.

Read-only: does not rewrite cockpit files.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

FETCH_MAP_PATH = ROOT / "audits" / "v19_84_8_cockpit_canonical_fetch_map" / "cockpit_canonical_fetch_map.json"
REGISTRY_PATH = ROOT / "data" / "runtime_authority" / "canonical_route_owner_registry.json"

CONTRACT_DIR = ROOT / "data" / "cockpit"
CONTRACT_PATH = CONTRACT_DIR / "canonical_cockpit_fetch_contract.json"

OUT_DIR = ROOT / "audits" / "v19_84_9_cockpit_binding_contract_lock"
OUT_JSON = OUT_DIR / "cockpit_binding_contract_lock.json"
OUT_MD = OUT_DIR / "cockpit_binding_contract_lock.md"

ALLOWED_CANONICAL_FETCHES = {
    "/dashboard/payload": {
        "method": "GET",
        "purpose": "Primary cockpit runtime payload.",
        "truth_owner": "backend",
        "required": True,
    },
    "/dashboard/payload/status": {
        "method": "GET",
        "purpose": "Payload availability and backend truth status.",
        "truth_owner": "backend",
        "required": True,
    },
    "/runtime/continuous/status": {
        "method": "GET",
        "purpose": "Continuous governed runtime status.",
        "truth_owner": "backend",
        "required": True,
    },
    "/runtime/continuous/review-queue": {
        "method": "GET",
        "purpose": "Operator review queue.",
        "truth_owner": "backend",
        "required": True,
    },
    "/runs/start": {
        "method": "POST",
        "purpose": "Operator-commanded manual run start.",
        "truth_owner": "backend",
        "required": True,
    },
    "/universes": {
        "method": "GET",
        "purpose": "Configured source universe list.",
        "truth_owner": "backend",
        "required": True,
    },
    "/health": {
        "method": "GET",
        "purpose": "Backend runtime health check.",
        "truth_owner": "backend",
        "required": False,
    },
    "/docs": {
        "method": "GET",
        "purpose": "Developer/API documentation surface; not an operator cockpit dependency.",
        "truth_owner": "backend",
        "required": False,
        "operator_cockpit_dependency": False,
    },
}

BLOCKED_FRONTEND_TRUTH_PATTERNS = [
    "mockData",
    "syntheticPayload",
    "fakePayload",
    "generatedPayload",
    "fallbackTruth",
    "hardcodedResults",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.84.9",
        "build": "Cockpit Binding Contract Lock",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "frontend_truth_generation_allowed": False,
        "empty_pending_unavailable_states_are_valid": True,
        "allowed_fetches": ALLOWED_CANONICAL_FETCHES,
        "blocked_frontend_truth_patterns": BLOCKED_FRONTEND_TRUTH_PATTERNS,
        "binding_rules": [
            "Cockpit may only fetch from allowed backend-owned routes unless explicitly registered.",
            "Cockpit must render unavailable/pending/empty states instead of synthesizing truth.",
            "Cockpit may issue operator commands only to registered operator_command routes.",
            "Cockpit must not create discoveries, route decisions, candidate counts, scores, or narratives locally.",
            "Backend payload is the sole source of runtime truth.",
        ],
    }


def evaluate_contract(fetch_map: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    allowed = contract.get("allowed_fetches", {})
    mapping = fetch_map.get("mapping", {}) if isinstance(fetch_map, dict) else {}
    risks = fetch_map.get("truth_risks", []) if isinstance(fetch_map, dict) else []

    for route, item in mapping.items():
        if route not in allowed:
            warnings.append({
                "area": "frontend_fetch",
                "route": route,
                "reason": "fetch_route_not_in_allowed_contract",
                "recommended_action": "Register route intentionally or remove cockpit dependency.",
                "references": item.get("frontend_references", []),
            })
        else:
            if item.get("truth_owner") not in {None, "backend"}:
                blockers.append({
                    "area": "truth_owner",
                    "route": route,
                    "reason": "allowed route does not resolve to backend truth owner",
                })

    for risk in risks:
        blockers.append({
            "area": "frontend_truth_synthesis",
            "file": risk.get("file"),
            "pattern": risk.get("pattern"),
            "reason": "blocked frontend truth-synthesis pattern detected",
        })

    required_missing = []
    for route, spec in allowed.items():
        if spec.get("required") and route not in mapping:
            required_missing.append(route)

    for route in required_missing:
        warnings.append({
            "area": "required_fetch",
            "route": route,
            "reason": "required canonical fetch not observed in frontend scan",
            "recommended_action": "Confirm cockpit loads this route through indirect fetch map or add explicit binding.",
        })

    return {
        "status": "locked_with_blockers" if blockers else "locked_with_warnings" if warnings else "locked_clean",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "allowed_fetch_count": len(allowed),
        "observed_fetch_count": len(mapping),
        "required_missing": required_missing,
    }


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Claire v19.84.9 Cockpit Binding Contract Lock")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Backend owns truth: `{report['contract']['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{report['contract']['cockpit_owns_presentation_only']}`")
    lines.append(f"- Allowed fetches: `{report['evaluation']['allowed_fetch_count']}`")
    lines.append(f"- Observed fetches: `{report['evaluation']['observed_fetch_count']}`")
    lines.append(f"- Blockers: `{report['evaluation']['blocker_count']}`")
    lines.append(f"- Warnings: `{report['evaluation']['warning_count']}`")
    lines.append("")

    lines.append("## Allowed Fetch Contract")
    lines.append("")
    for route, spec in report["contract"]["allowed_fetches"].items():
        lines.append(f"- `{spec['method']} {route}` — {spec['purpose']}")

    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if report["evaluation"]["blockers"]:
        for item in report["evaluation"]["blockers"]:
            target = item.get("route") or item.get("file") or item.get("area")
            lines.append(f"- `{target}` — `{item.get('reason')}`")
    else:
        lines.append("No blockers.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report["evaluation"]["warnings"]:
        for item in report["evaluation"]["warnings"]:
            target = item.get("route") or item.get("file") or item.get("area")
            lines.append(f"- `{target}` — `{item.get('reason')}`")
    else:
        lines.append("No warnings.")

    lines.append("")
    lines.append(f"Next build: `{report['next_build']}`")
    lines.append("")

    return "\n".join(lines)


def write_lock() -> Dict[str, Any]:
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fetch_map = load_json(FETCH_MAP_PATH)
    registry = load_json(REGISTRY_PATH)
    contract = build_contract()
    evaluation = evaluate_contract(fetch_map, contract)

    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.84.9",
        "build": "Cockpit Binding Contract Lock",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "inputs": {
            "fetch_map": str(FETCH_MAP_PATH.relative_to(ROOT)),
            "fetch_map_present": FETCH_MAP_PATH.exists(),
            "registry": str(REGISTRY_PATH.relative_to(ROOT)),
            "registry_present": REGISTRY_PATH.exists(),
            "registry_backend_truth": registry.get("backend_owns_truth"),
            "registry_cockpit_presentation_only": registry.get("cockpit_owns_presentation_only"),
        },
        "contract": contract,
        "evaluation": evaluation,
        "next_build": (
            "v19.85.0 Evidence Escalation Hardening"
            if evaluation["blocker_count"] == 0
            else "v19.84.10 Cockpit Truth Synthesis Cleanup"
        ),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")

    return report


def main() -> int:
    report = write_lock()

    print(json.dumps({
        "status": report["evaluation"]["status"],
        "version": report["version"],
        "contract_path": report["contract_path"],
        "blockers": report["evaluation"]["blocker_count"],
        "warnings": report["evaluation"]["warning_count"],
        "next_build": report["next_build"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
