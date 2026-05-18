from __future__ import annotations

"""
Claire Staged Update Validation Sandbox Contract — S513-S519

This module defines the governed validation-sandbox contract that must exist
before Claire can safely move from metadata-only update inspection toward a
future staged update validation workflow.

It builds on:
- S506-S512 Governed Update Package Inspector Readiness

Purpose:
- define a sandbox profile without creating or mutating a real sandbox
- map proposed update target paths into review categories
- define dry-run validation steps without executing tests
- define promotion / rejection / quarantine criteria
- preserve rollback, approval, and protected-path requirements
- keep automatic updates and runtime mutation blocked

No package is downloaded, no package is installed, no tests are executed,
no sandbox files are created, no runtime truth is mutated, no network request
is made, and no automatic update authority is enabled.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S513-S519"
PHASE = "S513-S519"
JS_ASSET = "frontend/cockpit/shell/assets/claire_staged_update_sandbox.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_staged_update_sandbox.css"


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
    "promotion_performed": False,
    "quarantine_write_performed": False,
}


SANDBOX_STATUSES = [
    "contract_ready",
    "awaiting_metadata_review",
    "eligible_for_future_sandbox_creation",
    "blocked_missing_validation_inputs",
    "blocked_protected_path_review",
    "rejected",
]


VALIDATION_STEP_STATUSES = [
    "declared_not_executed",
    "pending_operator_review",
    "blocked",
    "future_executable_after_approval",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


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
    from claire.api import claire_governed_update_inspector_s506_s512 as update_inspector

    return update_inspector


def build_s513_sandbox_profile_contract() -> Dict[str, Any]:
    return _safe_base(
        "S513",
        "sandbox_profile_contract_ready",
        sandbox_profile_fields=[
            "sandbox_id",
            "inspection_id",
            "candidate_package_id",
            "risk_level",
            "protected_path_hits",
            "sandbox_status",
            "can_create_sandbox_now",
            "future_sandbox_root_policy",
            "required_preconditions",
            "blocked_authority",
        ],
        sandbox_statuses=SANDBOX_STATUSES,
        rules=[
            "S513 defines sandbox profile shape only.",
            "No sandbox directory or files are created here.",
            "Metadata inspection must exist before a future sandbox can be created.",
            "Protected-path changes require heightened review.",
        ],
    )


def build_validation_sandbox_profile(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    candidate = active_inspection.get("candidate", {})
    missing_fields = list(active_inspection.get("missing_fields", []))
    protected_hits = list(active_inspection.get("protected_path_hits", []))
    risk_level = active_inspection.get("risk_level", "blocked")

    if risk_level == "blocked" or missing_fields:
        sandbox_status = "blocked_missing_validation_inputs"
    elif protected_hits:
        sandbox_status = "blocked_protected_path_review"
    elif risk_level in {"review_ready", "moderate"}:
        sandbox_status = "eligible_for_future_sandbox_creation"
    else:
        sandbox_status = "awaiting_metadata_review"

    profile = {
        "sandbox_id": f"validation_sandbox_profile_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "candidate_package_id": candidate.get("package_id"),
        "risk_level": risk_level,
        "protected_path_hits": protected_hits,
        "sandbox_status": sandbox_status,
        "can_create_sandbox_now": False,
        "future_sandbox_root_policy": "isolated_temp_or_quarantine_path_only_after_operator_approval",
        "required_preconditions": [
            "metadata_review_passed",
            "hash_declared",
            "signature_declared",
            "rollback_plan_declared",
            "tests_declared",
            "operator_review_complete",
        ],
        "blocked_authority": dict(BLOCKED_AUTHORITY),
    }
    profile.update(BLOCKED_AUTHORITY)
    return profile


def classify_target_path(path: str) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    normalized = str(path or "").replace("\\", "/")
    protected_markers = list(getattr(inspector, "PROTECTED_PATH_MARKERS", []))
    protected_hits = [marker for marker in protected_markers if marker in normalized]

    if not normalized.strip():
        category = "invalid"
        review_level = "blocked"
    elif protected_hits:
        category = "protected_runtime_or_test_path"
        review_level = "heightened_review"
    elif normalized.startswith("claire/"):
        category = "backend_module"
        review_level = "standard_review"
    elif normalized.startswith("frontend/"):
        category = "frontend_asset"
        review_level = "standard_review"
    elif normalized.startswith("tests/"):
        category = "test_file"
        review_level = "heightened_review"
    else:
        category = "other_project_path"
        review_level = "operator_review"

    return {
        "path": normalized,
        "category": category,
        "review_level": review_level,
        "protected_hits": protected_hits,
        "write_allowed_now": False,
        "requires_backup": category != "invalid",
        "requires_post_validation_test": category != "invalid",
    }


def build_staged_file_impact_map(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    candidate = active_inspection.get("candidate", {})
    target_paths = [str(path) for path in candidate.get("target_paths", []) if str(path).strip()]
    path_reviews = [classify_target_path(path) for path in target_paths]

    protected_count = sum(1 for item in path_reviews if item["protected_hits"])
    invalid_count = sum(1 for item in path_reviews if item["category"] == "invalid")
    impact_level = "blocked" if invalid_count else "protected" if protected_count else "standard"

    impact_map = {
        "impact_map_id": f"staged_file_impact_map_{abs(hash(tuple(target_paths))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "target_path_count": len(target_paths),
        "path_reviews": path_reviews,
        "protected_path_count": protected_count,
        "invalid_path_count": invalid_count,
        "impact_level": impact_level,
        "write_allowed_now": False,
        "backup_required": bool(target_paths),
        "operator_review_required": True,
    }
    impact_map.update(BLOCKED_AUTHORITY)
    return impact_map


def build_s514_staged_file_impact_map_contract() -> Dict[str, Any]:
    sample_map = build_staged_file_impact_map()
    protected_sample = build_staged_file_impact_map(
        _load_update_inspector_module().inspect_update_package_candidate(
            _load_update_inspector_module().build_sample_update_candidate(
                package_id="protected_path_demo",
                target_paths=["claire/api/dashboard_payload_bridge.py", "tests/test_dashboard_payload.py"],
            )
        )
    )
    return _safe_base(
        "S514",
        "staged_file_impact_map_contract_ready",
        path_categories=[
            "protected_runtime_or_test_path",
            "backend_module",
            "frontend_asset",
            "test_file",
            "other_project_path",
            "invalid",
        ],
        sample_impact_map={
            "impact_level": sample_map["impact_level"],
            "target_path_count": sample_map["target_path_count"],
        },
        protected_sample={
            "impact_level": protected_sample["impact_level"],
            "protected_path_count": protected_sample["protected_path_count"],
        },
    )


def build_dry_run_validation_steps(
    inspection: Optional[Dict[str, Any]] = None,
    impact_map: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    active_impact = dict(impact_map or build_staged_file_impact_map(active_inspection))
    candidate = active_inspection.get("candidate", {})
    declared_tests = list(candidate.get("tests_declared", []) or [])

    steps: List[Dict[str, Any]] = [
        {
            "step_id": "sandbox_profile_review",
            "label": "Review sandbox eligibility profile",
            "status": "pending_operator_review",
            "execution_performed": False,
            "required": True,
        },
        {
            "step_id": "file_impact_review",
            "label": "Review staged file impact map",
            "status": "pending_operator_review",
            "execution_performed": False,
            "required": True,
        },
        {
            "step_id": "hash_signature_precheck",
            "label": "Hash and signature precheck",
            "status": "declared_not_executed",
            "execution_performed": False,
            "required": True,
        },
        {
            "step_id": "rollback_precheck",
            "label": "Rollback plan precheck",
            "status": "declared_not_executed",
            "execution_performed": False,
            "required": True,
        },
        {
            "step_id": "declared_targeted_tests",
            "label": "Declared targeted tests",
            "status": "declared_not_executed",
            "execution_performed": False,
            "required": True,
            "declared_tests": declared_tests,
        },
        {
            "step_id": "full_regression_gate",
            "label": "Full regression gate",
            "status": "declared_not_executed",
            "execution_performed": False,
            "required": True,
        },
    ]

    if active_impact.get("protected_path_count", 0) > 0:
        steps.insert(
            2,
            {
                "step_id": "protected_path_manual_review",
                "label": "Protected path manual review",
                "status": "pending_operator_review",
                "execution_performed": False,
                "required": True,
                "protected_path_count": active_impact.get("protected_path_count", 0),
            },
        )

    blocked = active_inspection.get("risk_level") == "blocked" or active_impact.get("impact_level") == "blocked"

    plan = {
        "dry_run_plan_id": f"dry_run_validation_plan_{abs(hash((active_inspection.get('inspection_id'), active_impact.get('impact_map_id')))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "impact_map_id": active_impact.get("impact_map_id"),
        "steps": steps,
        "step_count": len(steps),
        "blocked": blocked,
        "can_execute_now": False,
        "can_create_sandbox_now": False,
        "test_execution_performed": False,
        "operator_review_required": True,
    }
    plan.update(BLOCKED_AUTHORITY)
    return plan


def build_s515_dry_run_validation_contract() -> Dict[str, Any]:
    plan = build_dry_run_validation_steps()
    return _safe_base(
        "S515",
        "dry_run_validation_contract_ready",
        validation_step_statuses=VALIDATION_STEP_STATUSES,
        sample_plan={
            "step_count": plan["step_count"],
            "can_execute_now": plan["can_execute_now"],
            "test_execution_performed": plan["test_execution_performed"],
        },
        validation_rules=[
            "Validation steps are declared only.",
            "No test command is executed here.",
            "No sandbox directory is created here.",
            "Protected-path updates require manual review before future execution.",
        ],
    )


def build_promotion_readiness_decision(
    inspection: Optional[Dict[str, Any]] = None,
    sandbox_profile: Optional[Dict[str, Any]] = None,
    dry_run_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    active_profile = dict(sandbox_profile or build_validation_sandbox_profile(active_inspection))
    active_plan = dict(dry_run_plan or build_dry_run_validation_steps(active_inspection))

    blockers: List[str] = []
    if active_inspection.get("risk_level") == "blocked":
        blockers.append("inspection_blocked")
    if active_profile.get("sandbox_status") in {"blocked_missing_validation_inputs", "blocked_protected_path_review"}:
        blockers.append(active_profile.get("sandbox_status"))
    if active_plan.get("blocked") is True:
        blockers.append("dry_run_plan_blocked")
    if active_plan.get("test_execution_performed") is False:
        blockers.append("tests_not_executed")
    if active_profile.get("can_create_sandbox_now") is False:
        blockers.append("sandbox_not_created")
    if active_inspection.get("approval_required") is True:
        blockers.append("operator_approval_required")

    decision = {
        "promotion_decision_id": f"promotion_readiness_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "sandbox_id": active_profile.get("sandbox_id"),
        "dry_run_plan_id": active_plan.get("dry_run_plan_id"),
        "promotion_ready": False,
        "promotion_performed": False,
        "blockers": blockers,
        "decision": "not_promotable_contract_only",
        "operator_review_required": True,
    }
    decision.update(BLOCKED_AUTHORITY)
    return decision


def build_s516_promotion_readiness_contract() -> Dict[str, Any]:
    decision = build_promotion_readiness_decision()
    return _safe_base(
        "S516",
        "promotion_readiness_contract_ready",
        promotion_decision=decision,
        promotion_rules=[
            "Promotion cannot occur from this module.",
            "Future promotion requires sandbox creation, test execution, rollback proof, and operator approval.",
            "Runtime mutation remains blocked.",
            "Automatic updates remain blocked.",
        ],
    )


def build_rejection_or_quarantine_decision(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    risk = active_inspection.get("risk_level", "blocked")
    forbidden = active_inspection.get("forbidden_authority_requested", {})

    reasons: List[str] = []
    if risk == "blocked":
        reasons.append("risk_level_blocked")
    if active_inspection.get("missing_fields"):
        reasons.append("missing_required_fields")
    if any(forbidden.values()):
        reasons.append("forbidden_authority_requested")
    if not active_inspection.get("rollback_plan_present"):
        reasons.append("missing_rollback_plan")
    if not active_inspection.get("signature_present"):
        reasons.append("missing_signature")
    if not active_inspection.get("hash_present"):
        reasons.append("missing_hash")

    decision = "reject_candidate" if reasons else "hold_for_operator_review"
    quarantine_required = bool(reasons)

    result = {
        "quarantine_decision_id": f"quarantine_decision_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "decision": decision,
        "reasons": reasons,
        "quarantine_required": quarantine_required,
        "quarantine_write_performed": False,
        "rejection_notice": "Candidate is rejected or held for review; no quarantine file is written by this contract.",
    }
    result.update(BLOCKED_AUTHORITY)
    return result


def build_s517_rejection_quarantine_contract() -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    blocked = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="reject_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )
    decision = build_rejection_or_quarantine_decision(blocked)
    return _safe_base(
        "S517",
        "rejection_quarantine_contract_ready",
        sample_decision=decision,
        quarantine_rules=[
            "Rejected candidates are identified without writing quarantine files.",
            "Future quarantine writer must be separately governed.",
            "Forbidden authority requests force rejection or quarantine review.",
        ],
    )


def build_s518_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S518",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "staged_update_sandbox_panel",
            "sandbox_profile_card",
            "file_impact_map_card",
            "dry_run_validation_steps",
            "promotion_readiness_card",
            "rejection_quarantine_card",
        ],
        visual_authority="presentation_only",
    )


def build_s519_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()

    inspection = inspector.inspect_update_package_candidate()
    protected_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="protected_demo",
            target_paths=["claire/api/dashboard_payload_bridge.py", "tests/test_dashboard_payload.py"],
        )
    )
    blocked_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="blocked_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )

    s513 = build_s513_sandbox_profile_contract()
    sandbox_profile = build_validation_sandbox_profile(inspection)
    protected_profile = build_validation_sandbox_profile(protected_inspection)
    impact_map = build_staged_file_impact_map(inspection)
    protected_impact = build_staged_file_impact_map(protected_inspection)
    dry_run = build_dry_run_validation_steps(inspection, impact_map)
    promotion = build_promotion_readiness_decision(inspection, sandbox_profile, dry_run)
    rejection = build_rejection_or_quarantine_decision(blocked_inspection)

    s514 = build_s514_staged_file_impact_map_contract()
    s515 = build_s515_dry_run_validation_contract()
    s516 = build_s516_promotion_readiness_contract()
    s517 = build_s517_rejection_quarantine_contract()
    s518 = build_s518_cockpit_asset_manifest(project_root)

    checks = {
        "s513_profile_contract_ready": "sandbox_id" in s513["sandbox_profile_fields"],
        "s514_impact_contract_ready": s514["protected_sample"]["impact_level"] == "protected",
        "s515_dry_run_contract_ready": s515["sample_plan"]["test_execution_performed"] is False,
        "s516_promotion_contract_blocks_promotion": s516["promotion_decision"]["promotion_ready"] is False,
        "s517_rejection_contract_ready": s517["sample_decision"]["quarantine_required"] is True,
        "s518_assets_exist": s518["assets"]["js_exists"] is True and s518["assets"]["css_exists"] is True,
        "sandbox_profile_no_creation": sandbox_profile["can_create_sandbox_now"] is False and sandbox_profile["sandbox_created"] is False,
        "protected_profile_blocks_review": protected_profile["sandbox_status"] == "blocked_protected_path_review",
        "impact_map_no_writes": impact_map["write_allowed_now"] is False and impact_map["sandbox_file_write_performed"] is False,
        "dry_run_no_execution": dry_run["can_execute_now"] is False and dry_run["test_execution_performed"] is False,
        "promotion_not_performed": promotion["promotion_ready"] is False and promotion["promotion_performed"] is False,
        "rejection_no_quarantine_write": rejection["quarantine_required"] is True and rejection["quarantine_write_performed"] is False,
        "all_authority_blocked": all(sandbox_profile.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S519",
        "claire_staged_update_sandbox_contract_passed" if ok else "claire_staged_update_sandbox_contract_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "sandbox_profile": sandbox_profile,
            "protected_profile": protected_profile,
            "impact_map": impact_map,
            "protected_impact": protected_impact,
            "dry_run": dry_run,
            "promotion": promotion,
            "rejection": rejection,
        },
        forward_motion_allowed=ok,
        next_phase="S520-S526 Controlled update validation execution plan",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s519_claire_staged_update_sandbox_contract_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_staged_update_sandbox_contract_s513_s519(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S513-S519",
        "claire_staged_update_sandbox_contract_ready",
        contracts={
            "s513": build_s513_sandbox_profile_contract(),
            "s514": build_s514_staged_file_impact_map_contract(),
            "s515": build_s515_dry_run_validation_contract(),
            "s516": build_s516_promotion_readiness_contract(),
            "s517": build_s517_rejection_quarantine_contract(),
            "s518": build_s518_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s519_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "SANDBOX_STATUSES",
    "VALIDATION_STEP_STATUSES",
    "build_s513_sandbox_profile_contract",
    "build_validation_sandbox_profile",
    "classify_target_path",
    "build_staged_file_impact_map",
    "build_s514_staged_file_impact_map_contract",
    "build_dry_run_validation_steps",
    "build_s515_dry_run_validation_contract",
    "build_promotion_readiness_decision",
    "build_s516_promotion_readiness_contract",
    "build_rejection_or_quarantine_decision",
    "build_s517_rejection_quarantine_contract",
    "build_s518_cockpit_asset_manifest",
    "build_s519_stop_gate",
    "build_claire_staged_update_sandbox_contract_s513_s519",
]
