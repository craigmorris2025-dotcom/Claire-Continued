from __future__ import annotations

"""
Claire Controlled Update Validation Execution Plan — S520-S526

This module defines the governed plan for future operator-controlled update
validation execution. It does not execute validation.

It builds on:
- S506-S512 Governed Update Package Inspector
- S513-S519 Staged Update Validation Sandbox Contract

Purpose:
- define which validation actions could be executed later
- define command manifests without running commands
- define preflight gates for future controlled validation
- define rollback proof requirements
- define operator-controlled execution gate
- keep all execution, downloads, installs, promotion, mutation, and automatic
  updates blocked in this phase

No package is downloaded, no package is installed, no tests are executed,
no sandbox files are created, no validation command is run, no runtime truth is
mutated, no network request is made, and no automatic update authority is enabled.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S520-S526"
PHASE = "S520-S526"
JS_ASSET = "frontend/cockpit/shell/assets/claire_controlled_update_validation_plan.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_controlled_update_validation_plan.css"


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
    "quarantine_write_performed": False,
}


CONTROLLED_VALIDATION_PHASES = [
    "metadata_review",
    "sandbox_profile_review",
    "file_impact_review",
    "hash_signature_future_check",
    "rollback_future_check",
    "declared_targeted_tests_future_run",
    "full_regression_future_run",
    "operator_approval_gate",
]


EXECUTION_GATE_STATES = [
    "blocked",
    "awaiting_operator_review",
    "eligible_for_future_manual_execution",
    "executed_elsewhere_not_by_this_module",
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


def _load_update_inspector_module():
    from runtime_core.api import governed_update_inspector_s506_s512 as update_inspector

    return update_inspector


def _load_sandbox_module():
    from runtime_core.api import staged_update_sandbox_contract_s513_s519 as sandbox_contract

    return sandbox_contract


def build_s520_execution_authority_matrix_contract() -> Dict[str, Any]:
    return _safe_base(
        "S520",
        "controlled_validation_authority_matrix_ready",
        allowed_now=[
            "build_validation_plan",
            "build_command_manifest",
            "evaluate_preflight_metadata",
            "show_operator_gate",
            "show_rollback_requirements",
            "render_cockpit_plan",
        ],
        blocked_now=[
            "download_update_package",
            "install_update_package",
            "create_sandbox_files",
            "run_validation_commands",
            "run_tests",
            "promote_update",
            "mutate_runtime_truth",
            "apply_automatic_update",
        ],
        authority_rule="This phase plans controlled validation; it does not execute controlled validation.",
    )


def build_validation_command_manifest(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build declared validation command manifest without running any command."""
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    candidate = active_inspection.get("candidate", {})
    declared_tests = list(candidate.get("tests_declared", []) or [])

    command_items: List[Dict[str, Any]] = [
        {
            "command_id": "metadata_review",
            "label": "Review metadata inspection report",
            "command_text": "review generated inspection report",
            "execution_allowed_now": False,
            "execution_performed": False,
            "requires_operator_action": True,
        },
        {
            "command_id": "hash_signature_future_check",
            "label": "Future hash and signature verification",
            "command_text": "verify declared hash and signature in governed sandbox",
            "execution_allowed_now": False,
            "execution_performed": False,
            "requires_operator_action": True,
        },
        {
            "command_id": "rollback_future_check",
            "label": "Future rollback proof validation",
            "command_text": "validate rollback map before any active application",
            "execution_allowed_now": False,
            "execution_performed": False,
            "requires_operator_action": True,
        },
    ]

    for index, declared in enumerate(declared_tests, start=1):
        command_items.append(
            {
                "command_id": f"declared_test_{index}",
                "label": f"Declared targeted test {index}",
                "command_text": str(declared),
                "execution_allowed_now": False,
                "execution_performed": False,
                "requires_operator_action": True,
            }
        )

    command_items.append(
        {
            "command_id": "full_regression_future_check",
            "label": "Future full regression gate",
            "command_text": "python -X utf8 -m pytest -vv --tb=short",
            "execution_allowed_now": False,
            "execution_performed": False,
            "requires_operator_action": True,
        }
    )

    manifest = {
        "command_manifest_id": f"validation_command_manifest_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "command_count": len(command_items),
        "commands": command_items,
        "execution_allowed_now": False,
        "execution_performed": False,
        "operator_review_required": True,
    }
    manifest.update(BLOCKED_AUTHORITY)
    return manifest


def build_s521_validation_command_manifest_contract() -> Dict[str, Any]:
    manifest = build_validation_command_manifest()
    return _safe_base(
        "S521",
        "validation_command_manifest_contract_ready",
        manifest_fields=[
            "command_manifest_id",
            "inspection_id",
            "command_count",
            "commands",
            "execution_allowed_now",
            "execution_performed",
            "operator_review_required",
        ],
        sample_manifest={
            "command_count": manifest["command_count"],
            "execution_allowed_now": manifest["execution_allowed_now"],
            "execution_performed": manifest["execution_performed"],
        },
        command_rules=[
            "Commands are declarative only.",
            "No validation command is run here.",
            "Operator-controlled execution requires a later execution owner.",
        ],
    )


def build_controlled_validation_execution_plan(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build the future controlled validation plan without executing it."""
    inspector = _load_update_inspector_module()
    sandbox = _load_sandbox_module()

    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    sandbox_profile = sandbox.build_validation_sandbox_profile(active_inspection)
    impact_map = sandbox.build_staged_file_impact_map(active_inspection)
    dry_run_plan = sandbox.build_dry_run_validation_steps(active_inspection, impact_map)
    command_manifest = build_validation_command_manifest(active_inspection)

    blockers: List[str] = []
    if active_inspection.get("risk_level") == "blocked":
        blockers.append("inspection_blocked")
    if sandbox_profile.get("sandbox_status") in {"blocked_missing_validation_inputs", "blocked_protected_path_review"}:
        blockers.append(sandbox_profile.get("sandbox_status"))
    if impact_map.get("impact_level") == "blocked":
        blockers.append("file_impact_blocked")
    if not active_inspection.get("rollback_plan_present"):
        blockers.append("rollback_plan_missing")
    if not active_inspection.get("signature_present"):
        blockers.append("signature_missing")
    if not active_inspection.get("hash_present"):
        blockers.append("hash_missing")

    gate_state = "blocked" if blockers else "awaiting_operator_review"

    plan = {
        "execution_plan_id": f"controlled_validation_plan_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "sandbox_profile": sandbox_profile,
        "impact_map": impact_map,
        "dry_run_plan": dry_run_plan,
        "command_manifest": command_manifest,
        "phases": CONTROLLED_VALIDATION_PHASES,
        "gate_state": gate_state,
        "blockers": blockers,
        "execution_allowed_now": False,
        "validation_execution_performed": False,
        "test_execution_performed": False,
        "promotion_allowed": False,
        "operator_review_required": True,
    }
    plan.update(BLOCKED_AUTHORITY)
    return plan


def build_s522_controlled_validation_plan_contract() -> Dict[str, Any]:
    plan = build_controlled_validation_execution_plan()
    return _safe_base(
        "S522",
        "controlled_validation_plan_contract_ready",
        controlled_validation_phases=CONTROLLED_VALIDATION_PHASES,
        execution_gate_states=EXECUTION_GATE_STATES,
        sample_plan={
            "gate_state": plan["gate_state"],
            "phase_count": len(plan["phases"]),
            "execution_allowed_now": plan["execution_allowed_now"],
        },
    )


def build_validation_preflight_decision(plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Evaluate whether a plan is eligible for a future manual execution owner."""
    active_plan = dict(plan or build_controlled_validation_execution_plan())
    sandbox_profile = active_plan.get("sandbox_profile", {})
    command_manifest = active_plan.get("command_manifest", {})

    blockers = list(active_plan.get("blockers", []))
    if active_plan.get("execution_allowed_now") is not False:
        blockers.append("unexpected_execution_authority")
    if command_manifest.get("execution_performed") is not False:
        blockers.append("unexpected_command_execution")
    if sandbox_profile.get("sandbox_created") is not False:
        blockers.append("unexpected_sandbox_creation")

    eligible_for_future_manual_execution = not blockers and active_plan.get("gate_state") == "awaiting_operator_review"

    preflight = {
        "preflight_id": f"validation_preflight_{abs(hash(active_plan.get('execution_plan_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "execution_plan_id": active_plan.get("execution_plan_id"),
        "eligible_for_future_manual_execution": eligible_for_future_manual_execution,
        "execution_allowed_now": False,
        "operator_approval_required": True,
        "blockers": blockers,
        "decision": (
            "eligible_for_future_manual_execution_owner"
            if eligible_for_future_manual_execution
            else "not_ready_for_execution_owner"
        ),
    }
    preflight.update(BLOCKED_AUTHORITY)
    return preflight


def build_s523_preflight_gate_contract() -> Dict[str, Any]:
    plan = build_controlled_validation_execution_plan()
    preflight = build_validation_preflight_decision(plan)
    return _safe_base(
        "S523",
        "validation_preflight_gate_contract_ready",
        sample_preflight={
            "eligible_for_future_manual_execution": preflight["eligible_for_future_manual_execution"],
            "execution_allowed_now": preflight["execution_allowed_now"],
            "decision": preflight["decision"],
        },
        preflight_rules=[
            "Preflight can make a future eligibility decision only.",
            "Preflight cannot execute validation.",
            "Operator approval remains required.",
            "Blocked authority flags must remain false.",
        ],
    )


def build_rollback_proof_checklist(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    candidate = active_inspection.get("candidate", {})
    target_paths = list(candidate.get("target_paths", []) or [])

    checklist_items = [
        {
            "check_id": "rollback_plan_declared",
            "label": "Rollback plan declared",
            "required": True,
            "declared": bool(active_inspection.get("rollback_plan_present") is True),
            "validated": False,
        },
        {
            "check_id": "target_file_backup_map",
            "label": "Target file backup map",
            "required": True,
            "declared": bool(target_paths),
            "validated": False,
        },
        {
            "check_id": "restore_instruction_map",
            "label": "Restore instruction map",
            "required": True,
            "declared": False,
            "validated": False,
        },
        {
            "check_id": "post_rollback_test_plan",
            "label": "Post-rollback test plan",
            "required": True,
            "declared": bool(candidate.get("tests_declared")),
            "validated": False,
        },
        {
            "check_id": "operator_rollback_acknowledgment",
            "label": "Operator rollback acknowledgment",
            "required": True,
            "declared": False,
            "validated": False,
        },
    ]

    checklist = {
        "rollback_checklist_id": f"rollback_proof_checklist_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "items": checklist_items,
        "required_count": len(checklist_items),
        "declared_count": sum(1 for item in checklist_items if item["declared"]),
        "validated_count": sum(1 for item in checklist_items if item["validated"]),
        "rollback_proven": False,
        "can_apply_without_rollback_proof": False,
    }
    checklist.update(BLOCKED_AUTHORITY)
    return checklist


def build_s524_rollback_proof_contract() -> Dict[str, Any]:
    checklist = build_rollback_proof_checklist()
    return _safe_base(
        "S524",
        "rollback_proof_contract_ready",
        checklist=checklist,
        rollback_rules=[
            "Rollback proof must be validated before future update application.",
            "Declared rollback is not the same as proven rollback.",
            "This module does not create backups or restore files.",
        ],
    )


def build_operator_controlled_execution_gate(plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_plan = dict(plan or build_controlled_validation_execution_plan())
    preflight = build_validation_preflight_decision(active_plan)
    rollback = build_rollback_proof_checklist()

    blockers = list(preflight.get("blockers", []))
    if rollback.get("rollback_proven") is False:
        blockers.append("rollback_not_proven")
    if preflight.get("operator_approval_required") is True:
        blockers.append("operator_approval_required")
    if active_plan.get("validation_execution_performed") is False:
        blockers.append("validation_not_executed")

    gate = {
        "controlled_execution_gate_id": f"controlled_execution_gate_{abs(hash(active_plan.get('execution_plan_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "execution_plan_id": active_plan.get("execution_plan_id"),
        "preflight_id": preflight.get("preflight_id"),
        "rollback_checklist_id": rollback.get("rollback_checklist_id"),
        "gate_state": "blocked",
        "operator_approved": False,
        "manual_execution_owner_required": True,
        "execution_allowed_now": False,
        "validation_execution_performed": False,
        "can_promote_after_execution": False,
        "blockers": blockers,
    }
    gate.update(BLOCKED_AUTHORITY)
    return gate


def build_s525_operator_controlled_execution_gate_contract() -> Dict[str, Any]:
    gate = build_operator_controlled_execution_gate()
    return _safe_base(
        "S525",
        "operator_controlled_execution_gate_contract_ready",
        execution_gate=gate,
        gate_rules=[
            "This gate does not execute validation.",
            "Manual execution owner is required for any future command run.",
            "Rollback proof and operator approval are mandatory.",
            "Promotion is impossible until future execution and validation evidence exist.",
        ],
    )


def build_s526_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S526",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "controlled_update_validation_plan_panel",
            "validation_command_manifest",
            "preflight_decision_card",
            "rollback_proof_checklist",
            "operator_controlled_execution_gate",
        ],
        visual_authority="presentation_only",
    )


def build_s526_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()

    normal_inspection = inspector.inspect_update_package_candidate()
    blocked_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="blocked_controlled_plan_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )

    s520 = build_s520_execution_authority_matrix_contract()
    manifest = build_validation_command_manifest(normal_inspection)
    blocked_plan = build_controlled_validation_execution_plan(blocked_inspection)
    normal_plan = build_controlled_validation_execution_plan(normal_inspection)
    preflight = build_validation_preflight_decision(normal_plan)
    rollback = build_rollback_proof_checklist(normal_inspection)
    gate = build_operator_controlled_execution_gate(normal_plan)

    s521 = build_s521_validation_command_manifest_contract()
    s522 = build_s522_controlled_validation_plan_contract()
    s523 = build_s523_preflight_gate_contract()
    s524 = build_s524_rollback_proof_contract()
    s525 = build_s525_operator_controlled_execution_gate_contract()
    s526 = build_s526_cockpit_asset_manifest(project_root)

    checks = {
        "s520_authority_matrix_ready": "run_validation_commands" in s520["blocked_now"],
        "s521_manifest_ready": manifest["execution_allowed_now"] is False and manifest["execution_performed"] is False,
        "s522_plan_ready": normal_plan["execution_allowed_now"] is False and normal_plan["validation_execution_performed"] is False,
        "s523_preflight_ready": preflight["execution_allowed_now"] is False,
        "s524_rollback_proof_blocks_apply": rollback["rollback_proven"] is False and rollback["can_apply_without_rollback_proof"] is False,
        "s525_execution_gate_blocks_execution": gate["execution_allowed_now"] is False and gate["gate_state"] == "blocked",
        "s526_assets_exist": s526["assets"]["js_exists"] is True and s526["assets"]["css_exists"] is True,
        "blocked_plan_blocks": blocked_plan["gate_state"] == "blocked",
        "no_command_execution": all(command["execution_performed"] is False for command in manifest["commands"]),
        "no_validation_execution": normal_plan["validation_execution_performed"] is False and gate["validation_execution_performed"] is False,
        "all_authority_blocked": all(normal_plan.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S526",
        "claire_controlled_update_validation_plan_passed" if ok else "claire_controlled_update_validation_plan_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "manifest": manifest,
            "normal_plan": normal_plan,
            "blocked_plan": blocked_plan,
            "preflight": preflight,
            "rollback": rollback,
            "execution_gate": gate,
        },
        forward_motion_allowed=ok,
        next_phase="S527-S533 Governed update evidence capture and operator review queue",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s526_claire_controlled_update_validation_plan_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_controlled_update_validation_plan_s520_s526(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S520-S526",
        "claire_controlled_update_validation_plan_ready",
        contracts={
            "s520": build_s520_execution_authority_matrix_contract(),
            "s521": build_s521_validation_command_manifest_contract(),
            "s522": build_s522_controlled_validation_plan_contract(),
            "s523": build_s523_preflight_gate_contract(),
            "s524": build_s524_rollback_proof_contract(),
            "s525": build_s525_operator_controlled_execution_gate_contract(),
            "s526": build_s526_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s526_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "CONTROLLED_VALIDATION_PHASES",
    "EXECUTION_GATE_STATES",
    "build_s520_execution_authority_matrix_contract",
    "build_validation_command_manifest",
    "build_s521_validation_command_manifest_contract",
    "build_controlled_validation_execution_plan",
    "build_s522_controlled_validation_plan_contract",
    "build_validation_preflight_decision",
    "build_s523_preflight_gate_contract",
    "build_rollback_proof_checklist",
    "build_s524_rollback_proof_contract",
    "build_operator_controlled_execution_gate",
    "build_s525_operator_controlled_execution_gate_contract",
    "build_s526_cockpit_asset_manifest",
    "build_s526_stop_gate",
    "build_controlled_update_validation_plan_s520_s526",
]
