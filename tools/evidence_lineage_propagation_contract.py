#!/usr/bin/env python3
"""
Claire v19.85.5 Evidence Lineage Propagation Contract
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_85_5_evidence_lineage_propagation_contract"
OUT_JSON = OUT_DIR / "evidence_lineage_propagation_contract.json"
CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "evidence_lineage_propagation_contract.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.5",
        "build": "Evidence Lineage Propagation Contract",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "required_lineage_fields": [
            "source_universe",
            "source_type",
            "source_identifier",
            "ingestion_id",
            "retrieval_path",
            "retrieved_at",
            "evidence_id",
        ],
        "propagation_targets": [
            "runtime_status",
            "lifecycle_state",
            "gate_decisions",
            "review_queue",
            "candidate_payload",
            "export_package",
        ],
        "rules": [
            "Lineage must be preserved across runtime artifacts.",
            "Candidate payloads must not strip evidence identifiers.",
            "Review queue items must reference evidence basket ids.",
            "Exports must include evidence lineage or state insufficient evidence.",
        ],
    }


def validate_lineage_item(item: Dict[str, Any], contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    contract = contract or build_contract()
    missing = []
    for field in contract["required_lineage_fields"]:
        if field not in item or item.get(field) in {None, ""}:
            missing.append(field)
    return {
        "status": "valid" if not missing else "invalid",
        "missing_fields": missing,
        "has_required_lineage": not missing,
    }


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {
        "version": "v19.85.5",
        "build": "Evidence Lineage Propagation Contract",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "next_build": "v19.85.6 Review Queue Promotion Gate",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({"status": "ok", "version": report["version"], "contract_path": report["contract_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
