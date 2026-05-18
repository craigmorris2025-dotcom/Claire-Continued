#!/usr/bin/env python3
"""
Claire v19.86.2 Probe-to-Evidence Basket Builder
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_86_2_probe_to_evidence_basket_builder"
OUT_JSON = OUT_DIR / "probe_to_evidence_basket_builder.json"
CONTRACT_DIR = ROOT / "data" / "source_universes"
CONTRACT_PATH = CONTRACT_DIR / "probe_to_evidence_basket_builder.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_evidence_basket_from_probe(probe: Dict[str, Any], route_type: str) -> Dict[str, Any]:
    results = probe.get("results", []) or []
    source_universe_id = probe.get("source_universe_id")
    evidence_items = []
    for index, item in enumerate(results):
        evidence_items.append({
            "evidence_id": item.get("result_id") or f"{probe.get('probe_id', 'probe')}-{index}",
            "source_universe": source_universe_id,
            "source_type": "provider",
            "source_identifier": item.get("source_identifier") or probe.get("provider"),
            "source_url": item.get("source_url"),
            "headline": item.get("title", ""),
            "summary": item.get("summary", ""),
            "confidence": float(probe.get("source_trust_score", 0) or 0),
            "confidence_owner": "backend",
            "lineage": {
                "ingestion_id": probe.get("probe_id"),
                "retrieval_path": probe.get("provider"),
                "retrieved_at": item.get("retrieved_at") or probe.get("requested_at"),
                "source_universe_id": source_universe_id,
            },
            "validation": {
                "validated": probe.get("status") == "success",
                "validation_reason": "probe_result_success" if probe.get("status") == "success" else "probe_not_successful",
            },
        })
    return {
        "basket_id": f"basket-{probe.get('probe_id', 'unknown')}",
        "created_at": utc_now(),
        "runtime_id": probe.get("runtime_id", "pending_runtime"),
        "route_type": route_type,
        "terminal_state": "review_required" if evidence_items else "pending_evidence",
        "evidence_items": evidence_items,
        "aggregate_confidence": round(sum(i["confidence"] for i in evidence_items) / len(evidence_items), 4) if evidence_items else 0,
        "aggregate_confidence_owner": "backend",
        "source_universe_count": len({i["source_universe"] for i in evidence_items if i["source_universe"]}),
        "operator_review_required": True,
    }


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.86.2",
        "build": "Probe-to-Evidence Basket Builder",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "builder_function": "build_evidence_basket_from_probe",
        "rule": "Probe results become evidence items only with preserved lineage.",
    }


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {"version":"v19.86.2","read_only":True,"contract_path":str(CONTRACT_PATH.relative_to(ROOT)),"contract":contract}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({"status":"ok","version":report["version"],"contract_path":report["contract_path"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
