
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.71"
CONTRACT_NAME = "Governed Update Pack Staging"

INTERNET_READINESS_PATH = Path("data/internet_readiness/internet_readiness_verification.json")
BUILD_VALIDATION_PATH = Path("data/validation/buildability_viability_manufacturability_validation.json")
RUNTIME_TRUTH_PATH = Path("data/runtime/runtime_truth_canonical.json")

STAGING_DIR = Path("data/update_packs/staging")
PACK_INDEX_PATH = Path("data/update_packs/update_pack_staging_index.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/update_pack_staging_payload.json")

PROTECTED_PATHS = [
    "claire/app.py",
    "claire/api/routes_pipeline.py",
    "claire/orchestrator/pipeline_v4.py",
    "claire/runtime_truth/runtime_truth_contract_repair.py",
    "frontend/command_center/modern/index.html",
    "LAUNCH_PLATFORM.bat",
    "pyproject.toml",
    "requirements.txt",
]

REQUIRED_UPDATE_PACK_SECTIONS = [
    "pack_identity",
    "source_authority",
    "scope",
    "file_operations",
    "validation_plan",
    "rollback_plan",
    "operator_review",
    "execution_gate",
]

DEFAULT_PACK_TYPES = [
    "runtime_truth_patch",
    "dashboard_contract_patch",
    "route_contract_patch",
    "internet_source_policy_patch",
    "update_governance_patch",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def slug_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def path_status(root: Path, paths: List[str]) -> Dict[str, Any]:
    present = []
    missing = []
    for item in paths:
        path = root / item
        if path.exists():
            present.append(item)
        else:
            missing.append(item)
    return {"present": present, "missing": missing, "score": len(present), "out_of": len(paths)}


def determine_staging_status(internet: Dict[str, Any], validation: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []

    internet_status = str(internet.get("status", "missing"))
    internet_readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}

    if not internet:
        warnings.append("internet_readiness_verification_missing")
    elif internet_status == "blocked":
        blockers.append("internet_readiness_blocked")
    elif internet_status == "warning":
        warnings.append("internet_readiness_warning")

    if internet_readiness.get("safe_for_automatic_updates") is True:
        warnings.append("internet readiness claims automatic updates are safe, but v17.71 still stages only and does not execute updates")
    if internet_readiness.get("automatic_updates_enabled") is True:
        blockers.append("automatic_updates_already_enabled_before_governance_pack")

    validation_status = str(validation.get("status", "missing"))
    if not validation:
        warnings.append("buildability_validation_missing")
    elif validation_status == "blocked":
        warnings.append("buildability_validation_blocked_for_design_route")

    return ("blocked" if blockers else ("warning" if warnings else "staging_ready")), blockers, warnings


def build_pack_template(root: Path, pack_id: str, pack_type: str, internet: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    status, blockers, warnings = determine_staging_status(internet, validation)

    pack = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "pack_identity": {
            "pack_id": pack_id,
            "pack_type": pack_type,
            "status": status,
            "stage_only": True,
            "execute_now": False,
            "automatic_update": False,
        },
        "source_authority": {
            "approved_sources_required": True,
            "source_trust_required": True,
            "allowlist_required": True,
            "quarantine_unknown_sources": True,
            "internet_readiness_status": internet.get("status", "missing"),
            "internet_readiness_source": str(INTERNET_READINESS_PATH).replace("\\", "/"),
        },
        "scope": {
            "description": "Governed update pack staging contract. This pack defines what could be updated, not execution.",
            "allowed_pack_types": DEFAULT_PACK_TYPES,
            "protected_paths": PROTECTED_PATHS,
            "requires_operator_scope_approval": True,
        },
        "file_operations": {
            "operations": [],
            "allowed_operations": ["write_new_file", "replace_file_with_backup", "append_guarded_mount", "write_report"],
            "forbidden_operations": ["delete_without_archive", "modify_protected_runtime_without_validation", "enable_background_updates", "execute_external_code"],
            "all_operations_require_hash": True,
        },
        "validation_plan": {
            "required_before_execution": [
                "syntax_check",
                "targeted_pytest",
                "route_smoke_test",
                "dashboard_contract_check",
                "runtime_truth_rebuild",
                "rollback_manifest_check",
            ],
            "validation_gauntlet_required": True,
            "current_build_validation_status": validation.get("status", "missing"),
            "current_build_validation_source": str(BUILD_VALIDATION_PATH).replace("\\", "/"),
        },
        "rollback_plan": {
            "required": True,
            "backup_required_before_replace": True,
            "rollback_manifest_required": True,
            "restore_command_required": True,
            "rollback_test_required": True,
        },
        "operator_review": {
            "required": True,
            "review_fields": [
                "pack_id",
                "pack_type",
                "source_authority",
                "scope",
                "file_operations",
                "validation_plan",
                "rollback_plan",
                "execution_gate",
            ],
            "approval_status": "not_approved",
        },
        "execution_gate": {
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "reason": "v17.71 stages update packs only. Execution is reserved for v17.72-v17.74 gates.",
            "blockers": blockers,
            "warnings": warnings,
        },
        "governance": {
            "no_hidden_updates": True,
            "no_uncontrolled_self_modification": True,
            "operator_review_required": True,
            "rollback_required": True,
            "validation_required": True,
            "source_trust_required": True,
            "staging_only": True,
        },
        "pack_hash": "",
    }

    canonical = json.dumps(pack, sort_keys=True, ensure_ascii=False)
    pack["pack_hash"] = sha256_text(canonical)
    return pack


def build_update_pack_staging(project_root: Optional[Path | str] = None, pack_type: str = "update_governance_patch") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    internet, internet_source = read_json(root / INTERNET_READINESS_PATH)
    validation, validation_source = read_json(root / BUILD_VALIDATION_PATH)
    runtime_truth, runtime_source = read_json(root / RUNTIME_TRUTH_PATH)

    pack_id = f"update_pack_{slug_time()}_{pack_type}"
    pack = build_pack_template(root, pack_id, pack_type, internet, validation)

    pack_path = root / STAGING_DIR / f"{pack_id}.json"
    write_json(pack_path, pack)

    existing_index, _ = read_json(root / PACK_INDEX_PATH)
    packs = existing_index.get("packs") if isinstance(existing_index.get("packs"), list) else []
    packs.append({
        "pack_id": pack_id,
        "pack_type": pack_type,
        "path": rel(root, pack_path),
        "status": pack["pack_identity"]["status"],
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "created_at": pack["generated_at"],
        "pack_hash": pack["pack_hash"],
    })

    index = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "staging_dir": str(STAGING_DIR).replace("\\", "/"),
        "sources": {
            "internet_readiness": internet_source,
            "build_validation": validation_source,
            "runtime_truth": runtime_source,
        },
        "protected_paths": path_status(root, PROTECTED_PATHS),
        "packs": packs[-100:],
        "latest_pack": packs[-1],
        "governance": {
            "staging_only": True,
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "operator_review_required": True,
            "rollback_required": True,
            "validation_required": True,
        },
        "next": [
            "v17.72 Rollback-Aware Update Plan Contract",
            "v17.73 Automatic Update Runner Gate",
            "v17.74 Update Governance Regression Lock",
            "v17.75 Full end-to-end proof pack",
        ],
    }
    write_json(root / PACK_INDEX_PATH, index)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": index["generated_at"],
        "latest_pack": index["latest_pack"],
        "pack_count": len(index["packs"]),
        "protected_paths": index["protected_paths"],
        "governance": index["governance"],
        "execution_enabled": False,
        "automatic_updates_enabled": False,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return index


def update_pack_staging_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    index = build_update_pack_staging(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "latest_pack": index.get("latest_pack"),
        "pack_count": len(index.get("packs", [])),
        "governance": index.get("governance"),
        "execution_enabled": False,
        "automatic_updates_enabled": False,
    }
