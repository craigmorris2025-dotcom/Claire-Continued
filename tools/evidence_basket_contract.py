#!/usr/bin/env python3
"""
Claire v19.85.1 Evidence Basket Contract

Purpose:
- Define canonical evidence basket schema.
- Define evidence lineage structure.
- Define source attribution requirements.
- Define confidence ownership boundaries.
- Produce validation-ready backend contracts.

Read-only schema build.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

OUT_DIR = ROOT / "audits" / "v19_85_1_evidence_basket_contract"
OUT_JSON = OUT_DIR / "evidence_basket_contract.json"
OUT_MD = OUT_DIR / "evidence_basket_contract.md"

CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "evidence_basket_contract.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.1",
        "build": "Evidence Basket Contract",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "basket_schema": {
            "basket_id": "uuid",
            "created_at": "iso8601",
            "runtime_id": "string",
            "route_type": "portfolio|breakthrough|design|acquisition|discovery",
            "terminal_state": "string",
            "evidence_items": [
                {
                    "evidence_id": "uuid",
                    "source_universe": "string",
                    "source_type": "web|internal|document|runtime|provider",
                    "source_identifier": "string",
                    "source_url": "string|null",
                    "headline": "string",
                    "summary": "string",
                    "raw_excerpt": "string",
                    "confidence": "float",
                    "confidence_owner": "backend",
                    "lineage": {
                        "ingestion_id": "uuid",
                        "retrieval_path": "string",
                        "retrieved_at": "iso8601",
                    },
                    "validation": {
                        "validated": "bool",
                        "validation_reason": "string",
                    },
                }
            ],
            "aggregate_confidence": "float",
            "aggregate_confidence_owner": "backend",
            "source_universe_count": "int",
            "operator_review_required": True,
        },
        "lineage_rules": [
            "Every evidence item must contain lineage metadata.",
            "Every evidence item must identify its source universe.",
            "Confidence scores are backend-generated only.",
            "Frontend may render evidence but may not create lineage.",
            "Operator review required before promotion into runtime truth.",
        ],
        "invalid_conditions": [
            "missing_source_universe",
            "missing_lineage",
            "frontend_generated_confidence",
            "empty_evidence_items",
            "synthetic_evidence",
        ],
    }


def validate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if contract.get("backend_owns_truth") is not True:
        blockers.append("backend truth ownership not enforced")

    schema = contract.get("basket_schema", {})

    required_fields = [
        "basket_id",
        "created_at",
        "runtime_id",
        "route_type",
        "terminal_state",
        "evidence_items",
        "aggregate_confidence",
        "aggregate_confidence_owner",
    ]

    for field in required_fields:
        if field not in schema:
            blockers.append(f"missing required basket field: {field}")

    if schema.get("aggregate_confidence_owner") != "backend":
        blockers.append("aggregate confidence owner must be backend")

    if not contract.get("lineage_rules"):
        warnings.append("no lineage rules configured")

    if not contract.get("invalid_conditions"):
        warnings.append("no invalid conditions configured")

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

    lines.append("# Claire v19.85.1 Evidence Basket Contract")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Backend owns truth: `{contract['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{contract['cockpit_owns_presentation_only']}`")
    lines.append("")

    lines.append("## Basket Schema Fields")
    lines.append("")

    for key in contract["basket_schema"].keys():
        lines.append(f"- `{key}`")

    lines.append("")
    lines.append("## Lineage Rules")
    lines.append("")

    for rule in contract["lineage_rules"]:
        lines.append(f"- {rule}")

    lines.append("")
    lines.append("## Invalid Conditions")
    lines.append("")

    for item in contract["invalid_conditions"]:
        lines.append(f"- `{item}`")

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
        "version": "v19.85.1",
        "build": "Evidence Basket Contract",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "evaluation": evaluation,
        "next_build": (
            "v19.85.2 Route-Specific Evidence Thresholds"
            if evaluation["blocker_count"] == 0
            else "v19.85.2 Evidence Basket Repair"
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
