from __future__ import annotations

"""
Claire Rollback Proof Packet and Recovery Gate — S548-S554

This module defines the rollback proof packet and recovery gate that must sit
between promotion decision review and any future operator-approved staged update
handoff.

It builds on:
- S541-S547 Update Promotion Decision Packet

Purpose:
- define rollback proof packet shape
- map target paths to declarative backup / restore requirements
- assess rollback proof completeness
- build recovery gate and recovery validation packet
- block any update application unless rollback proof is complete in a future
  governed phase
- preserve application, install, mutation, promotion, automatic update, and
  recovery execution blocks

No backups are created, no files are restored, no update is applied, no package
is installed, no validation command is executed, no recovery action is executed,
no persistent proof store is written, and no runtime truth is mutated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S548-S554"
PHASE = "S548-S554"
JS_ASSET = "frontend/cockpit/shell/assets/claire_rollback_recovery_gate.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_rollback_recovery_gate.css"


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
    "rollback_proof_persistent_write_performed": False,
}


ROLLBACK_PROOF_STATUSES = [
    "not_proven",
    "declared_only",
    "missing_required_fields",
    "blocked",
    "proof_packet_ready_for_operator_review",
]


RECOVERY_GATE_STATES = [
    "blocked_missing_rollback_proof",
    "blocked_failed_validation",
    "awaiting_operator_review",
    "recovery_gate_reference_ready",
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


def _load_promotion_module():
    from runtime_core.api import update_promotion_decision_packet_s541_s547 as promotion

    return promotion


def _load_validation_plan_module():
    from runtime_core.api import controlled_update_validation_plan_s520_s526 as validation_plan

    return validation_plan


def build_s548_rollback_proof_schema() -> Dict[str, Any]:
    return _safe_base(
        "S548",
        "rollback_proof_schema_ready",
        rollback_proof_statuses=ROLLBACK_PROOF_STATUSES,
        recovery_gate_states=RECOVERY_GATE_STATES,
        rollback_packet_fields=[
            "rollback_packet_id",
            "promotion_packet_id",
            "target_file_backup_map",
            "restore_instruction_map",
            "post_restore_validation_plan",
            "operator_acknowledgment",
            "proof_status",
            "blockers",
            "rollback_proven",
            "backup_created",
            "restore_performed",
            "update_apply_allowed",
        ],
        proof_rules=[
            "Rollback proof packet is review-only.",
            "Declared rollback is not the same as proven rollback.",
            "No backup, restore, install, update apply, or recovery execution occurs here.",
            "Recovery gate must block unless rollback proof is complete in a future governed phase.",
        ],
    )


def build_target_file_backup_map(
    promotion_packet: Optional[Dict[str, Any]] = None,
    target_paths: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    active_packet = dict(promotion_packet or _load_promotion_module().build_promotion_decision_packet())
    active_paths = list(target_paths or [
        "claire/api/future_update_target.py",
        "tests/test_future_update_target.py",
    ])

    entries: List[Dict[str, Any]] = []
    for path in active_paths:
        normalized = str(path).replace("\\", "/")
        protected = normalized.startswith("claire/api/") or normalized.startswith("tests/") or normalized in {"main.py", "pyproject.toml"}
        entries.append(
            {
                "target_path": normalized,
                "backup_required": True,
                "backup_declared": False,
                "backup_created": False,
                "protected_path": protected,
                "restore_required": True,
                "post_restore_test_required": True,
            }
        )

    backup_map = {
        "backup_map_id": _stable_id("rollback_backup_map", active_packet.get("promotion_packet_id"), active_paths),
        "version": VERSION,
        "created_at": _now(),
        "promotion_packet_id": active_packet.get("promotion_packet_id"),
        "entries": entries,
        "target_path_count": len(entries),
        "protected_path_count": sum(1 for entry in entries if entry["protected_path"]),
        "all_backups_declared": all(entry["backup_declared"] for entry in entries) if entries else False,
        "all_backups_created": False,
        "backup_created": False,
    }
    backup_map.update(BLOCKED_AUTHORITY)
    return backup_map


def build_restore_instruction_map(backup_map: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_map = dict(backup_map or build_target_file_backup_map())
    entries = [
        {
            "target_path": entry["target_path"],
            "restore_instruction_declared": False,
            "restore_performed": False,
            "restore_validation_required": True,
            "manual_review_required": bool(entry.get("protected_path")),
        }
        for entry in active_map.get("entries", [])
    ]

    restore_map = {
        "restore_map_id": _stable_id("restore_instruction_map", active_map.get("backup_map_id")),
        "version": VERSION,
        "created_at": _now(),
        "backup_map_id": active_map.get("backup_map_id"),
        "entries": entries,
        "entry_count": len(entries),
        "all_restore_instructions_declared": all(entry["restore_instruction_declared"] for entry in entries) if entries else False,
        "restore_performed": False,
    }
    restore_map.update(BLOCKED_AUTHORITY)
    return restore_map


def build_s549_backup_restore_map_contract() -> Dict[str, Any]:
    backup_map = build_target_file_backup_map()
    restore_map = build_restore_instruction_map(backup_map)
    return _safe_base(
        "S549",
        "backup_restore_map_contract_ready",
        sample_backup_map={
            "target_path_count": backup_map["target_path_count"],
            "protected_path_count": backup_map["protected_path_count"],
            "all_backups_created": backup_map["all_backups_created"],
        },
        sample_restore_map={
            "entry_count": restore_map["entry_count"],
            "all_restore_instructions_declared": restore_map["all_restore_instructions_declared"],
            "restore_performed": restore_map["restore_performed"],
        },
        map_rules=[
            "Backup and restore maps are declarative only.",
            "No backup files are created.",
            "No restore action is performed.",
            "Protected paths require manual review and post-restore validation.",
        ],
    )


def build_rollback_proof_packet(
    promotion_packet: Optional[Dict[str, Any]] = None,
    target_paths: Optional[Sequence[str]] = None,
    operator_acknowledged: bool = False,
    proof_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    active_promotion = dict(promotion_packet or _load_promotion_module().build_promotion_decision_packet())
    backup_map = build_target_file_backup_map(active_promotion, target_paths=target_paths)
    restore_map = build_restore_instruction_map(backup_map)
    overrides = dict(proof_overrides or {})

    post_restore_validation_plan = {
        "post_restore_validation_plan_id": _stable_id("post_restore_validation", restore_map.get("restore_map_id")),
        "required": True,
        "declared": bool(overrides.get("post_restore_validation_declared", False)),
        "executed": False,
        "required_commands": [
            "python -X utf8 -m pytest --lf -q --tb=short",
            "python -X utf8 -m pytest -vv --tb=short",
        ],
    }

    blockers: List[str] = []
    if active_promotion.get("decision") != "eligible_for_operator_promotion_review":
        blockers.append("promotion_packet_not_eligible")
    if not backup_map["all_backups_declared"]:
        blockers.append("backup_map_not_declared")
    if not restore_map["all_restore_instructions_declared"]:
        blockers.append("restore_instructions_not_declared")
    if not post_restore_validation_plan["declared"]:
        blockers.append("post_restore_validation_not_declared")
    if operator_acknowledged is False:
        blockers.append("operator_rollback_acknowledgment_missing")
    if backup_map["all_backups_created"] is False:
        blockers.append("backups_not_created")
    if restore_map["restore_performed"] is False:
        blockers.append("restore_not_tested")

    if active_promotion.get("decision") == "eligible_for_operator_promotion_review" and not blockers:
        proof_status = "proof_packet_ready_for_operator_review"
    elif active_promotion.get("decision") == "blocked_from_promotion":
        proof_status = "blocked"
    elif blockers:
        proof_status = "declared_only"
    else:
        proof_status = "not_proven"

    packet = {
        "rollback_packet_id": _stable_id("rollback_proof_packet", active_promotion.get("promotion_packet_id"), proof_status),
        "version": VERSION,
        "created_at": _now(),
        "promotion_packet_id": active_promotion.get("promotion_packet_id"),
        "promotion_decision": active_promotion.get("decision"),
        "target_file_backup_map": backup_map,
        "restore_instruction_map": restore_map,
        "post_restore_validation_plan": post_restore_validation_plan,
        "operator_acknowledgment": {
            "required": True,
            "received": bool(operator_acknowledged),
            "required_text": "I acknowledge rollback requirements and recovery validation must pass before any future application.",
        },
        "proof_status": proof_status,
        "blockers": sorted(set(blockers)),
        "rollback_proven": False,
        "backup_created": False,
        "restore_performed": False,
        "recovery_execution_performed": False,
        "update_apply_allowed": False,
        "review_only": True,
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s550_rollback_proof_packet_contract() -> Dict[str, Any]:
    packet = build_rollback_proof_packet()
    return _safe_base(
        "S550",
        "rollback_proof_packet_contract_ready",
        sample_packet={
            "proof_status": packet["proof_status"],
            "blocker_count": len(packet["blockers"]),
            "rollback_proven": packet["rollback_proven"],
            "update_apply_allowed": packet["update_apply_allowed"],
        },
        packet_rules=[
            "Rollback packet can be built before proof is complete.",
            "Incomplete proof creates blockers.",
            "Packet cannot create backups, perform restore, or apply updates.",
        ],
    )


def assess_rollback_proof_completeness(rollback_packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    packet = dict(rollback_packet or build_rollback_proof_packet())
    blockers = list(packet.get("blockers", []))

    completeness_checks = {
        "promotion_packet_eligible": packet.get("promotion_decision") == "eligible_for_operator_promotion_review",
        "backup_map_declared": packet.get("target_file_backup_map", {}).get("all_backups_declared") is True,
        "backups_created": packet.get("backup_created") is True,
        "restore_instructions_declared": packet.get("restore_instruction_map", {}).get("all_restore_instructions_declared") is True,
        "post_restore_validation_declared": packet.get("post_restore_validation_plan", {}).get("declared") is True,
        "operator_acknowledged": packet.get("operator_acknowledgment", {}).get("received") is True,
        "restore_tested": packet.get("restore_performed") is True,
    }

    complete = all(completeness_checks.values())
    if not complete and not blockers:
        blockers.append("rollback_proof_incomplete")

    assessment = {
        "rollback_completeness_id": _stable_id("rollback_completeness", packet.get("rollback_packet_id"), complete),
        "version": VERSION,
        "created_at": _now(),
        "rollback_packet_id": packet.get("rollback_packet_id"),
        "completeness_checks": completeness_checks,
        "rollback_proof_complete": complete,
        "rollback_proven": False,
        "blockers": sorted(set(blockers)),
        "can_advance_to_application_gate": False,
        "update_apply_allowed": False,
    }
    assessment.update(BLOCKED_AUTHORITY)
    return assessment


def build_s551_rollback_completeness_contract() -> Dict[str, Any]:
    assessment = assess_rollback_proof_completeness()
    return _safe_base(
        "S551",
        "rollback_completeness_contract_ready",
        sample_assessment={
            "rollback_proof_complete": assessment["rollback_proof_complete"],
            "can_advance_to_application_gate": assessment["can_advance_to_application_gate"],
            "blocker_count": len(assessment["blockers"]),
        },
        completeness_rules=[
            "Rollback completeness is stricter than rollback declaration.",
            "This phase never marks rollback as proven by execution.",
            "Application gate remains blocked.",
        ],
    )


def build_recovery_gate(
    rollback_packet: Optional[Dict[str, Any]] = None,
    completeness: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    packet = dict(rollback_packet or build_rollback_proof_packet())
    active_completeness = dict(completeness or assess_rollback_proof_completeness(packet))

    blockers = list(active_completeness.get("blockers", []))
    if active_completeness.get("rollback_proof_complete") is not True:
        gate_state = "blocked_missing_rollback_proof"
    elif packet.get("promotion_decision") != "eligible_for_operator_promotion_review":
        gate_state = "blocked_failed_validation"
        blockers.append("promotion_not_eligible")
    else:
        gate_state = "awaiting_operator_review"

    gate = {
        "recovery_gate_id": _stable_id("recovery_gate", packet.get("rollback_packet_id"), gate_state),
        "version": VERSION,
        "created_at": _now(),
        "rollback_packet_id": packet.get("rollback_packet_id"),
        "rollback_completeness_id": active_completeness.get("rollback_completeness_id"),
        "gate_state": gate_state,
        "blockers": sorted(set(blockers)),
        "operator_review_required": True,
        "recovery_execution_allowed": False,
        "recovery_execution_performed": False,
        "update_apply_allowed": False,
        "promotion_allowed_now": False,
        "runtime_mutation_enabled": False,
    }
    gate.update(BLOCKED_AUTHORITY)
    return gate


def build_s552_recovery_gate_contract() -> Dict[str, Any]:
    gate = build_recovery_gate()
    return _safe_base(
        "S552",
        "recovery_gate_contract_ready",
        recovery_gate=gate,
        gate_rules=[
            "Recovery gate blocks until rollback proof is complete.",
            "Recovery gate cannot execute recovery.",
            "Recovery gate cannot apply updates.",
            "Runtime mutation remains blocked.",
        ],
    )


def build_s553_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S553",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "rollback_recovery_gate_panel",
            "backup_map_card",
            "restore_map_card",
            "rollback_proof_packet_card",
            "rollback_completeness_card",
            "recovery_gate_card",
        ],
        visual_authority="presentation_only",
    )


def build_s554_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    promotion = _load_promotion_module()
    validation_plan = _load_validation_plan_module()
    result_intake = __import__(
        "runtime_core.api.validation_result_intake_s534_s540",
        fromlist=["validation_result_intake_s534_s540"],
    )

    plan = validation_plan.build_controlled_validation_execution_plan()
    passed_results = [
        {
            "command_id": command.get("command_id"),
            "status": "passed",
            "summary": f"Operator supplied pass result for {command.get('command_id')}.",
            "evidence_refs": [f"operator_evidence_{command.get('command_id')}"],
        }
        for command in plan.get("command_manifest", {}).get("commands", [])
    ]
    passed_intake = result_intake.intake_validation_results(plan, passed_results)
    passed_map = result_intake.build_result_evidence_map(passed_intake)
    passed_assessment = result_intake.assess_validation_result_readiness(passed_intake, passed_map)
    passed_review = result_intake.build_result_review_packet(passed_intake, passed_map, passed_assessment)
    eligible_promotion = promotion.build_promotion_decision_packet(passed_review)

    rollback_packet = build_rollback_proof_packet(eligible_promotion)
    completeness = assess_rollback_proof_completeness(rollback_packet)
    recovery_gate = build_recovery_gate(rollback_packet, completeness)

    failed_review_packet = promotion.build_promotion_decision_packet()
    blocked_rollback_packet = build_rollback_proof_packet(failed_review_packet)
    blocked_gate = build_recovery_gate(blocked_rollback_packet)

    s548 = build_s548_rollback_proof_schema()
    s549 = build_s549_backup_restore_map_contract()
    s550 = build_s550_rollback_proof_packet_contract()
    s551 = build_s551_rollback_completeness_contract()
    s552 = build_s552_recovery_gate_contract()
    s553 = build_s553_cockpit_asset_manifest(project_root)

    checks = {
        "s548_schema_ready": "rollback_packet_id" in s548["rollback_packet_fields"],
        "s549_maps_ready": s549["sample_backup_map"]["all_backups_created"] is False and s549["sample_restore_map"]["restore_performed"] is False,
        "s550_packet_ready": s550["sample_packet"]["update_apply_allowed"] is False,
        "s551_completeness_blocks_application": s551["sample_assessment"]["can_advance_to_application_gate"] is False,
        "s552_recovery_gate_blocks": s552["recovery_gate"]["recovery_execution_allowed"] is False,
        "s553_assets_exist": s553["assets"]["js_exists"] is True and s553["assets"]["css_exists"] is True,
        "eligible_promotion_not_applied": eligible_promotion["decision"] == "eligible_for_operator_promotion_review" and eligible_promotion["update_apply_allowed"] is False,
        "rollback_packet_not_proven": rollback_packet["rollback_proven"] is False and bool(rollback_packet["blockers"]) is True,
        "recovery_gate_blocked": recovery_gate["gate_state"] == "blocked_missing_rollback_proof",
        "blocked_gate_blocks": blocked_gate["gate_state"] in {"blocked_missing_rollback_proof", "blocked_failed_validation"},
        "no_backup_restore_recovery": all(
            value is False
            for value in [
                rollback_packet["backup_created"],
                rollback_packet["restore_performed"],
                rollback_packet["recovery_execution_performed"],
                recovery_gate["recovery_execution_performed"],
                recovery_gate["update_apply_allowed"],
            ]
        ),
        "all_authority_blocked": all(recovery_gate.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S554",
        "claire_rollback_recovery_gate_passed" if ok else "claire_rollback_recovery_gate_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "eligible_promotion": eligible_promotion,
            "rollback_packet": rollback_packet,
            "completeness": completeness,
            "recovery_gate": recovery_gate,
            "blocked_rollback_packet": blocked_rollback_packet,
            "blocked_gate": blocked_gate,
        },
        forward_motion_allowed=ok,
        next_phase="S555-S561 Operator-approved staged update handoff",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s554_claire_rollback_recovery_gate_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_rollback_recovery_gate_s548_s554(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S548-S554",
        "claire_rollback_recovery_gate_ready",
        contracts={
            "s548": build_s548_rollback_proof_schema(),
            "s549": build_s549_backup_restore_map_contract(),
            "s550": build_s550_rollback_proof_packet_contract(),
            "s551": build_s551_rollback_completeness_contract(),
            "s552": build_s552_recovery_gate_contract(),
            "s553": build_s553_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s554_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "ROLLBACK_PROOF_STATUSES",
    "RECOVERY_GATE_STATES",
    "build_s548_rollback_proof_schema",
    "build_target_file_backup_map",
    "build_restore_instruction_map",
    "build_s549_backup_restore_map_contract",
    "build_rollback_proof_packet",
    "build_s550_rollback_proof_packet_contract",
    "assess_rollback_proof_completeness",
    "build_s551_rollback_completeness_contract",
    "build_recovery_gate",
    "build_s552_recovery_gate_contract",
    "build_s553_cockpit_asset_manifest",
    "build_s554_stop_gate",
    "build_rollback_recovery_gate_s548_s554",
]
