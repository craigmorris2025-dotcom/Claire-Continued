from __future__ import annotations

"""
Claire End-to-End Governed Update Readiness Demo — S569-S575

This is the final build for the current governed-update readiness session.

It proves the complete review-only update runway from inspection through cockpit
payload without removing the web/update blocks.

It builds on:
- S506-S512 Governed Update Inspector
- S513-S519 Staged Update Sandbox Contract
- S520-S526 Controlled Validation Plan
- S527-S533 Update Evidence Review Queue
- S534-S540 Validation Result Intake
- S541-S547 Promotion Decision Packet
- S548-S554 Rollback Recovery Gate
- S555-S561 Operator Staged Update Handoff
- S562-S568 Dashboard Update-Control Cockpit Wiring

Purpose:
- build a single end-to-end readiness demo packet
- prove the stage chain is importable and internally coherent
- show passed-validation path still cannot apply updates
- show blocked path remains visible
- produce the final S575 stop gate for this build session
- hand off to the next planned phase: web/source/search issues

No update is applied, no package is installed, no package is downloaded, no
command is executed, no test is executed by Claire, no backup is created, no
restore is performed, no promotion occurs, no live web request is made, no
persistent demo store is written, and no runtime truth is mutated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


VERSION = "v19.89.8-S569-S575"
PHASE = "S569-S575"
JS_ASSET = "frontend/cockpit/shell/assets/claire_governed_update_readiness_demo.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_governed_update_readiness_demo.css"


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
    "cockpit_action_execution_performed": False,
    "cockpit_persistent_write_performed": False,
    "readiness_demo_persistent_write_performed": False,
}


DEMO_CHAIN_STAGES = [
    "S506-S512",
    "S513-S519",
    "S520-S526",
    "S527-S533",
    "S534-S540",
    "S541-S547",
    "S548-S554",
    "S555-S561",
    "S562-S568",
    "S569-S575",
]


NEXT_PHASE_AFTER_S575 = [
    "governed_source_registry",
    "source_trust_tiers",
    "need_diagnosis_engine",
    "search_plan_builder",
    "governed_web_search_evidence_only",
    "metadata_only_update_candidate_discovery",
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


def _load_modules() -> Dict[str, Any]:
    from runtime_core.api import governed_update_inspector_s506_s512 as inspector
    from runtime_core.api import staged_update_sandbox_contract_s513_s519 as sandbox
    from runtime_core.api import controlled_update_validation_plan_s520_s526 as validation_plan
    from runtime_core.api import update_evidence_review_queue_s527_s533 as review_queue
    from runtime_core.api import validation_result_intake_s534_s540 as result_intake
    from runtime_core.api import update_promotion_decision_packet_s541_s547 as promotion
    from runtime_core.api import rollback_recovery_gate_s548_s554 as rollback
    from runtime_core.api import operator_staged_update_handoff_s555_s561 as handoff
    from runtime_core.api import update_control_cockpit_wiring_s562_s568 as cockpit

    return {
        "inspector": inspector,
        "sandbox": sandbox,
        "validation_plan": validation_plan,
        "review_queue": review_queue,
        "result_intake": result_intake,
        "promotion": promotion,
        "rollback": rollback,
        "handoff": handoff,
        "cockpit": cockpit,
    }


def build_s569_readiness_demo_schema() -> Dict[str, Any]:
    return _safe_base(
        "S569",
        "governed_update_readiness_demo_schema_ready",
        demo_chain_stages=DEMO_CHAIN_STAGES,
        next_phase_after_s575=NEXT_PHASE_AFTER_S575,
        demo_packet_fields=[
            "readiness_demo_id",
            "inspection",
            "sandbox_profile",
            "validation_plan",
            "review_queue",
            "validation_result_intake",
            "promotion_packet",
            "rollback_packet",
            "handoff_packet",
            "cockpit_payload",
            "blocked_authority_audit",
            "final_status",
        ],
        demo_rules=[
            "Demo proves readiness only.",
            "Demo does not enable live web, download, install, apply, execute, or mutate.",
            "Blocked paths must remain visible.",
            "S575 hands off to web/source/search issues after this build session.",
        ],
    )


def build_passed_validation_results(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    commands = list(plan.get("command_manifest", {}).get("commands", []))
    return [
        {
            "command_id": command.get("command_id"),
            "status": "passed",
            "summary": f"Operator supplied pass result for {command.get('command_id')} in readiness demo.",
            "evidence_refs": [f"s575_demo_evidence_{command.get('command_id')}"],
            "blockers": [],
        }
        for command in commands
    ]


def build_blocked_validation_results(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = build_passed_validation_results(plan)
    if results:
        results[0] = {
            "command_id": results[0]["command_id"],
            "status": "failed",
            "summary": "S575 demo failure path remains blocked and visible.",
            "evidence_refs": ["s575_demo_failure_log"],
            "blockers": ["s575_demo_failed_validation"],
        }
    return results


def build_s570_demo_chain_packet(project_root: str | Path | None = None) -> Dict[str, Any]:
    modules = _load_modules()

    inspection = modules["inspector"].inspect_update_package_candidate()
    sandbox_profile = modules["sandbox"].build_validation_sandbox_profile(inspection)
    validation_plan = modules["validation_plan"].build_controlled_validation_execution_plan(inspection)

    evidence_bundle = modules["review_queue"].capture_update_evidence_bundle(
        inspection=inspection,
        execution_plan=validation_plan,
    )
    review_packet = modules["review_queue"].build_operator_review_packet(evidence_bundle)
    review_queue = modules["review_queue"].build_operator_review_queue([review_packet])

    passed_results = build_passed_validation_results(validation_plan)
    result_intake = modules["result_intake"].intake_validation_results(validation_plan, passed_results)
    result_evidence_map = modules["result_intake"].build_result_evidence_map(result_intake)
    result_assessment = modules["result_intake"].assess_validation_result_readiness(result_intake, result_evidence_map)
    result_review_packet = modules["result_intake"].build_result_review_packet(
        result_intake,
        result_evidence_map,
        result_assessment,
    )

    promotion_packet = modules["promotion"].build_promotion_decision_packet(
        result_review_packet,
        operator_note="S575 demo promotion-review path.",
    )
    rollback_packet = modules["rollback"].build_rollback_proof_packet(promotion_packet)
    rollback_completeness = modules["rollback"].assess_rollback_proof_completeness(rollback_packet)
    recovery_gate = modules["rollback"].build_recovery_gate(rollback_packet, rollback_completeness)

    handoff_packet = modules["handoff"].build_operator_staged_update_handoff_packet(
        promotion_packet,
        operator_approval_text=modules["handoff"].REQUIRED_APPROVAL_TEXT,
        operator_note="S575 demo handoff path remains review-only.",
    )
    application_boundary = modules["handoff"].build_application_owner_boundary(handoff_packet)
    pre_application_blockers = modules["handoff"].build_final_pre_application_blocker_packet(handoff_packet)
    cockpit_payload = modules["cockpit"].build_update_control_cockpit_payload(project_root)

    packet = {
        "readiness_demo_id": _stable_id("governed_update_readiness_demo", validation_plan.get("execution_plan_id"), promotion_packet.get("promotion_packet_id")),
        "version": VERSION,
        "created_at": _now(),
        "scenario": "passed_validation_but_no_apply_authority",
        "inspection": inspection,
        "sandbox_profile": sandbox_profile,
        "validation_plan": validation_plan,
        "evidence_bundle": evidence_bundle,
        "review_packet": review_packet,
        "review_queue": review_queue,
        "validation_result_intake": result_intake,
        "result_review_packet": result_review_packet,
        "promotion_packet": promotion_packet,
        "rollback_packet": rollback_packet,
        "rollback_completeness": rollback_completeness,
        "recovery_gate": recovery_gate,
        "handoff_packet": handoff_packet,
        "application_boundary": application_boundary,
        "pre_application_blockers": pre_application_blockers,
        "cockpit_payload": cockpit_payload,
        "final_status": "readiness_demo_complete_review_only",
        "can_move_to_web_issues_after_s575": True,
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s571_blocked_path_demo_packet(project_root: str | Path | None = None) -> Dict[str, Any]:
    modules = _load_modules()

    inspection = modules["inspector"].inspect_update_package_candidate(
        modules["inspector"].build_sample_update_candidate(
            package_id="s575_blocked_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            download_allowed=True,
            apply_allowed=True,
        )
    )
    validation_plan = modules["validation_plan"].build_controlled_validation_execution_plan(inspection)

    blocked_results = build_blocked_validation_results(validation_plan)
    result_intake = modules["result_intake"].intake_validation_results(validation_plan, blocked_results)
    result_evidence_map = modules["result_intake"].build_result_evidence_map(result_intake)
    result_assessment = modules["result_intake"].assess_validation_result_readiness(result_intake, result_evidence_map)
    result_review_packet = modules["result_intake"].build_result_review_packet(result_intake, result_evidence_map, result_assessment)

    promotion_packet = modules["promotion"].build_promotion_decision_packet(result_review_packet)
    rejection_packet = modules["promotion"].build_hold_or_rejection_packet(result_review_packet)
    rollback_packet = modules["rollback"].build_rollback_proof_packet(promotion_packet)
    recovery_gate = modules["rollback"].build_recovery_gate(rollback_packet)
    cockpit_payload = modules["cockpit"].build_update_control_cockpit_payload(project_root)

    packet = {
        "blocked_demo_id": _stable_id("governed_update_blocked_demo", validation_plan.get("execution_plan_id"), promotion_packet.get("promotion_packet_id")),
        "version": VERSION,
        "created_at": _now(),
        "scenario": "blocked_candidate_remains_visible",
        "inspection": inspection,
        "validation_plan": validation_plan,
        "validation_result_intake": result_intake,
        "result_review_packet": result_review_packet,
        "promotion_packet": promotion_packet,
        "rejection_packet": rejection_packet,
        "rollback_packet": rollback_packet,
        "recovery_gate": recovery_gate,
        "cockpit_payload": cockpit_payload,
        "final_status": "blocked_path_visible_review_only",
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s572_demo_summary_payload(project_root: str | Path | None = None) -> Dict[str, Any]:
    demo = build_s570_demo_chain_packet(project_root)
    blocked = build_s571_blocked_path_demo_packet(project_root)

    payload = {
        "demo_summary_id": _stable_id("s575_demo_summary", demo.get("readiness_demo_id"), blocked.get("blocked_demo_id")),
        "version": VERSION,
        "created_at": _now(),
        "title": "S575 Governed Update Readiness Demo",
        "primary_status": "complete_review_only",
        "passed_path": {
            "inspection_risk": demo["inspection"].get("risk_level"),
            "validation_state": demo["validation_result_intake"].get("result_readiness_state"),
            "promotion_decision": demo["promotion_packet"].get("decision"),
            "rollback_gate": demo["recovery_gate"].get("gate_state"),
            "handoff_status": demo["handoff_packet"].get("packet_status"),
            "apply_allowed": demo["update_apply_allowed"],
        },
        "blocked_path": {
            "inspection_risk": blocked["inspection"].get("risk_level"),
            "validation_state": blocked["validation_result_intake"].get("result_readiness_state"),
            "promotion_decision": blocked["promotion_packet"].get("decision"),
            "rejection_disposition": blocked["rejection_packet"].get("disposition"),
            "apply_allowed": blocked["update_apply_allowed"],
        },
        "operator_message": "Governed update readiness runway is complete through S575. Next build session should move to web/source/search issues.",
        "next_phase_after_s575": NEXT_PHASE_AFTER_S575,
    }
    payload.update(BLOCKED_AUTHORITY)
    return payload


def build_s573_final_blocked_authority_audit(project_root: str | Path | None = None) -> Dict[str, Any]:
    modules = _load_modules()
    cockpit_matrix = modules["cockpit"].build_blocked_authority_matrix()
    summary_payload = build_s572_demo_summary_payload(project_root)

    authority_sources = {
        "s575": dict(BLOCKED_AUTHORITY),
        "cockpit_matrix_all_blocked": cockpit_matrix.get("all_blocked") is True,
        "summary_payload_all_blocked": all(summary_payload.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }
    unexpected_enabled = [
        flag for flag, value in BLOCKED_AUTHORITY.items()
        if value is not False or summary_payload.get(flag) is not False
    ]

    audit = {
        "final_blocked_authority_audit_id": _stable_id("s575_blocked_authority_audit", unexpected_enabled),
        "version": VERSION,
        "created_at": _now(),
        "authority_sources": authority_sources,
        "blocked_authority_count": len(BLOCKED_AUTHORITY),
        "unexpected_enabled": unexpected_enabled,
        "all_update_and_web_blocks_preserved": not unexpected_enabled and cockpit_matrix.get("all_blocked") is True,
        "blocks_to_revisit_after_s575": [
            "governed internet search evidence-only",
            "source registry and trust tiers",
            "metadata-only update candidate discovery",
        ],
    }
    audit.update(BLOCKED_AUTHORITY)
    return audit


def build_s574_web_phase_handoff_contract() -> Dict[str, Any]:
    return _safe_base(
        "S574",
        "web_phase_handoff_contract_ready",
        next_session_focus="web_source_search_issues",
        do_not_change_s575_plan=True,
        next_phase_after_s575=NEXT_PHASE_AFTER_S575,
        first_blocks_to_consider_lifting=[
            {
                "block": "governed_source_search",
                "planned_change": "allow evidence-only source discovery after source registry and trust tiers exist",
                "still_blocked": [
                    "runtime_mutation",
                    "automatic_updates",
                    "package_install",
                    "package_download_until_manifest_gate",
                    "live_web_execution_outside_governed_adapter",
                ],
            }
        ],
        handoff_rules=[
            "S575 ends the current governed update readiness session.",
            "After S575, move to web/source/search issues.",
            "Do not remove update application blocks as part of S575.",
            "The first internet change should be evidence-only governed source discovery.",
        ],
    )


def build_s575_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s569 = build_s569_readiness_demo_schema()
    demo = build_s570_demo_chain_packet(project_root)
    blocked = build_s571_blocked_path_demo_packet(project_root)
    summary = build_s572_demo_summary_payload(project_root)
    audit = build_s573_final_blocked_authority_audit(project_root)
    handoff = build_s574_web_phase_handoff_contract()

    checks = {
        "s569_schema_ready": s569["demo_chain_stages"] == DEMO_CHAIN_STAGES,
        "s570_passed_path_complete": demo["final_status"] == "readiness_demo_complete_review_only",
        "s570_passed_path_can_enter_promotion_review": demo["promotion_packet"]["decision"] == "eligible_for_operator_promotion_review",
        "s570_passed_path_still_cannot_apply": demo["promotion_packet"]["update_apply_allowed"] is False and demo["pre_application_blockers"]["safe_to_apply"] is False,
        "s571_blocked_path_visible": blocked["final_status"] == "blocked_path_visible_review_only" and blocked["promotion_packet"]["decision"] == "blocked_from_promotion",
        "s572_summary_ready": summary["primary_status"] == "complete_review_only",
        "s573_all_blocks_preserved": audit["all_update_and_web_blocks_preserved"] is True,
        "s574_web_handoff_ready": handoff["next_session_focus"] == "web_source_search_issues",
        "no_live_web": demo["network_request_performed"] is False and blocked["network_request_performed"] is False,
        "no_install_or_apply": all(
            value is False
            for value in [
                demo["package_install_performed"],
                demo["update_apply_allowed"],
                demo["promotion_performed"],
                blocked["package_install_performed"],
                blocked["update_apply_allowed"],
                blocked["promotion_performed"],
            ]
        ),
        "no_runtime_mutation": demo["runtime_mutation_enabled"] is False and demo["runtime_truth_mutation_allowed"] is False,
        "ready_to_move_to_web_issues": demo["can_move_to_web_issues_after_s575"] is True,
        "all_authority_blocked": all(demo.get(flag) is False and summary.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S575",
        "claire_governed_update_readiness_demo_passed" if ok else "claire_governed_update_readiness_demo_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "readiness_demo": demo,
            "blocked_demo": blocked,
            "summary": summary,
            "blocked_authority_audit": audit,
            "web_phase_handoff": handoff,
        },
        forward_motion_allowed=ok,
        stop_point="STOP POINT D - end-to-end governed update readiness demo complete; move next to web/source/search issues.",
        next_phase="Web/source/search issues: governed source registry, trust tiers, need diagnosis, and evidence-only search.",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s575_claire_governed_update_readiness_demo_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_governed_update_readiness_demo_s569_s575(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S569-S575",
        "claire_governed_update_readiness_demo_ready",
        contracts={
            "s569": build_s569_readiness_demo_schema(),
            "s570": _safe_base("S570", "passed_path_demo_chain_ready"),
            "s571": _safe_base("S571", "blocked_path_demo_chain_ready"),
            "s572": _safe_base("S572", "demo_summary_payload_ready"),
            "s573": _safe_base("S573", "final_blocked_authority_audit_ready"),
            "s574": build_s574_web_phase_handoff_contract(),
        },
        stop_gate=build_s575_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "DEMO_CHAIN_STAGES",
    "NEXT_PHASE_AFTER_S575",
    "build_s569_readiness_demo_schema",
    "build_passed_validation_results",
    "build_blocked_validation_results",
    "build_s570_demo_chain_packet",
    "build_s571_blocked_path_demo_packet",
    "build_s572_demo_summary_payload",
    "build_s573_final_blocked_authority_audit",
    "build_s574_web_phase_handoff_contract",
    "build_s575_stop_gate",
    "build_governed_update_readiness_demo_s569_s575",
]
