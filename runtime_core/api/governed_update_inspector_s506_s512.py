from __future__ import annotations

"""
Claire Governed Update Package Inspector Readiness — S506-S512

This module creates the first review-only governed update package inspector
contract. It prepares Claire to evaluate update-package metadata safely before
any future staged validation or operator-approved application.

It builds on:
- S471-S477 Claire Knowledge Base Registry
- S492-S498 Useful Output Package Preview
- S499-S505 Claire Answer Memory and Replay

Purpose:
- define governed update package candidate schema
- inspect update metadata with zero-trust checks
- build validation plan and rollback requirements
- enforce operator approval gates
- produce cockpit-ready update inspection summaries

No package is downloaded, no URL is fetched, no files are inspected from disk,
no network request is made, no update is applied, no runtime truth is mutated,
and no automatic update is enabled.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S506-S512"
PHASE = "S506-S512"
JS_ASSET = "frontend/cockpit/shell/assets/claire_governed_update_inspector.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_governed_update_inspector.css"


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
    "persistent_memory_write_performed": False,
    "recursive_self_ingestion_executed": False,
}


UPDATE_RISK_LEVELS = ["blocked", "high", "moderate", "low", "review_ready"]


REQUIRED_UPDATE_METADATA_FIELDS = [
    "package_id",
    "name",
    "version",
    "source",
    "source_type",
    "declared_purpose",
    "target_paths",
    "expected_hash",
    "signature_present",
    "rollback_plan_present",
    "tests_declared",
    "operator_notes",
]


PROTECTED_PATH_MARKERS = [
    "main.py",
    "claire/app",
    "claire/api/server",
    "claire/api/dashboard_payload_bridge",
    "frontend/cockpit/shell",
    "tests/",
    "pyproject.toml",
    "pytest.ini",
]


ALLOWED_SOURCE_TYPES = [
    "operator_provided_local_metadata",
    "governed_update_registry_entry",
    "signed_internal_release_manifest",
    "quarantined_online_metadata",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


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


def build_sample_update_candidate(**overrides: Any) -> Dict[str, Any]:
    candidate = {
        "package_id": "update_candidate_demo_001",
        "name": "Claire governed update metadata demo",
        "version": "v19.89.8-demo",
        "source": "operator_provided_metadata_only",
        "source_type": "operator_provided_local_metadata",
        "declared_purpose": "Demonstrate governed update package inspection readiness without downloading or applying updates.",
        "target_paths": [
            "claire/api/example_future_update.py",
            "tests/test_example_future_update.py",
        ],
        "expected_hash": "sha256:demo-metadata-only-not-a-real-package",
        "signature_present": True,
        "rollback_plan_present": True,
        "tests_declared": [
            "python -X utf8 -m pytest tests/test_example_future_update.py -q --tb=short",
            "python -X utf8 -m pytest --lf -q --tb=short",
        ],
        "operator_notes": "Metadata-only candidate for S506-S512 readiness checks.",
        "network_source_allowed": False,
        "download_allowed": False,
        "install_allowed": False,
        "apply_allowed": False,
    }
    candidate.update(overrides)
    return candidate


def build_s506_update_package_manifest_schema() -> Dict[str, Any]:
    return _safe_base(
        "S506",
        "update_package_manifest_schema_ready",
        required_fields=REQUIRED_UPDATE_METADATA_FIELDS,
        allowed_source_types=ALLOWED_SOURCE_TYPES,
        protected_path_markers=PROTECTED_PATH_MARKERS,
        manifest_rules=[
            "Metadata can be inspected without download.",
            "A package cannot be downloaded or applied from this contract.",
            "Missing hash, signature, rollback plan, or tests blocks readiness.",
            "Protected path changes require heightened review.",
        ],
    )


def inspect_update_package_candidate(candidate: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Inspect update metadata only. No network, file, install, or execution happens."""
    active = dict(candidate or build_sample_update_candidate())

    missing_fields = [field for field in REQUIRED_UPDATE_METADATA_FIELDS if field not in active]
    target_paths = [str(path) for path in active.get("target_paths", []) if str(path).strip()]
    protected_path_hits = [
        path
        for path in target_paths
        if any(marker in path.replace("\\", "/") for marker in PROTECTED_PATH_MARKERS)
    ]

    source_type = str(active.get("source_type", ""))
    allowed_source_type = source_type in ALLOWED_SOURCE_TYPES
    hash_present = bool(str(active.get("expected_hash", "")).strip())
    signature_present = bool(active.get("signature_present") is True)
    rollback_present = bool(active.get("rollback_plan_present") is True)
    tests_declared = isinstance(active.get("tests_declared"), list) and len(active.get("tests_declared", [])) > 0

    forbidden_authority = {
        "network_source_allowed": bool(active.get("network_source_allowed") is True),
        "download_allowed": bool(active.get("download_allowed") is True),
        "install_allowed": bool(active.get("install_allowed") is True),
        "apply_allowed": bool(active.get("apply_allowed") is True),
    }

    score_components = {
        "required_fields_present": 0.18 if not missing_fields else 0.0,
        "allowed_source_type": 0.14 if allowed_source_type else 0.0,
        "hash_present": 0.14 if hash_present else 0.0,
        "signature_present": 0.14 if signature_present else 0.0,
        "rollback_plan_present": 0.14 if rollback_present else 0.0,
        "tests_declared": 0.12 if tests_declared else 0.0,
        "protected_path_penalty": -0.08 if protected_path_hits else 0.0,
        "forbidden_authority_penalty": -0.50 if any(forbidden_authority.values()) else 0.0,
    }
    readiness_score = round(_clamp(sum(score_components.values())), 3)

    if any(forbidden_authority.values()) or missing_fields or not allowed_source_type:
        risk_level = "blocked"
    elif not (hash_present and signature_present and rollback_present and tests_declared):
        risk_level = "high"
    elif protected_path_hits:
        risk_level = "moderate"
    elif readiness_score >= 0.76:
        risk_level = "review_ready"
    else:
        risk_level = "moderate"

    approval_required = True
    inspection = {
        "inspection_id": f"update_inspection_{abs(hash((active.get('package_id'), readiness_score))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "candidate": active,
        "missing_fields": missing_fields,
        "allowed_source_type": allowed_source_type,
        "hash_present": hash_present,
        "signature_present": signature_present,
        "rollback_plan_present": rollback_present,
        "tests_declared": tests_declared,
        "protected_path_hits": protected_path_hits,
        "forbidden_authority_requested": forbidden_authority,
        "score_components": score_components,
        "readiness_score": readiness_score,
        "risk_level": risk_level,
        "approval_required": approval_required,
        "download_allowed": False,
        "install_allowed": False,
        "apply_allowed": False,
        "operator_review_required": True,
        "inspection_scope": "metadata_only",
    }
    inspection.update(BLOCKED_AUTHORITY)
    return inspection


def build_s507_zero_trust_inspection_contract() -> Dict[str, Any]:
    sample = inspect_update_package_candidate()
    blocked = inspect_update_package_candidate(
        build_sample_update_candidate(
            package_id="blocked_update_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )
    return _safe_base(
        "S507",
        "zero_trust_inspection_contract_ready",
        checks=[
            "required_fields_present",
            "allowed_source_type",
            "expected_hash_present",
            "signature_present",
            "rollback_plan_present",
            "tests_declared",
            "protected_path_review",
            "forbidden_authority_requested",
        ],
        sample_inspection={
            "risk_level": sample["risk_level"],
            "readiness_score": sample["readiness_score"],
        },
        blocked_sample={
            "risk_level": blocked["risk_level"],
            "forbidden_authority_requested": blocked["forbidden_authority_requested"],
        },
    )


def build_update_validation_plan(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_inspection = dict(inspection or inspect_update_package_candidate())
    risk_level = active_inspection.get("risk_level", "blocked")
    protected_hits = list(active_inspection.get("protected_path_hits", []))

    validation_steps = [
        {
            "step_id": "metadata_review",
            "label": "Review package metadata",
            "required": True,
            "status": "pending_operator_review",
        },
        {
            "step_id": "hash_verification",
            "label": "Verify expected hash",
            "required": True,
            "status": "not_performed",
        },
        {
            "step_id": "signature_verification",
            "label": "Verify signature",
            "required": True,
            "status": "not_performed",
        },
        {
            "step_id": "static_safety_scan",
            "label": "Static safety scan",
            "required": True,
            "status": "not_performed",
        },
        {
            "step_id": "targeted_test_plan",
            "label": "Run declared targeted tests",
            "required": True,
            "status": "not_performed",
        },
        {
            "step_id": "rollback_validation",
            "label": "Validate rollback plan",
            "required": True,
            "status": "not_performed",
        },
        {
            "step_id": "operator_approval",
            "label": "Operator approval gate",
            "required": True,
            "status": "not_approved",
        },
    ]

    if protected_hits:
        validation_steps.insert(
            4,
            {
                "step_id": "protected_path_review",
                "label": "Protected path review",
                "required": True,
                "status": "pending_operator_review",
                "paths": protected_hits,
            },
        )

    plan = {
        "plan_id": f"update_validation_plan_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "risk_level": risk_level,
        "validation_steps": validation_steps,
        "can_advance_to_staged_validation": risk_level in {"review_ready", "moderate"},
        "can_apply_update": False,
        "network_required": False,
        "download_required": False,
        "operator_review_required": True,
    }
    plan.update(BLOCKED_AUTHORITY)
    return plan


def build_s508_validation_plan_contract() -> Dict[str, Any]:
    inspection = inspect_update_package_candidate()
    plan = build_update_validation_plan(inspection)
    return _safe_base(
        "S508",
        "update_validation_plan_contract_ready",
        validation_plan=plan,
        validation_rules=[
            "Validation plan is generated from metadata inspection only.",
            "Hash/signature checks are declared as required but not performed here.",
            "Tests are declared but not executed here.",
            "Operator approval remains required.",
        ],
    )


def build_rollback_readiness_assessment(inspection: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_inspection = dict(inspection or inspect_update_package_candidate())
    candidate = active_inspection.get("candidate", {})
    rollback_present = bool(active_inspection.get("rollback_plan_present") is True)
    protected_hits = list(active_inspection.get("protected_path_hits", []))

    readiness = {
        "rollback_id": f"rollback_readiness_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "rollback_plan_present": rollback_present,
        "target_path_count": len(candidate.get("target_paths", []) or []),
        "protected_path_count": len(protected_hits),
        "rollback_required": True,
        "rollback_validated": False,
        "can_apply_without_rollback_validation": False,
        "rollback_requirements": [
            "backup_active_files_before_apply",
            "prove_restore_command_or_file_map",
            "validate_tests_after_rollback",
            "record_operator_approval",
        ],
        "status": "rollback_plan_declared_not_validated" if rollback_present else "blocked_missing_rollback_plan",
    }
    readiness.update(BLOCKED_AUTHORITY)
    return readiness


def build_s509_rollback_readiness_contract() -> Dict[str, Any]:
    rollback = build_rollback_readiness_assessment()
    return _safe_base(
        "S509",
        "rollback_readiness_contract_ready",
        rollback_assessment=rollback,
        rollback_rules=[
            "Rollback must be present before review readiness.",
            "Rollback must be validated before any future update application.",
            "Protected path updates require heightened rollback proof.",
            "This module does not create backups or alter files.",
        ],
    )


def build_operator_approval_gate(inspection: Optional[Dict[str, Any]] = None, validation_plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_inspection = dict(inspection or inspect_update_package_candidate())
    active_plan = dict(validation_plan or build_update_validation_plan(active_inspection))

    blockers: List[str] = []
    if active_inspection.get("risk_level") == "blocked":
        blockers.append("inspection_risk_blocked")
    if active_inspection.get("missing_fields"):
        blockers.append("missing_required_metadata")
    if any(active_inspection.get("forbidden_authority_requested", {}).values()):
        blockers.append("candidate_requested_forbidden_authority")
    if not active_inspection.get("rollback_plan_present"):
        blockers.append("missing_rollback_plan")
    if not active_inspection.get("signature_present"):
        blockers.append("missing_signature")
    if not active_inspection.get("hash_present"):
        blockers.append("missing_expected_hash")

    gate = {
        "approval_gate_id": f"operator_approval_gate_{abs(hash(active_inspection.get('inspection_id'))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "plan_id": active_plan.get("plan_id"),
        "approval_required": True,
        "operator_approved": False,
        "blockers": blockers,
        "approval_state": "blocked" if blockers else "awaiting_operator_review",
        "can_apply_update": False,
        "can_download_package": False,
        "can_mutate_runtime": False,
        "future_required_approval_text": "I approve this staged update after validation and rollback proof.",
    }
    gate.update(BLOCKED_AUTHORITY)
    return gate


def build_s510_operator_approval_gate_contract() -> Dict[str, Any]:
    inspection = inspect_update_package_candidate()
    plan = build_update_validation_plan(inspection)
    gate = build_operator_approval_gate(inspection, plan)
    return _safe_base(
        "S510",
        "operator_approval_gate_contract_ready",
        approval_gate=gate,
        approval_rules=[
            "Operator approval is required but not sufficient by itself.",
            "Validation and rollback proof must pass before any future application.",
            "Approval state cannot override blocked authority flags.",
            "Automatic updates remain disabled.",
        ],
    )


def build_s511_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S511",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "governed_update_inspector_panel",
            "update_candidate_summary",
            "zero_trust_check_cards",
            "validation_plan_steps",
            "rollback_readiness_card",
            "operator_approval_gate",
        ],
        visual_authority="presentation_only",
    )


def build_s512_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s506 = build_s506_update_package_manifest_schema()
    s507 = build_s507_zero_trust_inspection_contract()
    inspection = inspect_update_package_candidate()
    blocked_inspection = inspect_update_package_candidate(
        build_sample_update_candidate(
            package_id="blocked_missing_safety",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            network_source_allowed=True,
            download_allowed=True,
            install_allowed=True,
            apply_allowed=True,
        )
    )
    validation_plan = build_update_validation_plan(inspection)
    rollback = build_rollback_readiness_assessment(inspection)
    approval_gate = build_operator_approval_gate(inspection, validation_plan)
    s508 = build_s508_validation_plan_contract()
    s509 = build_s509_rollback_readiness_contract()
    s510 = build_s510_operator_approval_gate_contract()
    s511 = build_s511_cockpit_asset_manifest(project_root)

    checks = {
        "s506_schema_ready": "expected_hash" in s506["required_fields"],
        "s507_zero_trust_ready": s507["blocked_sample"]["risk_level"] == "blocked",
        "s508_validation_plan_ready": validation_plan["can_apply_update"] is False and len(validation_plan["validation_steps"]) >= 7,
        "s509_rollback_ready": rollback["can_apply_without_rollback_validation"] is False,
        "s510_approval_gate_ready": approval_gate["operator_approved"] is False and approval_gate["can_apply_update"] is False,
        "s511_assets_exist": s511["assets"]["js_exists"] is True and s511["assets"]["css_exists"] is True,
        "inspection_metadata_only": inspection["inspection_scope"] == "metadata_only",
        "blocked_candidate_blocked": blocked_inspection["risk_level"] == "blocked",
        "no_download_or_apply": all(
            value is False
            for value in [
                inspection["download_allowed"],
                inspection["install_allowed"],
                inspection["apply_allowed"],
                validation_plan["download_required"],
                approval_gate["can_download_package"],
                approval_gate["can_apply_update"],
            ]
        ),
        "all_authority_blocked": all(inspection.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S512",
        "claire_governed_update_inspector_passed" if ok else "claire_governed_update_inspector_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "inspection": inspection,
            "blocked_inspection": blocked_inspection,
            "validation_plan": validation_plan,
            "rollback": rollback,
            "approval_gate": approval_gate,
        },
        forward_motion_allowed=ok,
        next_phase="S513-S519 Staged update validation sandbox contract",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s512_claire_governed_update_inspector_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_governed_update_inspector_s506_s512(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S506-S512",
        "claire_governed_update_inspector_ready",
        contracts={
            "s506": build_s506_update_package_manifest_schema(),
            "s507": build_s507_zero_trust_inspection_contract(),
            "s508": build_s508_validation_plan_contract(),
            "s509": build_s509_rollback_readiness_contract(),
            "s510": build_s510_operator_approval_gate_contract(),
            "s511": build_s511_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s512_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "UPDATE_RISK_LEVELS",
    "REQUIRED_UPDATE_METADATA_FIELDS",
    "PROTECTED_PATH_MARKERS",
    "ALLOWED_SOURCE_TYPES",
    "build_sample_update_candidate",
    "build_s506_update_package_manifest_schema",
    "inspect_update_package_candidate",
    "build_s507_zero_trust_inspection_contract",
    "build_update_validation_plan",
    "build_s508_validation_plan_contract",
    "build_rollback_readiness_assessment",
    "build_s509_rollback_readiness_contract",
    "build_operator_approval_gate",
    "build_s510_operator_approval_gate_contract",
    "build_s511_cockpit_asset_manifest",
    "build_s512_stop_gate",
    "build_governed_update_inspector_s506_s512",
]
