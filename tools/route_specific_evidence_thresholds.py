#!/usr/bin/env python3
"""
Claire v19.85.2 Route-Specific Evidence Thresholds

Purpose:
- Define route-specific evidence requirements.
- Bind escalation thresholds to route type.
- Provide reusable validation logic for future runtime enforcement.
- Keep cockpit presentation-only and backend truth ownership intact.

Read-only policy/validation build.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]

POLICY_PATH = ROOT / "data" / "evidence_governance" / "evidence_escalation_policy.json"
BASKET_CONTRACT_PATH = ROOT / "data" / "evidence_governance" / "evidence_basket_contract.json"

OUT_DIR = ROOT / "audits" / "v19_85_2_route_specific_evidence_thresholds"
OUT_JSON = OUT_DIR / "route_specific_evidence_thresholds.json"
OUT_MD = OUT_DIR / "route_specific_evidence_thresholds.md"

CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "route_specific_evidence_thresholds.json"


ROUTE_THRESHOLDS = {
    "discovery": {
        "minimum_evidence_items": 2,
        "minimum_source_universes": 1,
        "minimum_confidence": 0.62,
        "required_dimensions": ["signal_quality", "source_lineage"],
        "allowed_terminal_states": ["candidate_ready", "review_required"],
        "thin_input_terminal_state": "pending_evidence",
    },
    "portfolio": {
        "minimum_evidence_items": 3,
        "minimum_source_universes": 2,
        "minimum_confidence": 0.70,
        "required_dimensions": ["market_signal", "source_lineage", "portfolio_relevance"],
        "allowed_terminal_states": ["candidate_ready", "review_required"],
        "thin_input_terminal_state": "insufficient_data",
    },
    "breakthrough": {
        "minimum_evidence_items": 5,
        "minimum_source_universes": 3,
        "minimum_confidence": 0.82,
        "required_dimensions": ["novelty_signal", "non_obviousness", "source_lineage", "validation_signal"],
        "allowed_terminal_states": ["review_required", "validated_candidate"],
        "thin_input_terminal_state": "blocked_evidence",
    },
    "design": {
        "minimum_evidence_items": 6,
        "minimum_source_universes": 3,
        "minimum_confidence": 0.85,
        "required_dimensions": ["technical_feasibility", "buildability", "source_lineage", "validation_signal"],
        "allowed_terminal_states": ["review_required", "validated_candidate"],
        "thin_input_terminal_state": "blocked_evidence",
    },
    "acquisition": {
        "minimum_evidence_items": 7,
        "minimum_source_universes": 4,
        "minimum_confidence": 0.88,
        "required_dimensions": ["buyer_fit", "market_signal", "strategic_rationale", "source_lineage", "validation_signal"],
        "allowed_terminal_states": ["review_required", "validated_candidate"],
        "thin_input_terminal_state": "blocked_evidence",
    },
}


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
        "version": "v19.85.2",
        "build": "Route-Specific Evidence Thresholds",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "frontend_truth_generation_allowed": False,
        "operator_review_required_before_promotion": True,
        "route_thresholds": ROUTE_THRESHOLDS,
        "failure_terminal_states": {
            "thin_input": "pending_evidence|insufficient_data|blocked_evidence",
            "missing_lineage": "blocked_evidence",
            "insufficient_source_diversity": "insufficient_data",
            "confidence_below_threshold": "review_required",
        },
        "rules": [
            "Route escalation must pass the threshold for its selected route.",
            "Higher-risk routes require more evidence, more source universes, and higher confidence.",
            "Thin input cannot produce breakthrough, design, acquisition, or final package outputs.",
            "Every accepted evidence item must carry lineage.",
            "Operator review remains required before runtime truth promotion.",
        ],
    }


def validate_route_candidate(route_type: str, basket: Dict[str, Any], contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    contract = contract or build_contract()
    thresholds = contract["route_thresholds"].get(route_type)

    if thresholds is None:
        return {
            "status": "blocked",
            "route_type": route_type,
            "terminal_state": "blocked_evidence",
            "reasons": [f"unknown route_type: {route_type}"],
            "passed": False,
        }

    evidence_items = basket.get("evidence_items", []) or []
    source_universe_count = basket.get("source_universe_count")
    if source_universe_count is None:
        source_universe_count = len({item.get("source_universe") for item in evidence_items if item.get("source_universe")})

    aggregate_confidence = float(basket.get("aggregate_confidence", 0) or 0)
    dimensions = set(basket.get("dimensions", []) or [])
    has_lineage = all(bool(item.get("lineage")) for item in evidence_items) if evidence_items else False

    reasons: List[str] = []

    if len(evidence_items) < thresholds["minimum_evidence_items"]:
        reasons.append("insufficient_evidence_items")

    if int(source_universe_count) < thresholds["minimum_source_universes"]:
        reasons.append("insufficient_source_universe_diversity")

    if aggregate_confidence < thresholds["minimum_confidence"]:
        reasons.append("confidence_below_route_threshold")

    missing_dimensions = [dim for dim in thresholds["required_dimensions"] if dim not in dimensions]
    if missing_dimensions:
        reasons.append("missing_required_dimensions:" + ",".join(missing_dimensions))

    if not has_lineage:
        reasons.append("missing_or_incomplete_lineage")

    passed = not reasons

    if passed:
        terminal_state = "review_required"
        status = "passed_requires_operator_review"
    elif "missing_or_incomplete_lineage" in reasons:
        terminal_state = "blocked_evidence"
        status = "blocked"
    elif "insufficient_evidence_items" in reasons or "insufficient_source_universe_diversity" in reasons:
        terminal_state = "insufficient_data"
        status = "insufficient_data"
    else:
        terminal_state = "review_required"
        status = "review_required"

    return {
        "status": status,
        "route_type": route_type,
        "terminal_state": terminal_state,
        "reasons": reasons,
        "passed": passed,
        "observed": {
            "evidence_item_count": len(evidence_items),
            "source_universe_count": int(source_universe_count),
            "aggregate_confidence": aggregate_confidence,
            "dimensions": sorted(dimensions),
            "has_lineage": has_lineage,
        },
        "required": thresholds,
    }


def validate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if contract.get("backend_owns_truth") is not True:
        blockers.append("backend_owns_truth must be true")

    if contract.get("frontend_truth_generation_allowed") is not False:
        blockers.append("frontend truth generation must be false")

    expected_routes = {"discovery", "portfolio", "breakthrough", "design", "acquisition"}
    actual_routes = set(contract.get("route_thresholds", {}).keys())

    missing = expected_routes - actual_routes
    if missing:
        blockers.append("missing route thresholds: " + ",".join(sorted(missing)))

    for route, thresholds in contract.get("route_thresholds", {}).items():
        if thresholds.get("minimum_evidence_items", 0) <= 0:
            blockers.append(f"{route}: invalid minimum_evidence_items")
        if thresholds.get("minimum_source_universes", 0) <= 0:
            blockers.append(f"{route}: invalid minimum_source_universes")
        if thresholds.get("minimum_confidence", 0) < 0.5:
            warnings.append(f"{route}: low minimum_confidence")
        if "source_lineage" not in thresholds.get("required_dimensions", []):
            blockers.append(f"{route}: source_lineage dimension required")

    return {
        "status": "locked_clean" if not blockers else "blocked",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
    }


def write_markdown(report: Dict[str, Any]) -> str:
    contract = report["contract"]
    lines: List[str] = []

    lines.append("# Claire v19.85.2 Route-Specific Evidence Thresholds")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Backend owns truth: `{contract['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{contract['cockpit_owns_presentation_only']}`")
    lines.append("")

    lines.append("## Route Thresholds")
    lines.append("")
    for route, spec in contract["route_thresholds"].items():
        lines.append(f"### `{route}`")
        lines.append(f"- Minimum evidence items: `{spec['minimum_evidence_items']}`")
        lines.append(f"- Minimum source universes: `{spec['minimum_source_universes']}`")
        lines.append(f"- Minimum confidence: `{spec['minimum_confidence']}`")
        lines.append(f"- Required dimensions: `{', '.join(spec['required_dimensions'])}`")
        lines.append(f"- Thin input terminal state: `{spec['thin_input_terminal_state']}`")
        lines.append("")

    lines.append("## Rules")
    lines.append("")
    for rule in contract["rules"]:
        lines.append(f"- {rule}")

    lines.append("")
    lines.append(f"Next build: `{report['next_build']}`")
    lines.append("")

    return "\\n".join(lines)


def write_contract() -> Dict[str, Any]:
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = build_contract()
    evaluation = validate_contract(contract)

    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.85.2",
        "build": "Route-Specific Evidence Thresholds",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "inputs": {
            "evidence_escalation_policy": str(POLICY_PATH.relative_to(ROOT)),
            "evidence_escalation_policy_present": POLICY_PATH.exists(),
            "evidence_basket_contract": str(BASKET_CONTRACT_PATH.relative_to(ROOT)),
            "evidence_basket_contract_present": BASKET_CONTRACT_PATH.exists(),
        },
        "contract": contract,
        "evaluation": evaluation,
        "next_build": (
            "v19.85.3 Thin Input Escalation Blocker"
            if evaluation["blocker_count"] == 0
            else "v19.85.3 Route Threshold Repair"
        ),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")

    return report


def main() -> int:
    report = write_contract()

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
