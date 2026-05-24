from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_discovery_candidates import build_discovery_candidate
from runtime_core.api.governed_useful_outputs import build_useful_output_candidate
from runtime_core.api.governed_review_queue import enqueue_for_review, decide_review_item
from runtime_core.api.governed_reviewed_exports import export_reviewed_output
from runtime_core.api.governed_route_repeat import build_route_repeat_payload

def build_demo_contract(evidence_basket: Mapping[str, Any], extraction: Mapping[str, Any] | None = None, *, route: str = "portfolio", store_path: Path | None = None, export_dir: Path | None = None, approve: bool = True) -> Dict[str, Any]:
    discovery = build_discovery_candidate(evidence_basket, extraction, requested_route=route)
    output = build_useful_output_candidate(discovery)
    review_item = enqueue_for_review(output, store_path=store_path, operator="demo_contract")
    decision_payload = None
    export_payload = None
    if approve:
        decision_payload = decide_review_item(
            review_item["review_item_id"],
            "approved",
            store_path=store_path,
            operator="demo_contract",
            note="S90 controlled demo approval for export proof only.",
        )
        export_payload = export_reviewed_output(decision_payload["review_item"], export_dir=export_dir, export_format="json")
    return {
        "demo_contract_version": "S90",
        "status": "demo_export_ready" if export_payload else "review_required",
        "path": [
            "manual_probe",
            "quarantine",
            "evidence_basket",
            "extraction",
            "discovery_candidate",
            "useful_output_candidate",
            "review_queue",
            "approval" if approve else "pending_review",
            "export" if export_payload else "no_export",
        ],
        "discovery_candidate": discovery,
        "useful_output_candidate": output,
        "review_item": decision_payload["review_item"] if decision_payload else review_item,
        "review_decision": decision_payload["decision"] if decision_payload else None,
        "export": export_payload,
        "authority": {
            "runtime_truth_write": "blocked",
            "runtime_truth_mutation": "blocked",
            "automatic_updates": "blocked",
            "autonomous_execution": "blocked",
            "live_web_execution": "blocked_unless_explicitly_gated",
        },
    }

def build_demo_readiness_proof(evidence_basket: Mapping[str, Any], extraction: Mapping[str, Any] | None = None, *, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    demo = build_demo_contract(evidence_basket, extraction, route="portfolio", store_path=store_path, export_dir=export_dir, approve=True)
    route_repeat = build_route_repeat_payload(evidence_basket, extraction, store_path=store_path)
    export = demo.get("export") or {}
    return {
        "demo_readiness_version": "S91",
        "status": "ready" if export.get("status") == "exported" else "not_ready",
        "proof_chain": {
            "evidence_present": bool(evidence_basket),
            "extraction_present": bool(extraction),
            "candidate_present": bool(demo.get("discovery_candidate")),
            "useful_output_present": bool(demo.get("useful_output_candidate")),
            "review_decision_present": bool(demo.get("review_decision")),
            "export_present": export.get("status") == "exported",
            "route_repeat_present": route_repeat.get("status") == "route_repeat_ready",
        },
        "demo": demo,
        "route_repeat": route_repeat,
        "operator_statement": "S91 proof shows governed evidence can become a candidate, useful output, reviewed artifact, and export without runtime truth mutation.",
    }
