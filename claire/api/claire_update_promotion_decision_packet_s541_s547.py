from __future__ import annotations

"""
Claire Update Promotion Decision Packet — S541-S547

This module defines the governed promotion decision packet that follows
controlled validation result intake.

It builds on:
- S520-S526 Controlled Update Validation Execution Plan
- S534-S540 Controlled Validation Result Intake Contract

Purpose:
- assess whether supplied validation results can enter promotion review
- build promotion / hold / rejection decision packets
- define approval boundary requirements
- preserve rollback and operator review gates
- provide cockpit-ready decision packet summaries

No update is promoted, no update is applied, no package is installed, no command
is executed, no test is run, no persistent decision store is written, no runtime
truth is mutated, and automatic updates remain blocked.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S541-S547"
PHASE = "S541-S547"
JS_ASSET = "frontend/cockpit/shell/assets/claire_update_promotion_decision_packet.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_update_promotion_decision_packet.css"


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
    "decision_persistent_write_performed": False,
}


PROMOTION_DECISIONS = [
    "eligible_for_operator_promotion_review",
    "hold_for_more_validation_evidence",
    "blocked_from_promotion",
    "reject_update_candidate",
]


PROMOTION_PACKET_STATUSES = [
    "promotion_review_ready",
    "held",
    "blocked",
    "rejected",
]


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


def _load_validation_plan_module():
    from claire.api import claire_controlled_update_validation_plan_s520_s526 as validation_plan

    return validation_plan


def _load_result_intake_module():
    from claire.api import claire_validation_result_intake_s534_s540 as result_intake

    return result_intake


def _all_passed_supplied_results(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    commands = list(plan.get("command_manifest", {}).get("commands", []))
    return [
        {
            "command_id": command.get("command_id"),
            "status": "passed",
            "summary": f"Operator supplied pass result for {command.get('command_id')}.",
            "evidence_refs": [f"operator_evidence_{command.get('command_id')}"],
            "blockers": [],
        }
        for command in commands
    ]


def _failed_supplied_results(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = _all_passed_supplied_results(plan)
    if results:
        results[0] = {
            "command_id": results[0]["command_id"],
            "status": "failed",
            "summary": "Operator supplied failed validation result.",
            "evidence_refs": ["operator_failure_log"],
            "blockers": ["targeted_validation_failed"],
        }
    return results


def build_s541_promotion_decision_schema() -> Dict[str, Any]:
    return _safe_base(
        "S541",
        "promotion_decision_schema_ready",
        promotion_decisions=PROMOTION_DECISIONS,
        promotion_packet_statuses=PROMOTION_PACKET_STATUSES,
        decision_packet_fields=[
            "promotion_packet_id",
            "decision",
            "packet_status",
            "result_review_packet_id",
            "readiness_assessment_id",
            "evidence_summary",
            "blockers",
            "required_before_apply",
            "operator_approval_boundary",
            "promotion_allowed_now",
            "update_apply_allowed",
            "promotion_performed",
        ],
        decision_rules=[
            "Promotion decision packet is review-only.",
            "Eligible does not mean applied.",
            "Operator approval, rollback proof, and separate application authority remain required.",
            "Failed or missing validation results block promotion review.",
        ],
    )


def build_promotion_eligibility_assessment(result_review_packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result_intake = _load_result_intake_module()

    packet = dict(result_review_packet or result_intake.build_result_review_packet())
    blockers = list(packet.get("blockers", []))
    status_counts = dict(packet.get("status_counts", {}))

    if packet.get("promotion_decision_packet_ready") is True and not blockers:
        decision = "eligible_for_operator_promotion_review"
        packet_status = "promotion_review_ready"
    elif packet.get("review_status") == "blocked" or status_counts.get("failed", 0) or status_counts.get("blocked", 0):
        decision = "blocked_from_promotion"
        packet_status = "blocked"
        if "validation_result_blocked_or_failed" not in blockers:
            blockers.append("validation_result_blocked_or_failed")
    elif status_counts.get("not_provided", 0) or status_counts.get("inconclusive", 0):
        decision = "hold_for_more_validation_evidence"
        packet_status = "held"
        if "validation_results_incomplete" not in blockers:
            blockers.append("validation_results_incomplete")
    else:
        decision = "hold_for_more_validation_evidence"
        packet_status = "held"
        if "promotion_evidence_not_ready" not in blockers:
            blockers.append("promotion_evidence_not_ready")

    assessment = {
        "promotion_eligibility_id": _stable_id("promotion_eligibility", packet.get("result_review_packet_id"), decision),
        "version": VERSION,
        "created_at": _now(),
        "result_review_packet_id": packet.get("result_review_packet_id"),
        "readiness_assessment_id": packet.get("readiness_assessment_id"),
        "decision": decision,
        "packet_status": packet_status,
        "status_counts": status_counts,
        "blockers": sorted(set(blockers)),
        "eligible_for_operator_review": decision == "eligible_for_operator_promotion_review",
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "promotion_performed": False,
        "operator_review_required": True,
    }
    assessment.update(BLOCKED_AUTHORITY)
    return assessment


def build_s542_promotion_eligibility_contract() -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    result_intake = _load_result_intake_module()

    plan = validation_plan.build_controlled_validation_execution_plan()
    passed_intake = result_intake.intake_validation_results(plan, _all_passed_supplied_results(plan))
    passed_map = result_intake.build_result_evidence_map(passed_intake)
    passed_assessment = result_intake.assess_validation_result_readiness(passed_intake, passed_map)
    passed_packet = result_intake.build_result_review_packet(passed_intake, passed_map, passed_assessment)
    promotion_assessment = build_promotion_eligibility_assessment(passed_packet)

    return _safe_base(
        "S542",
        "promotion_eligibility_contract_ready",
        sample_assessment={
            "decision": promotion_assessment["decision"],
            "packet_status": promotion_assessment["packet_status"],
            "eligible_for_operator_review": promotion_assessment["eligible_for_operator_review"],
            "promotion_allowed_now": promotion_assessment["promotion_allowed_now"],
        },
        eligibility_rules=[
            "All passed supplied validation results can enter operator promotion review.",
            "Operator promotion review still cannot apply the update.",
            "Failed, blocked, missing, or inconclusive results block or hold promotion review.",
        ],
    )


def build_operator_approval_boundary(eligibility: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active = dict(eligibility or build_promotion_eligibility_assessment())
    approval_text = "I approve this staged update for a future governed application step after rollback proof and final checks."

    boundary = {
        "approval_boundary_id": _stable_id("promotion_approval_boundary", active.get("promotion_eligibility_id")),
        "version": VERSION,
        "created_at": _now(),
        "promotion_eligibility_id": active.get("promotion_eligibility_id"),
        "operator_approval_required": True,
        "operator_approval_received": False,
        "required_approval_text": approval_text,
        "approval_text_matched": False,
        "rollback_proof_required": True,
        "final_regression_required": True,
        "separate_application_authority_required": True,
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "promotion_performed": False,
    }
    boundary.update(BLOCKED_AUTHORITY)
    return boundary


def build_promotion_decision_packet(
    result_review_packet: Optional[Dict[str, Any]] = None,
    operator_note: str | None = None,
) -> Dict[str, Any]:
    result_intake = _load_result_intake_module()

    packet = dict(result_review_packet or result_intake.build_result_review_packet())
    eligibility = build_promotion_eligibility_assessment(packet)
    approval_boundary = build_operator_approval_boundary(eligibility)

    if eligibility["decision"] == "eligible_for_operator_promotion_review":
        summary = "Validation results can enter operator promotion review. Application remains blocked."
        required_before_apply = [
            "operator_approval_received",
            "rollback_proof_packet_passed",
            "final_regression_confirmed",
            "separate_application_authority_enabled",
        ]
    elif eligibility["decision"] == "blocked_from_promotion":
        summary = "Validation results block promotion review until failed or blocked checks are resolved."
        required_before_apply = [
            "resolve_failed_or_blocked_validation_results",
            "supply_clean_validation_evidence",
            "rebuild_promotion_decision_packet",
        ]
    else:
        summary = "More validation evidence is required before promotion review."
        required_before_apply = [
            "supply_missing_validation_results",
            "attach_result_evidence_refs",
            "reassess_validation_readiness",
        ]

    decision_packet = {
        "promotion_packet_id": _stable_id("promotion_decision_packet", packet.get("result_review_packet_id"), eligibility["decision"], operator_note or ""),
        "version": VERSION,
        "created_at": _now(),
        "decision": eligibility["decision"],
        "packet_status": eligibility["packet_status"],
        "result_review_packet_id": packet.get("result_review_packet_id"),
        "readiness_assessment_id": packet.get("readiness_assessment_id"),
        "evidence_summary": {
            "status_counts": packet.get("status_counts", {}),
            "promotion_decision_packet_ready": packet.get("promotion_decision_packet_ready", False),
            "review_status": packet.get("review_status"),
        },
        "blockers": eligibility["blockers"],
        "required_before_apply": required_before_apply,
        "operator_approval_boundary": approval_boundary,
        "operator_note": str(operator_note or ""),
        "summary": summary,
        "review_only": True,
        "promotion_allowed_now": False,
        "update_apply_allowed": False,
        "promotion_performed": False,
        "decision_persistent_write_allowed": False,
        "decision_persistent_write_performed": False,
    }
    decision_packet.update(BLOCKED_AUTHORITY)
    return decision_packet


def build_s543_promotion_decision_packet_contract() -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    result_intake = _load_result_intake_module()

    plan = validation_plan.build_controlled_validation_execution_plan()
    passed_intake = result_intake.intake_validation_results(plan, _all_passed_supplied_results(plan))
    passed_map = result_intake.build_result_evidence_map(passed_intake)
    passed_assessment = result_intake.assess_validation_result_readiness(passed_intake, passed_map)
    passed_review = result_intake.build_result_review_packet(passed_intake, passed_map, passed_assessment)
    packet = build_promotion_decision_packet(passed_review, operator_note="S543 sample promotion review packet.")

    return _safe_base(
        "S543",
        "promotion_decision_packet_contract_ready",
        sample_packet={
            "decision": packet["decision"],
            "packet_status": packet["packet_status"],
            "review_only": packet["review_only"],
            "promotion_allowed_now": packet["promotion_allowed_now"],
            "update_apply_allowed": packet["update_apply_allowed"],
        },
        packet_rules=[
            "Packet can mark eligibility for operator promotion review.",
            "Packet cannot promote or apply the update.",
            "Packet preserves blockers and required-before-apply gates.",
        ],
    )


def build_hold_or_rejection_packet(result_review_packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    packet = build_promotion_decision_packet(result_review_packet)
    decision = packet["decision"]

    if decision == "blocked_from_promotion":
        disposition = "reject_or_rework"
    elif decision == "hold_for_more_validation_evidence":
        disposition = "hold_for_more_evidence"
    else:
        disposition = "not_rejection_packet"

    rejection = {
        "hold_rejection_packet_id": _stable_id("hold_rejection_packet", packet.get("promotion_packet_id"), disposition),
        "version": VERSION,
        "created_at": _now(),
        "promotion_packet_id": packet.get("promotion_packet_id"),
        "disposition": disposition,
        "decision": decision,
        "blockers": packet.get("blockers", []),
        "required_next_steps": packet.get("required_before_apply", []),
        "can_apply_update": False,
        "can_promote_update": False,
        "operator_review_required": True,
    }
    rejection.update(BLOCKED_AUTHORITY)
    return rejection


def build_s544_hold_rejection_contract() -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    result_intake = _load_result_intake_module()

    plan = validation_plan.build_controlled_validation_execution_plan()
    failed_intake = result_intake.intake_validation_results(plan, _failed_supplied_results(plan))
    failed_map = result_intake.build_result_evidence_map(failed_intake)
    failed_assessment = result_intake.assess_validation_result_readiness(failed_intake, failed_map)
    failed_review = result_intake.build_result_review_packet(failed_intake, failed_map, failed_assessment)
    rejection = build_hold_or_rejection_packet(failed_review)

    return _safe_base(
        "S544",
        "hold_rejection_contract_ready",
        sample_rejection={
            "disposition": rejection["disposition"],
            "decision": rejection["decision"],
            "can_apply_update": rejection["can_apply_update"],
        },
        hold_rejection_rules=[
            "Failed validation results produce a rejection or rework packet.",
            "Missing validation results produce a hold packet.",
            "Hold/rejection packets do not execute decisions.",
        ],
    )


def build_s545_approval_boundary_contract() -> Dict[str, Any]:
    boundary = build_operator_approval_boundary()
    return _safe_base(
        "S545",
        "approval_boundary_contract_ready",
        approval_boundary=boundary,
        approval_rules=[
            "Operator approval is required but absent by default.",
            "Approval text must be explicit in a future phase.",
            "Approval alone is not enough; rollback proof and final regression remain required.",
            "This module cannot apply an update.",
        ],
    )


def build_s546_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S546",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "promotion_decision_packet_panel",
            "promotion_eligibility_card",
            "promotion_blockers_card",
            "approval_boundary_card",
            "hold_rejection_packet_card",
        ],
        visual_authority="presentation_only",
    )


def build_s547_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    result_intake = _load_result_intake_module()

    plan = validation_plan.build_controlled_validation_execution_plan()

    passed_intake = result_intake.intake_validation_results(plan, _all_passed_supplied_results(plan))
    passed_map = result_intake.build_result_evidence_map(passed_intake)
    passed_assessment = result_intake.assess_validation_result_readiness(passed_intake, passed_map)
    passed_review = result_intake.build_result_review_packet(passed_intake, passed_map, passed_assessment)
    passed_promotion = build_promotion_decision_packet(passed_review)

    failed_intake = result_intake.intake_validation_results(plan, _failed_supplied_results(plan))
    failed_map = result_intake.build_result_evidence_map(failed_intake)
    failed_assessment = result_intake.assess_validation_result_readiness(failed_intake, failed_map)
    failed_review = result_intake.build_result_review_packet(failed_intake, failed_map, failed_assessment)
    failed_promotion = build_promotion_decision_packet(failed_review)
    failed_rejection = build_hold_or_rejection_packet(failed_review)

    empty_review = result_intake.build_result_review_packet()
    hold_promotion = build_promotion_decision_packet(empty_review)

    s541 = build_s541_promotion_decision_schema()
    s542 = build_s542_promotion_eligibility_contract()
    s543 = build_s543_promotion_decision_packet_contract()
    s544 = build_s544_hold_rejection_contract()
    s545 = build_s545_approval_boundary_contract()
    s546 = build_s546_cockpit_asset_manifest(project_root)

    checks = {
        "s541_schema_ready": "eligible_for_operator_promotion_review" in s541["promotion_decisions"],
        "s542_eligibility_ready": s542["sample_assessment"]["eligible_for_operator_review"] is True,
        "s543_packet_ready": s543["sample_packet"]["promotion_allowed_now"] is False and s543["sample_packet"]["update_apply_allowed"] is False,
        "s544_rejection_ready": s544["sample_rejection"]["can_apply_update"] is False,
        "s545_approval_boundary_ready": s545["approval_boundary"]["operator_approval_received"] is False,
        "s546_assets_exist": s546["assets"]["js_exists"] is True and s546["assets"]["css_exists"] is True,
        "passed_packet_enters_review_only": passed_promotion["decision"] == "eligible_for_operator_promotion_review" and passed_promotion["review_only"] is True,
        "passed_packet_does_not_apply": passed_promotion["promotion_allowed_now"] is False and passed_promotion["update_apply_allowed"] is False,
        "failed_packet_blocks": failed_promotion["decision"] == "blocked_from_promotion" and failed_rejection["disposition"] == "reject_or_rework",
        "hold_packet_holds": hold_promotion["decision"] == "hold_for_more_validation_evidence",
        "no_persistence_or_promotion": all(
            value is False
            for value in [
                passed_promotion["decision_persistent_write_performed"],
                passed_promotion["promotion_performed"],
                failed_promotion["promotion_performed"],
                hold_promotion["promotion_performed"],
            ]
        ),
        "all_authority_blocked": all(passed_promotion.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S547",
        "claire_update_promotion_decision_packet_passed" if ok else "claire_update_promotion_decision_packet_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "passed_promotion": passed_promotion,
            "failed_promotion": failed_promotion,
            "failed_rejection": failed_rejection,
            "hold_promotion": hold_promotion,
        },
        forward_motion_allowed=ok,
        stop_point="STOP POINT B - validation results and promotion decision packets exist; still no application.",
        next_phase="S548-S554 Rollback proof packet and recovery gate",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s547_claire_update_promotion_decision_packet_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_update_promotion_decision_packet_s541_s547(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S541-S547",
        "claire_update_promotion_decision_packet_ready",
        contracts={
            "s541": build_s541_promotion_decision_schema(),
            "s542": build_s542_promotion_eligibility_contract(),
            "s543": build_s543_promotion_decision_packet_contract(),
            "s544": build_s544_hold_rejection_contract(),
            "s545": build_s545_approval_boundary_contract(),
            "s546": build_s546_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s547_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "PROMOTION_DECISIONS",
    "PROMOTION_PACKET_STATUSES",
    "build_s541_promotion_decision_schema",
    "build_promotion_eligibility_assessment",
    "build_s542_promotion_eligibility_contract",
    "build_operator_approval_boundary",
    "build_promotion_decision_packet",
    "build_s543_promotion_decision_packet_contract",
    "build_hold_or_rejection_packet",
    "build_s544_hold_rejection_contract",
    "build_s545_approval_boundary_contract",
    "build_s546_cockpit_asset_manifest",
    "build_s547_stop_gate",
    "build_claire_update_promotion_decision_packet_s541_s547",
]
