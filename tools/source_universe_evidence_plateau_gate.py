#!/usr/bin/env python3
"""
Claire v19.86.4 Source Universe Evidence Plateau Gate
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_86_4_source_universe_evidence_plateau_gate"
OUT_JSON = OUT_DIR / "source_universe_evidence_plateau_gate.json"

REQUIRED = [
    "source_universe_evidence_lineage.json",
    "source_probe_result_schema.json",
    "probe_to_evidence_basket_builder.json",
    "source_trust_rejection_reasons.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_plateau():
    base = ROOT / "data" / "source_universes"
    missing = [name for name in REQUIRED if not (base / name).exists()]
    return {
        "version":"v19.86.4",
        "build":"Source Universe Evidence Plateau Gate",
        "generated_at":utc_now(),
        "status":"plateau_ready" if not missing else "plateau_blocked",
        "missing":missing,
        "present_count":len(REQUIRED)-len(missing),
        "required_count":len(REQUIRED),
        "next_build":"v19.87.0 Continuous Governed Runtime Scheduler" if not missing else "repair_source_universe_contracts",
    }


def write_gate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = check_plateau()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_gate()
    print(json.dumps({"status":report["status"],"version":report["version"],"missing":len(report["missing"]),"next_build":report["next_build"]}, indent=2))
    return 0 if report["status"] == "plateau_ready" else 1

if __name__ == "__main__":
    raise SystemExit(main())
