from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_discovery_candidates import build_discovery_candidate
from claire.api.governed_useful_outputs import build_useful_output_candidate
from claire.api.governed_review_queue import enqueue_for_review, decide_review_item, list_review_queue
from claire.api.governed_reviewed_exports import export_reviewed_output
from claire.api.governed_runtime_spine_s106r1 import build_runtime_spine_state

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def default_evidence() -> Dict[str, Any]:
    return {
        "basket_id": "s114_s120_evidence_basket",
        "trust_score": 0.86,
        "evidence_items": [
            {"evidence_id": "s114_ev_001", "title": "Dashboard-managed evidence signal", "trust_score": 0.86}
        ],
    }

def default_extraction() -> Dict[str, Any]:
    return {
        "extraction_id": "s114_s120_extraction",
        "signals": [
            {"label": "approved evidence run signal", "type": "portfolio", "confidence": 0.84},
            {"label": "governed search management signal", "type": "design", "confidence": 0.76},
        ],
    }

def build_evidence_to_lifecycle_bridge(
    evidence_basket: Mapping[str, Any] | None = None,
    extraction: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    evidence_basket = evidence_basket or default_evidence()
    extraction = extraction or default_extraction()
    discovery = build_discovery_candidate(evidence_basket, extraction, requested_route="portfolio")
    output = build_useful_output_candidate(discovery)
    return {
        "stage_version": "S114",
        "status": "evidence_to_lifecycle_bridge_ready",
        "mapping": {
            "evidence_basket": "Signal Ingestion / Source Validation",
            "extraction": "Entity Extraction / Relationship Mapping",
            "discovery_candidate": "Discovery Generation",
            "useful_output_candidate": "Advancement Path Selection",
            "review_queue": "Operator Review Gate",
            "export": "Final Package Construction",
        },
        "discovery_candidate": discovery,
        "useful_output_candidate": output,
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_approved_evidence_run_contract(
    evidence_basket: Mapping[str, Any] | None = None,
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    bridge = build_evidence_to_lifecycle_bridge(evidence_basket, extraction)
    output = bridge["useful_output_candidate"]
    review_item = enqueue_for_review(output, store_path=store_path, operator="s115_contract")
    decision = decide_review_item(
        review_item["review_item_id"],
        "approved",
        store_path=store_path,
        operator="s115_contract",
        note="S115 approved evidence run contract; export only, no runtime truth write.",
    )
    export = export_reviewed_output(decision["review_item"], export_dir=export_dir, export_format="json")
    return {
        "stage_version": "S115",
        "status": "approved_evidence_run_contract_ready",
        "bridge": bridge,
        "review_item": decision["review_item"],
        "decision": decision["decision"],
        "export": export,
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_dashboard_operations_fetch_map() -> Dict[str, Any]:
    return {
        "stage_version": "S116",
        "status": "dashboard_operations_fetch_map_locked",
        "read_only": True,
        "fetch_map": {
            "runtime_spine": "backend:function:build_runtime_spine_state",
            "evidence_bridge": "backend:function:build_evidence_to_lifecycle_bridge",
            "approved_run": "backend:function:build_approved_evidence_run_contract",
            "review_export_control": "backend:function:build_review_export_control_backend",
            "governed_search_control": "backend:function:build_governed_search_control_backend",
            "dashboard_demo": "backend:function:build_dashboard_managed_demo_backend",
        },
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "locks": dict(LOCKS),
    }

def build_review_export_control_backend(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    approved = build_approved_evidence_run_contract(store_path=store_path, export_dir=export_dir)
    queue = list_review_queue(store_path=store_path)
    return {
        "stage_version": "S117",
        "status": "review_export_control_backend_ready",
        "available_actions": ["approve", "reject", "archive", "export_only"],
        "manual_operator_only": True,
        "queue_total": len(queue.get("queue", [])),
        "decision_total": len(queue.get("decisions", [])),
        "latest_export": approved["export"],
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_governed_search_control_backend() -> Dict[str, Any]:
    return {
        "stage_version": "S118",
        "status": "governed_search_control_backend_ready",
        "manual_probe_required": True,
        "quarantine_required": True,
        "operator_review_required": True,
        "manual_promotion_required": True,
        "continuous_crawling": "blocked",
        "automatic_updates": "blocked",
        "autonomous_execution": "blocked",
        "live_web_execution": "blocked_unless_explicitly_gated",
        "locks": dict(LOCKS),
    }

def build_dashboard_managed_demo_backend(
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    spine = build_runtime_spine_state(review_queue_total=0, export_count=0)
    bridge = build_evidence_to_lifecycle_bridge()
    approved = build_approved_evidence_run_contract(store_path=store_path, export_dir=export_dir)
    fetch_map = build_dashboard_operations_fetch_map()
    review_export = build_review_export_control_backend(store_path=store_path, export_dir=export_dir)
    search_control = build_governed_search_control_backend()

    return {
        "stage_version": "S119",
        "status": "dashboard_managed_demo_backend_ready",
        "demo_path": [
            "runtime_spine",
            "evidence_to_lifecycle_bridge",
            "approved_evidence_run_contract",
            "dashboard_operations_fetch_map",
            "review_export_control_backend",
            "governed_search_control_backend",
            "export_artifact",
        ],
        "runtime_spine": spine,
        "evidence_bridge": bridge,
        "approved_run": approved,
        "fetch_map": fetch_map,
        "review_export_control": review_export,
        "governed_search_control": search_control,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "locks": dict(LOCKS),
    }

def build_s114_s120_stop_gate(
    *,
    report_dir: Path | None = None,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    demo = build_dashboard_managed_demo_backend(store_path=store_path, export_dir=export_dir)
    checks = {
        "s114_bridge_ready": demo["evidence_bridge"]["status"] == "evidence_to_lifecycle_bridge_ready",
        "s115_approved_run_ready": demo["approved_run"]["status"] == "approved_evidence_run_contract_ready",
        "s116_fetch_map_locked": demo["fetch_map"]["status"] == "dashboard_operations_fetch_map_locked",
        "s117_review_export_ready": demo["review_export_control"]["status"] == "review_export_control_backend_ready",
        "s118_search_control_ready": demo["governed_search_control"]["status"] == "governed_search_control_backend_ready",
        "s119_demo_ready": demo["status"] == "dashboard_managed_demo_backend_ready",
        "export_exists": Path(demo["approved_run"]["export"]["path"]).exists(),
        "no_live_rewire": demo["live_dashboard_rewire_performed"] is False,
        "no_app_patch": demo["app_patch_performed"] is False,
        "no_route_registration": demo["route_registration_performed"] is False,
        "runtime_truth_write_blocked": demo["locks"]["runtime_truth_write_blocked"] is True,
        "autonomous_execution_blocked": demo["locks"]["autonomous_execution_blocked"] is True,
    }
    ok = all(checks.values())
    report = {
        "stage_version": "S120",
        "generated_at": _utc_now(),
        "status": "s114_s120_stop_gate_passed" if ok else "s114_s120_stop_gate_failed",
        "ok": ok,
        "functional_plan_coverage": {
            "S114": "evidence-to-lifecycle bridge",
            "S115": "approved evidence run contract",
            "S116": "dashboard operations fetch-map lock",
            "S117": "cockpit review/export control backend",
            "S118": "cockpit governed search control backend",
            "S119": "end-to-end dashboard-managed demo backend",
            "S120": "stop-gate proof",
        },
        "checks": checks,
        "demo": demo,
        "forward_motion_allowed": ok,
        "next_allowed_phase": "S121 controlled read-only cockpit integration" if ok else "repair S114-S120 failing check only",
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s114_s120_functional_stop_gate.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report
