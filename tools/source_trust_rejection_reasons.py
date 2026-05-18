#!/usr/bin/env python3
"""
Claire v19.86.3 Source Trust and Rejection Reasons
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_86_3_source_trust_rejection_reasons"
OUT_JSON = OUT_DIR / "source_trust_rejection_reasons.json"
CONTRACT_DIR = ROOT / "data" / "source_universes"
CONTRACT_PATH = CONTRACT_DIR / "source_trust_rejection_reasons.json"

MIN_TRUST = 0.55


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_source_trust(source: Dict[str, Any]) -> Dict[str, Any]:
    score = float(source.get("source_trust_score", 0) or 0)
    reasons = []
    if score < MIN_TRUST:
        reasons.append("source_trust_below_minimum")
    if source.get("status") == "blocked_by_governance":
        reasons.append("blocked_by_governance")
    if source.get("status") == "failed":
        reasons.append("probe_failed")
    return {
        "accepted": not reasons,
        "score": score,
        "minimum": MIN_TRUST,
        "rejection_reasons": reasons,
        "status": "accepted" if not reasons else "rejected",
    }


def build_contract() -> Dict[str, Any]:
    return {"version":"v19.86.3","build":"Source Trust and Rejection Reasons","generated_at":utc_now(),"minimum_source_trust":MIN_TRUST,"backend_owns_truth":True}


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {"version":"v19.86.3","read_only":True,"contract_path":str(CONTRACT_PATH.relative_to(ROOT)),"contract":contract}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report

def main() -> int:
    report = write_contract()
    print(json.dumps({"status":"ok","version":report["version"],"contract_path":report["contract_path"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
