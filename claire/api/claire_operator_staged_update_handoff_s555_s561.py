from __future__ import annotations

"""
Claire Operator-Approved Staged Update Handoff — S555-S561

This module defines the final review-only handoff packet before any future real
controlled updater work.

It builds on:
- S541-S547 Update Promotion Decision Packet
- S548-S554 Rollback Proof Packet and Recovery Gate

Purpose:
- define explicit operator approval text requirements
- build staged update handoff eligibility assessment
- build handoff packets for future application owner review
- define application-owner boundary and final pre-application blockers
- mark STOP POINT C: operator-approved staged update handoff exists, but no
  update is applied and no runtime mutation is enabled

No update is applied, no package is installed, no package is downloaded, no
command is executed, no backup is created, no restore is performed, no promotion
occurs, no persistent handoff store is written, and no runtime truth is mutated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S555-S561"
PHASE = "S555-S561"
JS_ASSET = "frontend/cockpit/shell/assets/claire_operator_staged_update_handoff.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_operator_staged_update_handoff.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "package_execution_enabled": False,
    "package_export_performed": False,
    "sandbox_file_write_performed": False,
    "sandbox_created": False,
    "test_execution_performed": False,
    "validation_execution_performed": False,
    "promotion_performed": False,
    "promotion_allowed_now": False,
    "update_apply_allowed": False,
    "backup_created": False,
    "restore_performed": False,
    "rollback_execution_performed": False,
    "recovery_execution_performed": False,
    "handoff_execution_performed": False,
    "application_handoff_performed": False,
    "handoff_persistent_write_performed": False,
}


HANDOFF_STATES = [
    "not_ready",
    "blocked",
    "awaiting_operator_approval",
    "operator_approval_recorded_for_review",
    "ready_for_future_application_owner_review",
]


APPLICATION_OWNER_BOUNDARY_STATES = [
    "no_application_owner_enabled",
    "future_owner_required",
    "blocked_by_missing_rollback_proof",
    "blocked_by_missing_operator_approval",
    "reference_handoff_ready",
]


REQUIRED_APPROVAL_TEXT = (
    "I approve this staged update handoff for future application-owner review only; "
    "I understand this does not apply or install the update."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _stable_id(prefix: str, *parts: Any) -> str:
    joined = "|".join(str(part) for part in parts)
    return f"{prefix}_{abs(hash(joined)) % 10_000_000:07d}"


def _load_promotion_module():
    from claire.api import claire_update_promotion_decision_packet_s541_s547 as promotion

    return promotion


def _load_rollback_module():
    from claire.api import claire_rollback_recovery_gate_s548_s554 as rollback

    return rollback


def _load_validation_plan_module():
    from claire.api import claire_controlled_update_validation_plan_s520_s526 as validation_plan

    return validation_plan


def _load_result_intake_module():
    from claire.api import claire_validation_result_intake_s534_s540 as result_intake

    return result_intake


def _build_eligible_promotion_packet() -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    result_intake = _load_result_intake_module()
    promotion = _load_promotion_module()

    plan = validation_plan.build_controlled_validation_execution_plan()
    supplied_results = [
        {
            "command_id": command.get("command_id"),
            "status": "passed",
            "summary": f"Operator supplied pass result for {command.get('command_id')}.",
            "evidence_refs": [f"operator_evidence_{command.get('command_id')}"],
            "blockers": [],
        }
        for command in plan.get("command_manifest", {}).get("commands", [])
    ]
    intake = result_intake.intake_validation_results(plan, supplied_results)
    evidence_map = result_intake.build_result_evidence_map(intake)
    assessment = result_intake.assess_validation_result_readiness(intake, evidence_map)
    review_packet = result_intake.build_result_review_packet(intake, evidence_map, assessment)
    return promotion.build_promotion_decision_packet(review_packet)


def build_s555_operator_approval_text_contract() -> Dict[str, Any]:
    return _safe_base(
        "S555",
        "operator_approval_text_contract_ready",
        required_approval_text=REQUIRED_APPROVAL_TEXT,
        approval_fields=[
            "operator_approval_text",
            "approval_text_matched",
            "approval_recorded_for_review",
            "approval_scope",
            "approval_does_not_apply_update",
        ],
        approval_rules=[
            "Approval must be explicit.",
            "Approval is only for future application-owner review.",
            "Approval does not apply, install, promote, download, or mutate anything.",
            "Approval can be recorded in a review-only handoff packet.",
        ],
    )


def evaluate_operator_approval_text(operator_approval_text: str | None = None) -> Dict[str, Any]:
    supplied = str(operator_approval_text or "")
    matched = supplied.strip() == REQUIRED_APPROVAL_TEXT

    result = {
        "operator_approval_id": _stable_id("operator_approval", supplied, matched),
        "version": VERSION,
        "created_at": _now(),
        "operator_approval_text": supplied,
        "required_approval_text": REQUIRED_APPROVAL_TEXT,
        "approval_text_matched": matched,
        "approval_recorded_for_review": matched,
        "approval_scope": "future_application_owner_review_only" if matched else "not_approved",
        "approval_does_not_apply_update": True,
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "handoff_execution_performed": False,
    }
    result.update(BLOCKED_AUTHORITY)
    return result


def assess_staged_handoff_eligibility(
    promotion_packet: Optional[Dict[str, Any]] = None,
    rollback_packet: Optional[Dict[str, Any]] = None,
    recovery_gate: Optional[Dict[str, Any]] = None,
    operator_approval: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    rollback_module = _load_rollback_module()

    active_promotion = dict(promotion_packet or _build_eligible_promotion_packet())
    active_rollback = dict(rollback_packet or rollback_module.build_rollback_proof_packet(active_promotion))
    active_recovery_gate = dict(recovery_gate or rollback_module.build_recovery_gate(active_rollback))
    active_approval = dict(operator_approval or evaluate_operator_approval_text())

    blockers: List[str] = []
    if active_promotion.get("decision") != "eligible_for_operator_promotion_review":
        blockers.append("promotion_packet_not_eligible")
    if active_promotion.get("update_apply_allowed") is not False:
        blockers.append("unexpected_update_apply_authority")
    if active_rollback.get("rollback_proven") is not True:
        blockers.append("rollback_not_proven")
    if active_recovery_gate.get("gate_state") != "awaiting_operator_review":
        blockers.append("recovery_gate_not_open")
    if active_approval.get("approval_text_matched") is not True:
        blockers.append("operator_approval_missing_or_mismatched")

    if "promotion_packet_not_eligible" in blockers:
        handoff_state = "blocked"
    elif "operator_approval_missing_or_mismatched" in blockers:
        handoff_state = "awaiting_operator_approval"
    elif blockers:
        handoff_state = "operator_approval_recorded_for_review" if active_approval.get("approval_text_matched") else "not_ready"
    else:
        handoff_state = "ready_for_future_application_owner_review"

    eligibility = {
        "handoff_eligibility_id": _stable_id(
            "handoff_eligibility",
            active_promotion.get("promotion_packet_id"),
            active_rollback.get("rollback_packet_id"),
            active_approval.get("operator_approval_id"),
            handoff_state,
        ),
        "version": VERSION,
        "created_at": _now(),
        "promotion_packet_id": active_promotion.get("promotion_packet_id"),
        "rollback_packet_id": active_rollback.get("rollback_packet_id"),
        "recovery_gate_id": active_recovery_gate.get("recovery_gate_id"),
        "operator_approval_id": active_approval.get("operator_approval_id"),
        "handoff_state": handoff_state,
        "blockers": sorted(set(blockers)),
        "eligible_for_future_application_owner_review": handoff_state == "ready_for_future_application_owner_review",
        "operator_approval_recorded_for_review": active_approval.get("approval_recorded_for_review") is True,
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "application_handoff_performed": False,
    }
    eligibility.update(BLOCKED_AUTHORITY)
    return eligibility


def build_s556_handoff_eligibility_contract() -> Dict[str, Any]:
    approval = evaluate_operator_approval_text(REQUIRED_APPROVAL_TEXT)
    eligibility = assess_staged_handoff_eligibility(operator_approval=approval)
    return _safe_base(
        "S556",
        "staged_handoff_eligibility_contract_ready",
        handoff_states=HANDOFF_STATES,
        sample_eligibility={
            "handoff_state": eligibility["handoff_state"],
            "operator_approval_recorded_for_review": eligibility["operator_approval_recorded_for_review"],
            "eligible_for_future_application_owner_review": eligibility["eligible_for_future_application_owner_review"],
            "update_apply_allowed": eligibility["update_apply_allowed"],
            "blocker_count": len(eligibility["blockers"]),
        },
        eligibility_rules=[
            "Eligibility can be assessed but cannot perform handoff execution.",
            "Rollback proof is still required for true application-owner readiness.",
            "Approval can be recorded for review while apply authority remains blocked.",
        ],
    )


def build_operator_staged_update_handoff_packet(
    promotion_packet: Optional[Dict[str, Any]] = None,
    operator_approval_text: str | None = None,
    operator_note: str | None = None,
) -> Dict[str, Any]:
    rollback_module = _load_rollback_module()

    active_promotion = dict(promotion_packet or _build_eligible_promotion_packet())
    rollback_packet = rollback_module.build_rollback_proof_packet(active_promotion)
    recovery_gate = rollback_module.build_recovery_gate(rollback_packet)
    approval = evaluate_operator_approval_text(operator_approval_text)
    eligibility = assess_staged_handoff_eligibility(active_promotion, rollback_packet, recovery_gate, approval)

    if eligibility["handoff_state"] == "ready_for_future_application_owner_review":
        packet_status = "reference_handoff_ready"
    elif eligibility["handoff_state"] == "blocked":
        packet_status = "blocked"
    elif eligibility["operator_approval_recorded_for_review"]:
        packet_status = "approval_recorded_but_blocked"
    else:
        packet_status = "awaiting_operator_approval"

    packet = {
        "handoff_packet_id": _stable_id("staged_update_handoff", eligibility.get("handoff_eligibility_id"), operator_note or ""),
        "version": VERSION,
        "created_at": _now(),
        "packet_status": packet_status,
        "handoff_state": eligibility["handoff_state"],
        "promotion_packet_id": active_promotion.get("promotion_packet_id"),
        "rollback_packet_id": rollback_packet.get("rollback_packet_id"),
        "recovery_gate_id": recovery_gate.get("recovery_gate_id"),
        "operator_approval": approval,
        "eligibility": eligibility,
        "blockers": eligibility["blockers"],
        "operator_note": str(operator_note or ""),
        "handoff_summary": (
            "Operator approval is recorded for review, but application remains blocked until rollback proof and a future application owner exist."
            if approval.get("approval_text_matched")
            else "Awaiting exact operator approval text before handoff review can be recorded."
        ),
        "review_only": True,
        "application_owner_required": True,
        "application_owner_enabled": False,
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "application_handoff_performed": False,
        "handoff_persistent_write_allowed": False,
        "handoff_persistent_write_performed": False,
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s557_handoff_packet_contract() -> Dict[str, Any]:
    packet = build_operator_staged_update_handoff_packet(
        operator_approval_text=REQUIRED_APPROVAL_TEXT,
        operator_note="S557 sample handoff packet.",
    )
    return _safe_base(
        "S557",
        "operator_staged_update_handoff_packet_contract_ready",
        sample_packet={
            "packet_status": packet["packet_status"],
            "handoff_state": packet["handoff_state"],
            "review_only": packet["review_only"],
            "application_owner_enabled": packet["application_owner_enabled"],
            "update_apply_allowed": packet["update_apply_allowed"],
        },
        packet_rules=[
            "Handoff packet can record explicit operator approval for review.",
            "Handoff packet cannot apply or install an update.",
            "Application owner is required but disabled here.",
            "Persistent handoff storage is not written.",
        ],
    )


def build_application_owner_boundary(handoff_packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    packet = dict(handoff_packet or build_operator_staged_update_handoff_packet())
    blockers = list(packet.get("blockers", []))

    if not packet.get("application_owner_required"):
        state = "no_application_owner_enabled"
    elif "rollback_not_proven" in blockers:
        state = "blocked_by_missing_rollback_proof"
    elif not packet.get("operator_approval", {}).get("approval_text_matched"):
        state = "blocked_by_missing_operator_approval"
    elif packet.get("packet_status") == "reference_handoff_ready":
        state = "reference_handoff_ready"
    else:
        state = "future_owner_required"

    boundary = {
        "application_owner_boundary_id": _stable_id("application_owner_boundary", packet.get("handoff_packet_id"), state),
        "version": VERSION,
        "created_at": _now(),
        "handoff_packet_id": packet.get("handoff_packet_id"),
        "boundary_state": state,
        "application_owner_required": True,
        "application_owner_enabled": False,
        "application_owner_must_verify": [
            "exact_operator_approval",
            "rollback_proof_complete",
            "recovery_gate_open",
            "final_regression_evidence",
            "protected_path_review",
            "separate_application_authority",
        ],
        "blocked_authority": dict(BLOCKED_AUTHORITY),
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "package_install_performed": False,
        "runtime_mutation_enabled": False,
    }
    boundary.update(BLOCKED_AUTHORITY)
    return boundary


def build_s558_application_owner_boundary_contract() -> Dict[str, Any]:
    boundary = build_application_owner_boundary()
    return _safe_base(
        "S558",
        "application_owner_boundary_contract_ready",
        boundary_states=APPLICATION_OWNER_BOUNDARY_STATES,
        sample_boundary={
            "boundary_state": boundary["boundary_state"],
            "application_owner_required": boundary["application_owner_required"],
            "application_owner_enabled": boundary["application_owner_enabled"],
            "update_apply_allowed": boundary["update_apply_allowed"],
        },
        boundary_rules=[
            "Application owner is required later but disabled here.",
            "No application owner can apply updates from this packet.",
            "Separate application authority must be implemented and tested in a later phase.",
        ],
    )


def build_final_pre_application_blocker_packet(handoff_packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    packet = dict(handoff_packet or build_operator_staged_update_handoff_packet())
    boundary = build_application_owner_boundary(packet)

    blockers = list(packet.get("blockers", []))
    required_missing = []
    if packet.get("application_owner_enabled") is False:
        required_missing.append("application_owner_not_enabled")
    if packet.get("update_apply_allowed") is False:
        required_missing.append("update_apply_authority_not_enabled")
    if packet.get("promotion_allowed_now") is False:
        required_missing.append("promotion_authority_not_enabled")
    if packet.get("handoff_persistent_write_performed") is False:
        required_missing.append("handoff_not_persisted")
    if boundary.get("boundary_state") != "reference_handoff_ready":
        required_missing.append(boundary.get("boundary_state"))

    all_blockers = sorted(set(blockers + required_missing))
    blocker_packet = {
        "pre_application_blocker_packet_id": _stable_id("pre_application_blockers", packet.get("handoff_packet_id"), all_blockers),
        "version": VERSION,
        "created_at": _now(),
        "handoff_packet_id": packet.get("handoff_packet_id"),
        "application_owner_boundary_id": boundary.get("application_owner_boundary_id"),
        "blockers": all_blockers,
        "safe_to_apply": False,
        "safe_to_install": False,
        "safe_to_mutate_runtime": False,
        "required_before_application": [
            "complete_rollback_proof",
            "enable_and_test_application_owner",
            "prove_final_regression",
            "persist_handoff_audit_record",
            "operator_final_apply_approval",
        ],
    }
    blocker_packet.update(BLOCKED_AUTHORITY)
    return blocker_packet


def build_s559_pre_application_blocker_contract() -> Dict[str, Any]:
    blocker_packet = build_final_pre_application_blocker_packet()
    return _safe_base(
        "S559",
        "pre_application_blocker_contract_ready",
        sample_blocker_packet={
            "blocker_count": len(blocker_packet["blockers"]),
            "safe_to_apply": blocker_packet["safe_to_apply"],
            "safe_to_install": blocker_packet["safe_to_install"],
            "safe_to_mutate_runtime": blocker_packet["safe_to_mutate_runtime"],
        },
        blocker_rules=[
            "Pre-application blockers remain visible.",
            "A handoff packet does not remove apply blockers.",
            "Future application owner must satisfy all blockers before any update application.",
        ],
    )


def build_s560_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S560",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "operator_staged_update_handoff_panel",
            "operator_approval_text_card",
            "handoff_eligibility_card",
            "handoff_packet_card",
            "application_owner_boundary_card",
            "pre_application_blocker_card",
        ],
        visual_authority="presentation_only",
    )


def build_s561_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s555 = build_s555_operator_approval_text_contract()
    exact_approval = evaluate_operator_approval_text(REQUIRED_APPROVAL_TEXT)
    bad_approval = evaluate_operator_approval_text("approve it")

    eligible_promotion = _build_eligible_promotion_packet()
    approved_handoff = build_operator_staged_update_handoff_packet(
        eligible_promotion,
        operator_approval_text=REQUIRED_APPROVAL_TEXT,
        operator_note="S561 approved review-only handoff sample.",
    )
    unapproved_handoff = build_operator_staged_update_handoff_packet(
        eligible_promotion,
        operator_approval_text="approve it",
    )
    boundary = build_application_owner_boundary(approved_handoff)
    blockers = build_final_pre_application_blocker_packet(approved_handoff)

    s556 = build_s556_handoff_eligibility_contract()
    s557 = build_s557_handoff_packet_contract()
    s558 = build_s558_application_owner_boundary_contract()
    s559 = build_s559_pre_application_blocker_contract()
    s560 = build_s560_cockpit_asset_manifest(project_root)

    checks = {
        "s555_approval_contract_ready": s555["required_approval_text"] == REQUIRED_APPROVAL_TEXT,
        "exact_approval_matches": exact_approval["approval_text_matched"] is True and exact_approval["update_apply_allowed"] is False,
        "bad_approval_rejected": bad_approval["approval_text_matched"] is False,
        "s556_eligibility_ready": s556["sample_eligibility"]["update_apply_allowed"] is False,
        "s557_handoff_packet_ready": s557["sample_packet"]["review_only"] is True and s557["sample_packet"]["application_owner_enabled"] is False,
        "s558_boundary_ready": s558["sample_boundary"]["application_owner_enabled"] is False,
        "s559_blockers_ready": s559["sample_blocker_packet"]["safe_to_apply"] is False,
        "s560_assets_exist": s560["assets"]["js_exists"] is True and s560["assets"]["css_exists"] is True,
        "approved_handoff_records_approval_only": approved_handoff["operator_approval"]["approval_text_matched"] is True and approved_handoff["update_apply_allowed"] is False,
        "unapproved_handoff_waits": unapproved_handoff["operator_approval"]["approval_text_matched"] is False,
        "boundary_blocks_application_owner": boundary["application_owner_enabled"] is False and boundary["update_apply_allowed"] is False,
        "pre_application_blockers_visible": bool(blockers["blockers"]) is True and blockers["safe_to_apply"] is False,
        "no_handoff_execution_or_apply": all(
            value is False
            for value in [
                approved_handoff["application_handoff_performed"],
                approved_handoff["handoff_execution_performed"],
                approved_handoff["update_apply_allowed"],
                approved_handoff["package_install_performed"],
                approved_handoff["runtime_mutation_enabled"],
            ]
        ),
        "all_authority_blocked": all(approved_handoff.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S561",
        "claire_operator_staged_update_handoff_passed" if ok else "claire_operator_staged_update_handoff_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "exact_approval": exact_approval,
            "bad_approval": bad_approval,
            "approved_handoff": approved_handoff,
            "unapproved_handoff": unapproved_handoff,
            "application_owner_boundary": boundary,
            "pre_application_blockers": blockers,
        },
        forward_motion_allowed=ok,
        stop_point="STOP POINT C - operator-approved staged update handoff exists; last safe stop before real controlled updater work.",
        next_phase="S562-S568 Dashboard update-control cockpit wiring",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s561_claire_operator_staged_update_handoff_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_operator_staged_update_handoff_s555_s561(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S555-S561",
        "claire_operator_staged_update_handoff_ready",
        contracts={
            "s555": build_s555_operator_approval_text_contract(),
            "s556": build_s556_handoff_eligibility_contract(),
            "s557": build_s557_handoff_packet_contract(),
            "s558": build_s558_application_owner_boundary_contract(),
            "s559": build_s559_pre_application_blocker_contract(),
            "s560": build_s560_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s561_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "HANDOFF_STATES",
    "APPLICATION_OWNER_BOUNDARY_STATES",
    "REQUIRED_APPROVAL_TEXT",
    "build_s555_operator_approval_text_contract",
    "evaluate_operator_approval_text",
    "assess_staged_handoff_eligibility",
    "build_s556_handoff_eligibility_contract",
    "build_operator_staged_update_handoff_packet",
    "build_s557_handoff_packet_contract",
    "build_application_owner_boundary",
    "build_s558_application_owner_boundary_contract",
    "build_final_pre_application_blocker_packet",
    "build_s559_pre_application_blocker_contract",
    "build_s560_cockpit_asset_manifest",
    "build_s561_stop_gate",
    "build_claire_operator_staged_update_handoff_s555_s561",
]
