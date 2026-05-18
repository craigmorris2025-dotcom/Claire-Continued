#!/usr/bin/env python3
"""
Claire v19.85.6 Review Queue Promotion Gate
Repair: v19.85.6.1

Fix:
- Required-field validation no longer checks list values inside a set.
- Empty lists are treated as missing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_85_6_review_queue_promotion_gate"
OUT_JSON = OUT_DIR / "review_queue_promotion_gate.json"
CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "review_queue_promotion_gate.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return True
    return False


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.6.1",
        "build": "Review Queue Promotion Gate",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "operator_review_required_before_promotion": True,
        "promotion_allowed_states": ["review_required", "validated_candidate"],
        "promotion_blocked_states": ["pending_evidence", "insufficient_data", "blocked_evidence"],
        "required_fields": [
            "candidate_id",
            "route_type",
            "terminal_state",
            "evidence_basket_id",
            "lineage_refs",
            "operator_review_required",
        ],
    }


def evaluate_promotion_candidate(candidate: Dict[str, Any], contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    contract = contract or build_contract()

    missing = [
        field
        for field in contract["required_fields"]
        if field not in candidate or is_missing_value(candidate.get(field))
    ]

    terminal_state = candidate.get("terminal_state")

    if missing:
        return {
            "promotion_allowed": False,
            "status": "blocked",
            "reason": "missing_required_fields",
            "missing_fields": missing,
        }

    if terminal_state in contract["promotion_blocked_states"]:
        return {
            "promotion_allowed": False,
            "status": "blocked",
            "reason": "terminal_state_blocks_promotion",
            "terminal_state": terminal_state,
        }

    if terminal_state not in contract["promotion_allowed_states"]:
        return {
            "promotion_allowed": False,
            "status": "blocked",
            "reason": "unknown_terminal_state",
            "terminal_state": terminal_state,
        }

    if candidate.get("operator_review_required") is not True:
        return {
            "promotion_allowed": False,
            "status": "blocked",
            "reason": "operator_review_flag_missing",
        }

    return {
        "promotion_allowed": True,
        "status": "review_queue_ready",
        "reason": "candidate_requires_operator_review",
    }


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.85.6.1",
        "build": "Review Queue Promotion Gate Repair",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "next_build": "v19.85.7 Runtime Artifact Integrity Check",
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({
        "status": "ok",
        "version": report["version"],
        "contract_path": report["contract_path"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
