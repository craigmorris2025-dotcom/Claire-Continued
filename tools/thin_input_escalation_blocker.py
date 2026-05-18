#!/usr/bin/env python3
"""
Claire v19.85.3 Thin Input Escalation Blocker

Purpose:
- Detect placeholder, empty, and non-substantive inputs.
- Prevent thin input from escalating into portfolio, breakthrough, design, acquisition, or final package outputs.
- Produce a reusable validation function for future runtime enforcement.
- Keep this build read-only: no runtime route mutation.

This is a policy + validator build.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

POLICY_PATH = ROOT / "data" / "evidence_governance" / "evidence_escalation_policy.json"
ROUTE_THRESHOLDS_PATH = ROOT / "data" / "evidence_governance" / "route_specific_evidence_thresholds.json"

OUT_DIR = ROOT / "audits" / "v19_85_3_thin_input_escalation_blocker"
OUT_JSON = OUT_DIR / "thin_input_escalation_blocker.json"
OUT_MD = OUT_DIR / "thin_input_escalation_blocker.md"

CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "thin_input_escalation_blocker.json"

PLACEHOLDER_TERMS = {
    "additionalprop1",
    "additionalprop2",
    "additionalprop3",
    "string",
    "test",
    "todo",
    "example",
    "sample",
    "placeholder",
    "null",
    "none",
    "undefined",
    "lorem",
    "ipsum",
}

HIGH_ESCALATION_ROUTES = {"breakthrough", "design", "acquisition", "final_package"}
ALL_ESCALATION_ROUTES = {"discovery", "portfolio", "breakthrough", "design", "acquisition", "final_package"}

MINIMUMS = {
    "minimum_raw_characters": 80,
    "minimum_token_count": 10,
    "minimum_unique_token_count": 7,
    "minimum_specificity_score": 0.20,
    "minimum_semantic_density_score": 0.25,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip().lower()
    try:
        return json.dumps(value, sort_keys=True).strip().lower()
    except Exception:
        return str(value).strip().lower()


def tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9_\\-]+", text.lower()) if token]


def compute_input_profile(raw_input: Any) -> Dict[str, Any]:
    text = normalize_text(raw_input)
    tokens = tokenize(text)
    unique_tokens = sorted(set(tokens))
    placeholder_tokens = [token for token in tokens if token in PLACEHOLDER_TERMS]
    placeholder_ratio = (len(placeholder_tokens) / len(tokens)) if tokens else 1.0

    non_placeholder_tokens = [token for token in tokens if token not in PLACEHOLDER_TERMS]
    specificity_score = min(1.0, len(set(non_placeholder_tokens)) / 20.0)
    semantic_density_score = 0.0 if not tokens else min(1.0, len(non_placeholder_tokens) / max(len(tokens), 1))

    return {
        "raw_character_count": len(text),
        "token_count": len(tokens),
        "unique_token_count": len(unique_tokens),
        "placeholder_token_count": len(placeholder_tokens),
        "placeholder_ratio": round(placeholder_ratio, 4),
        "specificity_score": round(specificity_score, 4),
        "semantic_density_score": round(semantic_density_score, 4),
        "tokens": tokens[:50],
        "placeholder_tokens": placeholder_tokens[:50],
        "has_substantive_input": (
            len(text) >= MINIMUMS["minimum_raw_characters"]
            and len(tokens) >= MINIMUMS["minimum_token_count"]
            and len(unique_tokens) >= MINIMUMS["minimum_unique_token_count"]
            and specificity_score >= MINIMUMS["minimum_specificity_score"]
            and semantic_density_score >= MINIMUMS["minimum_semantic_density_score"]
            and placeholder_ratio < 0.35
        ),
    }


def classify_thin_input(raw_input: Any, route_type: str = "discovery") -> Dict[str, Any]:
    profile = compute_input_profile(raw_input)
    route_type = (route_type or "discovery").lower()

    reasons: List[str] = []

    if profile["raw_character_count"] == 0:
        reasons.append("empty_input")

    if profile["raw_character_count"] < MINIMUMS["minimum_raw_characters"]:
        reasons.append("raw_input_too_short")

    if profile["token_count"] < MINIMUMS["minimum_token_count"]:
        reasons.append("token_count_too_low")

    if profile["unique_token_count"] < MINIMUMS["minimum_unique_token_count"]:
        reasons.append("unique_token_count_too_low")

    if profile["placeholder_ratio"] >= 0.35:
        reasons.append("placeholder_ratio_too_high")

    if profile["specificity_score"] < MINIMUMS["minimum_specificity_score"]:
        reasons.append("specificity_score_too_low")

    if profile["semantic_density_score"] < MINIMUMS["minimum_semantic_density_score"]:
        reasons.append("semantic_density_score_too_low")

    thin = bool(reasons) or not profile["has_substantive_input"]

    if not thin:
        terminal_state = "candidate_ready"
        status = "substantive_input"
        allowed_to_escalate = True
    elif route_type in HIGH_ESCALATION_ROUTES:
        terminal_state = "blocked_evidence"
        status = "blocked_thin_input"
        allowed_to_escalate = False
    elif route_type == "portfolio":
        terminal_state = "insufficient_data"
        status = "insufficient_input"
        allowed_to_escalate = False
    else:
        terminal_state = "pending_evidence"
        status = "pending_evidence"

        allowed_to_escalate = False

    return {
        "version": "v19.85.3",
        "route_type": route_type,
        "status": status,
        "terminal_state": terminal_state,
        "allowed_to_escalate": allowed_to_escalate,
        "thin_input": thin,
        "reasons": reasons,
        "profile": profile,
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
    }


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.3",
        "build": "Thin Input Escalation Blocker",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "frontend_truth_generation_allowed": False,
        "placeholder_terms": sorted(PLACEHOLDER_TERMS),
        "minimums": MINIMUMS,
        "route_behavior": {
            "discovery": {
                "thin_input_terminal_state": "pending_evidence",
                "allowed_to_escalate": False,
            },
            "portfolio": {
                "thin_input_terminal_state": "insufficient_data",
                "allowed_to_escalate": False,
            },
            "breakthrough": {
                "thin_input_terminal_state": "blocked_evidence",
                "allowed_to_escalate": False,
            },
            "design": {
                "thin_input_terminal_state": "blocked_evidence",
                "allowed_to_escalate": False,
            },
            "acquisition": {
                "thin_input_terminal_state": "blocked_evidence",
                "allowed_to_escalate": False,
            },
            "final_package": {
                "thin_input_terminal_state": "blocked_evidence",
                "allowed_to_escalate": False,
            },
        },
        "rules": [
            "Thin input must not become discovery, portfolio, breakthrough, design, acquisition, or package truth.",
            "Placeholder terms such as additionalprop1 and string must block high-escalation routes.",
            "Frontend may render the backend terminal state but may not override it.",
            "Substantive raw input and evidence baskets are required before route escalation.",
        ],
    }


def validate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if contract.get("backend_owns_truth") is not True:
        blockers.append("backend_owns_truth must be true")

    if contract.get("frontend_truth_generation_allowed") is not False:
        blockers.append("frontend_truth_generation_allowed must be false")

    if "additionalprop1" not in contract.get("placeholder_terms", []):
        blockers.append("additionalprop1 must be blocked as placeholder input")

    for route in ALL_ESCALATION_ROUTES:
        behavior = contract.get("route_behavior", {}).get(route)
        if not behavior:
            blockers.append(f"missing route behavior for {route}")
            continue
        if behavior.get("allowed_to_escalate") is not False:
            blockers.append(f"thin input must not escalate for {route}")

    if not contract.get("rules"):
        warnings.append("no rules configured")

    return {
        "status": "locked_clean" if not blockers else "blocked",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
    }


def run_self_checks() -> Dict[str, Any]:
    cases = [
        {"name": "empty discovery", "raw_input": "", "route_type": "discovery", "expected_terminal_state": "pending_evidence"},
        {"name": "swagger placeholder breakthrough", "raw_input": "string additionalprop1 additionalprop1", "route_type": "breakthrough", "expected_terminal_state": "blocked_evidence"},
        {"name": "swagger placeholder portfolio", "raw_input": {"additionalProp1": "string"}, "route_type": "portfolio", "expected_terminal_state": "insufficient_data"},
        {
            "name": "substantive discovery",
            "raw_input": "Market signals show rising enterprise demand for governed evidence lineage platforms across corporate strategy teams, with repeated buyer pain around weak signal detection, auditability, and portfolio decision traceability.",
            "route_type": "discovery",
            "expected_terminal_state": "candidate_ready",
        },
    ]

    results = []
    failed = []

    for case in cases:
        result = classify_thin_input(case["raw_input"], case["route_type"])
        passed = result["terminal_state"] == case["expected_terminal_state"]
        row = {
            "name": case["name"],
            "route_type": case["route_type"],
            "expected_terminal_state": case["expected_terminal_state"],
            "observed_terminal_state": result["terminal_state"],
            "passed": passed,
            "status": result["status"],
            "reasons": result["reasons"],
        }
        results.append(row)
        if not passed:
            failed.append(row)

    return {
        "status": "passed" if not failed else "failed",
        "case_count": len(cases),
        "failed_count": len(failed),
        "results": results,
    }


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Claire v19.85.3 Thin Input Escalation Blocker")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Self-check status: `{report['self_checks']['status']}`")
    lines.append(f"- Backend owns truth: `{report['contract']['backend_owns_truth']}`")
    lines.append("")

    lines.append("## Route Behavior")
    lines.append("")
    for route, behavior in report["contract"]["route_behavior"].items():
        lines.append(f"- `{route}` thin input → `{behavior['thin_input_terminal_state']}`")

    lines.append("")
    lines.append("## Self Checks")
    lines.append("")
    for item in report["self_checks"]["results"]:
        lines.append(
            f"- `{item['name']}`: expected `{item['expected_terminal_state']}`, "
            f"observed `{item['observed_terminal_state']}` → `{item['passed']}`"
        )

    lines.append("")
    lines.append(f"Next build: `{report['next_build']}`")
    lines.append("")

    return "\\n".join(lines)


def write_contract() -> Dict[str, Any]:
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = build_contract()
    evaluation = validate_contract(contract)
    self_checks = run_self_checks()

    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.85.3",
        "build": "Thin Input Escalation Blocker",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "inputs": {
            "evidence_escalation_policy": str(POLICY_PATH.relative_to(ROOT)),
            "evidence_escalation_policy_present": POLICY_PATH.exists(),
            "route_specific_evidence_thresholds": str(ROUTE_THRESHOLDS_PATH.relative_to(ROOT)),
            "route_specific_evidence_thresholds_present": ROUTE_THRESHOLDS_PATH.exists(),
        },
        "contract": contract,
        "evaluation": evaluation,
        "self_checks": self_checks,
        "next_build": (
            "v19.85.4 Evidence Gate Runtime Adapter"
            if evaluation["blocker_count"] == 0 and self_checks["status"] == "passed"
            else "v19.85.4 Thin Input Blocker Repair"
        ),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")

    return report


def main() -> int:
    report = write_contract()

    print(json.dumps({
        "status": report["evaluation"]["status"],
        "self_checks": report["self_checks"]["status"],
        "version": report["version"],
        "contract_path": report["contract_path"],
        "blockers": report["evaluation"]["blocker_count"],
        "warnings": report["evaluation"]["warning_count"],
        "next_build": report["next_build"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
