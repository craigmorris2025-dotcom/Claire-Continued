
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.72"
CONTRACT_NAME = "Rollback-Aware Update Plan Contract"

STAGING_INDEX_PATH = Path("data/update_packs/update_pack_staging_index.json")
ROLLBACK_DIR = Path("data/update_packs/rollback_plans")
ROLLBACK_INDEX_PATH = Path("data/update_packs/rollback_plan_index.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/rollback_update_plan_payload.json")

PROTECTED_PATHS = [
    "claire/app.py",
    "claire/api/routes_pipeline.py",
    "claire/orchestrator/pipeline_v4.py",
    "claire/runtime_truth/runtime_truth_contract_repair.py",
    "claire/dashboard/operator_dashboard_state.py",
    "frontend/command_center/modern/index.html",
    "LAUNCH_PLATFORM.bat",
    "pyproject.toml",
    "requirements.txt",
]

REQUIRED_ROLLBACK_SECTIONS = [
    "plan_identity",
    "linked_update_pack",
    "preflight_snapshot",
    "backup_manifest",
    "restore_steps",
    "validation_after_restore",
    "operator_review",
    "execution_gate",
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


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def latest_pack(staging_index: Dict[str, Any]) -> Dict[str, Any]:
    latest = staging_index.get("latest_pack")
    if isinstance(latest, dict):
        return latest
    packs = staging_index.get("packs")
    if isinstance(packs, list) and packs:
        return packs[-1] if isinstance(packs[-1], dict) else {}
    return {}


def protected_snapshot(root: Path) -> List[Dict[str, Any]]:
    snapshot = []
    for item in PROTECTED_PATHS:
        path = root / item
        snapshot.append({
            "path": item,
            "exists": path.exists(),
            "is_file": path.is_file(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
            "sha256": sha256_file(path),
            "must_backup_before_replace": True,
        })
    return snapshot


def build_restore_steps(plan_id: str, backup_root: str) -> List[Dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "Stop Claire runtime before restore",
            "required": True,
            "command": "Stop any running Claire terminal/server windows before restoring files.",
        },
        {
            "step": 2,
            "name": "Verify rollback backup exists",
            "required": True,
            "command": f"dir {backup_root}",
        },
        {
            "step": 3,
            "name": "Restore files from rollback backup",
            "required": True,
            "command": f"python tools/rollback_restore.py --plan {plan_id}",
            "status": "contract_only_tool_may_not_exist_yet",
        },
        {
            "step": 4,
            "name": "Run rollback validation",
            "required": True,
            "command": "python -m pytest tests/test_v17_72_rollback_aware_update_plan_contract.py -q",
        },
        {
            "step": 5,
            "name": "Launch dashboard after restore",
            "required": True,
            "command": "LAUNCH_PLATFORM.bat",
        },
    ]


def determine_status(staging_index: Dict[str, Any], pack: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []

    if not staging_index:
        blockers.append("update_pack_staging_index_missing_run_v17_71_first")

    if not pack:
        blockers.append("no_staged_update_pack_found")

    if pack.get("execution_enabled") is not False:
        blockers.append("linked_pack_execution_gate_not_false")
    if pack.get("automatic_execution_enabled") is not False:
        blockers.append("linked_pack_automatic_execution_gate_not_false")

    governance = staging_index.get("governance") if isinstance(staging_index.get("governance"), dict) else {}
    if governance.get("staging_only") is not True:
        warnings.append("staging_index_does_not_confirm_staging_only")
    if governance.get("rollback_required") is not True:
        blockers.append("staging_index_does_not_require_rollback")

    if blockers:
        return "blocked", blockers, warnings
    if warnings:
        return "warning"
    return "rollback_plan_ready", blockers, warnings


def build_rollback_update_plan(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    staging_index, staging_source = read_json(root / STAGING_INDEX_PATH)
    pack = latest_pack(staging_index)
    status_result = determine_status(staging_index, pack)
    if len(status_result) == 2:
        status, blockers, warnings = status_result[0], [], status_result[1]
    else:
        status, blockers, warnings = status_result

    pack_id = pack.get("pack_id") or "no_pack"
    plan_id = f"rollback_plan_{slug_time()}_{pack_id}"
    backup_root = f"backups/update_pack_rollbacks/{plan_id}"

    plan = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "plan_identity": {
            "plan_id": plan_id,
            "status": status,
            "execute_now": False,
            "automatic_execution_enabled": False,
            "rollback_execution_enabled": False,
        },
        "linked_update_pack": {
            "pack_id": pack_id,
            "pack_type": pack.get("pack_type"),
            "pack_path": pack.get("path"),
            "pack_hash": pack.get("pack_hash"),
            "pack_status": pack.get("status"),
            "execution_enabled": pack.get("execution_enabled", False),
            "automatic_execution_enabled": pack.get("automatic_execution_enabled", False),
        },
        "preflight_snapshot": {
            "staging_index_source": staging_source,
            "protected_paths": protected_snapshot(root),
            "snapshot_required_before_execution": True,
        },
        "backup_manifest": {
            "backup_root": backup_root,
            "backup_required_before_any_replace": True,
            "backup_every_modified_file": True,
            "backup_hash_required": True,
            "backup_manifest_required": True,
        },
        "restore_steps": build_restore_steps(plan_id, backup_root),
        "validation_after_restore": {
            "required": True,
            "commands": [
                "python -m pytest tests/test_v17_72_rollback_aware_update_plan_contract.py -q",
                "python -m pytest -q",
                "LAUNCH_PLATFORM.bat",
            ],
            "manual_checks": [
                "Dashboard opens",
                "Runtime truth endpoint still responds",
                "Update staging index still readable",
                "No automatic update runner enabled",
            ],
        },
        "operator_review": {
            "required": True,
            "approval_status": "not_approved",
            "review_required_before_execution": True,
            "review_fields": REQUIRED_ROLLBACK_SECTIONS,
        },
        "execution_gate": {
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "rollback_execution_enabled": False,
            "reason": "v17.72 defines rollback-aware planning only. Execution remains disabled until later gated builds.",
            "blockers": blockers,
            "warnings": warnings,
        },
        "governance": {
            "no_hidden_updates": True,
            "no_unreviewed_restore": True,
            "rollback_required_before_update_execution": True,
            "operator_review_required": True,
            "validation_required_after_restore": True,
            "execution_still_disabled": True,
        },
        "next": [
            "v17.73 Automatic Update Runner Gate",
            "v17.74 Update Governance Regression Lock",
            "v17.75 Full end-to-end proof pack",
        ],
    }

    plan_path = root / ROLLBACK_DIR / f"{plan_id}.json"
    write_json(plan_path, plan)

    existing_index, _ = read_json(root / ROLLBACK_INDEX_PATH)
    plans = existing_index.get("plans") if isinstance(existing_index.get("plans"), list) else []
    plans.append({
        "plan_id": plan_id,
        "path": rel(root, plan_path),
        "status": status,
        "linked_pack_id": pack_id,
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "created_at": plan["generated_at"],
    })

    index = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "rollback_dir": str(ROLLBACK_DIR).replace("\\", "/"),
        "plans": plans[-100:],
        "latest_plan": plans[-1],
        "governance": {
            "rollback_plans_required": True,
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "operator_review_required": True,
            "validation_after_restore_required": True,
        },
        "next": plan["next"],
    }
    write_json(root / ROLLBACK_INDEX_PATH, index)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": index["generated_at"],
        "latest_plan": index["latest_plan"],
        "plan_count": len(index["plans"]),
        "linked_pack": plan["linked_update_pack"],
        "execution_gate": plan["execution_gate"],
        "governance": index["governance"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return index


def rollback_update_plan_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    index = build_rollback_update_plan(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "latest_plan": index.get("latest_plan"),
        "plan_count": len(index.get("plans", [])),
        "governance": index.get("governance"),
        "execution_enabled": False,
        "automatic_execution_enabled": False,
    }
