#!/usr/bin/env python3
"""
Claire v19.85.0 Evidence Escalation Hardening

Purpose:
- Formalize evidence escalation thresholds.
- Prevent thin-input promotion into discoveries, breakthroughs, portfolios, or designs.
- Define accepted terminal evidence states.
- Produce backend-owned evidence escalation policy artifacts.

Read-only policy build.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

OUT_DIR = ROOT / "audits" / "v19_85_0_evidence_escalation_hardening"
OUT_JSON = OUT_DIR / "evidence_escalation_hardening.json"
OUT_MD = OUT_DIR / "evidence_escalation_hardening.md"

POLICY_DIR = ROOT / "data" / "evidence_governance"
POLICY_PATH = POLICY_DIR / "evidence_escalation_policy.json"

THIN_INPUT_PATTERNS = [
    "additionalprop1",
    "",
    "{}",
    "test",
    "hello",
    "run",
    "go",
]

TERMINAL_EVIDENCE_STATES = [
    "pending_evidence",
    "insufficient_data",
    "blocked_evidence",
    "review_required",
    "candidate_ready",
    "validated_candidate",
]

ESCALATION_TARGETS = {
    "portfolio": {
        "minimum_evidence_items": 3,
        "minimum_source_universes": 2,
        "minimum_confidence": 0.70,
    },
    "breakthrough": {
        "minimum_evidence_items": 5,
        "minimum_source_universes": 3,
        "minimum_confidence": 0.82,
    },
    "design": {
        "minimum_evidence_items": 6,
        "minimum_source_universes": 3,
        "minimum_confidence": 0.85,
    },
    "acquisition": {
        "minimum_evidence_items": 7,
        "minimum_source_universes": 4,
        "minimum_confidence": 0.88,
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_policy() -> Dict[str, Any]:
    return {
        "version": "v19.85.0",
        "build": "Evidence Escalation Hardening",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "frontend_truth_generation_allowed": False,
        "thin_input_patterns": THIN_INPUT_PATTERNS,
        "terminal_evidence_states": TERMINAL_EVIDENCE_STATES,
        "escalation_targets": ESCALATION_TARGETS,
        "rules": [
            "Thin inputs may not escalate directly into discoveries, breakthroughs, portfolios, or designs.",
            "All escalation routes require evidence baskets with lineage.",
            "Source universe diversity is mandatory for escalation.",
            "Confidence scores must be backend-generated.",
            "Cockpit may render pending or unavailable states without synthesizing conclusions.",
            "Operator review remains mandatory before promotion into runtime truth.",
        ],
    }


def evaluate_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if policy.get("backend_owns_truth") is not True:
        blockers.append("backend truth ownership not enforced")

    if policy.get("frontend_truth_generation_allowed") is not False:
        blockers.append("frontend truth generation improperly allowed")

    if not policy.get("thin_input_patterns"):
        warnings.append("no thin input patterns configured")

    if not policy.get("terminal_evidence_states"):
        blockers.append("terminal evidence states missing")

    for target, spec in policy.get("escalation_targets", {}).items():
        if spec.get("minimum_evidence_items", 0) <= 0:
            blockers.append(f"{target} minimum evidence items invalid")

        if spec.get("minimum_confidence", 0) < 0.5:
            warnings.append(f"{target} confidence threshold unusually low")

    return {
        "status": "locked_clean" if not blockers else "blocked",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
    }


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Claire v19.85.0 Evidence Escalation Hardening")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Backend owns truth: `{report['policy']['backend_owns_truth']}`")
    lines.append(f"- Frontend truth generation allowed: `{report['policy']['frontend_truth_generation_allowed']}`")
    lines.append("")

    lines.append("## Escalation Targets")
    lines.append("")

    for target, spec in report["policy"]["escalation_targets"].items():
        lines.append(f"### `{target}`")
        lines.append(f"- Minimum evidence items: `{spec['minimum_evidence_items']}`")
        lines.append(f"- Minimum source universes: `{spec['minimum_source_universes']}`")
        lines.append(f"- Minimum confidence: `{spec['minimum_confidence']}`")
        lines.append("")

    lines.append("## Terminal Evidence States")
    lines.append("")

    for state in report["policy"]["terminal_evidence_states"]:
        lines.append(f"- `{state}`")

    lines.append("")
    lines.append(f"Next build: `{report['next_build']}`")
    lines.append("")

    return "\n".join(lines)


def write_policy() -> Dict[str, Any]:
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    policy = build_policy()
    evaluation = evaluate_policy(policy)

    POLICY_PATH.write_text(json.dumps(policy, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.85.0",
        "build": "Evidence Escalation Hardening",
        "generated_at": utc_now(),
        "read_only": True,
        "policy_path": str(POLICY_PATH.relative_to(ROOT)),
        "policy": policy,
        "evaluation": evaluation,
        "next_build": (
            "v19.85.1 Evidence Basket Contract"
            if evaluation["blocker_count"] == 0
            else "v19.85.1 Evidence Policy Repair"
        ),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")

    return report


def main() -> int:
    report = write_policy()

    print(json.dumps({
        "status": report["evaluation"]["status"],
        "version": report["version"],
        "policy_path": report["policy_path"],
        "blockers": report["evaluation"]["blocker_count"],
        "warnings": report["evaluation"]["warning_count"],
        "next_build": report["next_build"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
