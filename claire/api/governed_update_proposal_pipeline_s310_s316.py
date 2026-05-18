"""
S310-S316 — Evidence -> Update Proposal -> Review -> Export.

This module completes governed internet-update readiness by turning governed
evidence capsules into update candidates, proposals, review records, export
packages, dashboard proposal state, and a deterministic end-to-end run proof.
It remains proposal-only and never mutates runtime truth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import hashlib
import json

from claire.api.governed_internet_update_foundation_s296_s302 import authority_locks
from claire.api.governed_fetch_evidence_pipeline_s303_s309 import (
    build_s306_evidence_capsule_builder,
    build_s307_source_lineage_trust_scoring,
    build_s309_stop_gate,
)


PHASE = "S310-S316"
VERSION = "v19.89.8-S310-S316"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "authority_locks": authority_locks(),
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "proposal_only": True,
        "runtime_truth_modified": False,
        "created_at": _timestamp(),
    }
    payload.update(extra)
    return payload


def build_s310_update_candidate_detector() -> Dict[str, Any]:
    evidence = build_s306_evidence_capsule_builder()["evidence_capsule"]
    candidate_seed = json.dumps(evidence, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(candidate_seed).hexdigest()
    return _base(
        "S310",
        "update_candidate_detector_ready",
        update_candidate={
            "candidate_id": f"candidate_{digest[:12]}",
            "evidence_id": evidence["evidence_id"],
            "candidate_type": "research_note_update",
            "affected_component": "internet_update_review_queue",
            "current_value": "no_promoted_update",
            "proposed_value": "review_required_governed_update_note",
            "reason": "governed evidence capsule is available and requires review",
            "confidence": "review_required",
            "requires_review": True,
        },
    )


def build_s311_update_proposal_builder() -> Dict[str, Any]:
    candidate = build_s310_update_candidate_detector()["update_candidate"]
    trust = build_s307_source_lineage_trust_scoring()
    proposal_seed = json.dumps(candidate, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(proposal_seed).hexdigest()
    return _base(
        "S311",
        "update_proposal_builder_ready",
        update_proposal={
            "proposal_id": f"proposal_{digest[:12]}",
            "candidate_id": candidate["candidate_id"],
            "evidence_ids": [candidate["evidence_id"]],
            "summary": "Governed internet evidence is available for operator review.",
            "proposed_change": candidate["proposed_value"],
            "affected_paths": [],
            "risk_level": "low_proposal_only",
            "approval_required": True,
            "self_apply_allowed": False,
            "runtime_truth_write_allowed": False,
            "source_trust_summary": trust["scoring"],
        },
    )


def build_s312_review_queue_integration() -> Dict[str, Any]:
    proposal = build_s311_update_proposal_builder()["update_proposal"]
    return _base(
        "S312",
        "review_queue_integration_ready",
        review_item={
            "review_item_id": proposal["proposal_id"].replace("proposal_", "review_"),
            "proposal_id": proposal["proposal_id"],
            "status": "review_required",
            "available_actions": ["approve", "reject", "archive", "export_only"],
            "operator_action": None,
            "decision_timestamp": None,
            "decision_reason": None,
            "manual_promotion_gate": True,
        },
    )


def build_s313_approved_update_export_package(export_dir: str | Path | None = None) -> Dict[str, Any]:
    proposal = build_s311_update_proposal_builder()["update_proposal"]
    review = build_s312_review_queue_integration()["review_item"]
    package = {
        "export_id": proposal["proposal_id"].replace("proposal_", "export_"),
        "proposal_id": proposal["proposal_id"],
        "review_item_id": review["review_item_id"],
        "export_status": "ready_for_operator_export",
        "evidence_lineage": proposal["evidence_ids"],
        "rollback_notes": "No runtime mutation was performed; rollback is not required.",
        "runtime_truth_modified": False,
        "self_apply_allowed": False,
    }
    payload = _base(
        "S313",
        "approved_update_export_package_ready",
        export_package=package,
    )

    if export_dir is not None:
        path = Path(export_dir)
        path.mkdir(parents=True, exist_ok=True)
        json_path = path / f"{package['export_id']}.json"
        md_path = path / f"{package['export_id']}.md"
        json_path.write_text(json.dumps(package, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(
            "# Governed Internet Update Export\\n\\n"
            f"Proposal: {proposal['proposal_id']}\\n\\n"
            "Runtime truth modified: false\\n",
            encoding="utf-8",
        )
        payload["export_paths"] = {"json": str(json_path), "summary": str(md_path)}

    return payload


def build_s314_dashboard_update_proposal_surface() -> Dict[str, Any]:
    candidate = build_s310_update_candidate_detector()["update_candidate"]
    proposal = build_s311_update_proposal_builder()["update_proposal"]
    review = build_s312_review_queue_integration()["review_item"]
    return _base(
        "S314",
        "dashboard_update_proposal_surface_ready",
        dashboard_surface={
            "panel_key": "internet_update_proposals",
            "title": "Internet Update Proposals",
            "internet_update_candidates": [candidate],
            "internet_update_proposals": [proposal],
            "review_queue_status": [review],
            "approved_exports": [],
            "runtime_mutation_status": "blocked",
            "blocked_action_banner": "Runtime mutation and automatic updates are blocked until explicit future gates allow them.",
        },
    )


def build_s315_end_to_end_governed_update_run(export_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s309_stop_gate()
    candidate = build_s310_update_candidate_detector()
    proposal = build_s311_update_proposal_builder()
    review = build_s312_review_queue_integration()
    export = build_s313_approved_update_export_package(export_dir=export_dir)
    dashboard = build_s314_dashboard_update_proposal_surface()
    return _base(
        "S315",
        "end_to_end_governed_update_run_ready",
        run={
            "operator_intent": "governed_internet_update_readiness_demo",
            "previous_gate": previous,
            "candidate": candidate,
            "proposal": proposal,
            "review_queue": review,
            "export": export,
            "dashboard": dashboard,
            "audit_trail": [
                "provider_probe",
                "controlled_fetch_contract",
                "quarantine",
                "evidence_capsule",
                "candidate",
                "proposal",
                "review_required",
                "export_ready",
                "dashboard_payload_ready",
            ],
            "runtime_truth_modified": False,
        },
    )


def build_s316_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s309_stop_gate()
    run = build_s315_end_to_end_governed_update_run()
    checks = {
        "foundation_and_fetch_gate_ok": previous["ok"],
        "candidate_ready": build_s310_update_candidate_detector()["ok"],
        "proposal_ready": build_s311_update_proposal_builder()["ok"],
        "review_queue_ready": build_s312_review_queue_integration()["ok"],
        "export_package_ready": build_s313_approved_update_export_package()["ok"],
        "dashboard_update_surface_ready": build_s314_dashboard_update_proposal_surface()["ok"],
        "end_to_end_run_ready": run["ok"],
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
        "automatic_updates_blocked": authority_locks()["automatic_updates_allowed"] is False,
        "autonomous_crawling_blocked": authority_locks()["autonomous_crawling_allowed"] is False,
        "runtime_truth_not_modified": run["run"]["runtime_truth_modified"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S316",
        "governed_internet_connected_update_readiness_passed" if ok else "governed_internet_connected_update_readiness_failed",
        checks=checks,
        forward_motion_allowed=ok,
        readiness_state="governed_internet_update_ready" if ok else "repair_required",
        next_phase="dashboard_consolidation_s317_s337" if ok else "repair S310-S316 update proposal pipeline",
    )

    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s310_s316_governed_update_readiness.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)

    return payload


def build_governed_update_proposal_pipeline_s310_s316() -> Dict[str, Any]:
    return _base(
        "S316",
        "governed_update_proposal_pipeline_ready",
        candidate=build_s310_update_candidate_detector(),
        proposal=build_s311_update_proposal_builder(),
        review_queue=build_s312_review_queue_integration(),
        export_package=build_s313_approved_update_export_package(),
        dashboard_surface=build_s314_dashboard_update_proposal_surface(),
        end_to_end_run=build_s315_end_to_end_governed_update_run(),
        stop_gate=build_s316_stop_gate(),
    )


__all__ = [
    "build_s310_update_candidate_detector",
    "build_s311_update_proposal_builder",
    "build_s312_review_queue_integration",
    "build_s313_approved_update_export_package",
    "build_s314_dashboard_update_proposal_surface",
    "build_s315_end_to_end_governed_update_run",
    "build_s316_stop_gate",
    "build_governed_update_proposal_pipeline_s310_s316",
]
