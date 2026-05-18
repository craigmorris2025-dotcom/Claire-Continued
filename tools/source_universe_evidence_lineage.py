#!/usr/bin/env python3
"""
Claire v19.86.0 Source Universe Evidence Lineage

Defines the canonical evidence lineage contract from source universe -> probe -> evidence basket.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_86_0_source_universe_evidence_lineage"
OUT_JSON = OUT_DIR / "source_universe_evidence_lineage.json"
CONTRACT_DIR = ROOT / "data" / "source_universes"
CONTRACT_PATH = CONTRACT_DIR / "source_universe_evidence_lineage.json"

CANONICAL_UNIVERSES = {
    "market_intelligence": {
        "label": "Market Intelligence",
        "evidence_role": "market_signal",
        "allowed_routes": ["discovery", "portfolio", "acquisition"],
    },
    "technology_breakthroughs": {
        "label": "Technology Breakthroughs",
        "evidence_role": "technology_signal",
        "allowed_routes": ["discovery", "breakthrough", "design"],
    },
    "existing_systems": {
        "label": "Existing Systems",
        "evidence_role": "system_decomposition_signal",
        "allowed_routes": ["discovery", "breakthrough", "design", "acquisition"],
    },
    "acquisition_targets": {
        "label": "Acquisition Targets",
        "evidence_role": "buyer_fit_signal",
        "allowed_routes": ["portfolio", "acquisition"],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.86.0",
        "build": "Source Universe Evidence Lineage",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "universes": CANONICAL_UNIVERSES,
        "lineage_flow": [
            "source_universe",
            "probe_request",
            "probe_result",
            "source_trust_score",
            "evidence_item",
            "evidence_basket",
            "route_gate",
            "review_queue",
        ],
        "rules": [
            "Source universes provide evidence context, not runtime truth.",
            "Every probe result must preserve source_universe_id.",
            "Evidence baskets must preserve universe and probe lineage.",
            "No direct promotion from source universe to runtime truth.",
        ],
    }


def validate_universe(universe_id: str, route_type: str, contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    contract = contract or build_contract()
    universe = contract["universes"].get(universe_id)
    if not universe:
        return {"valid": False, "status": "unknown_universe", "reason": "source universe is not registered"}
    if route_type not in universe["allowed_routes"]:
        return {"valid": False, "status": "route_not_allowed_for_universe", "reason": f"{universe_id} cannot directly support {route_type}"}
    return {"valid": True, "status": "universe_route_allowed", "evidence_role": universe["evidence_role"]}


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {
        "version": "v19.86.0",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "next_build": "v19.86.1 Source Probe Result Schema",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({"status": "ok", "version": report["version"], "contract_path": report["contract_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
