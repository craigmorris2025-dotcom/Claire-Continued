#!/usr/bin/env python3
"""
Claire v19.85.8 Evidence Governance Plateau Gate
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_85_8_evidence_governance_plateau_gate"
OUT_JSON = OUT_DIR / "evidence_governance_plateau_gate.json"

REQUIRED_CONTRACTS = [
    "evidence_escalation_policy.json",
    "evidence_basket_contract.json",
    "route_specific_evidence_thresholds.json",
    "thin_input_escalation_blocker.json",
    "evidence_gate_runtime_adapter.json",
    "evidence_lineage_propagation_contract.json",
    "review_queue_promotion_gate.json",
    "runtime_artifact_integrity_check.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_plateau() -> Dict[str, Any]:
    base = ROOT / "data" / "evidence_governance"
    missing = []
    present = []
    for name in REQUIRED_CONTRACTS:
        path = base / name
        if path.exists():
            present.append(str(path.relative_to(ROOT)))
        else:
            missing.append(str(path.relative_to(ROOT)))
    return {
        "version": "v19.85.8",
        "build": "Evidence Governance Plateau Gate",
        "generated_at": utc_now(),
        "status": "plateau_ready" if not missing else "plateau_blocked",
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "required_contract_count": len(REQUIRED_CONTRACTS),
        "present_count": len(present),
        "missing_count": len(missing),
        "present": present,
        "missing": missing,
        "next_build": "v19.86.0 Source Universe Evidence Lineage" if not missing else "repair_missing_evidence_contracts",
    }


def write_gate() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = check_plateau()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_gate()
    print(json.dumps({
        "status": report["status"],
        "version": report["version"],
        "present": report["present_count"],
        "missing": report["missing_count"],
        "next_build": report["next_build"],
    }, indent=2))
    return 0 if report["status"] == "plateau_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
