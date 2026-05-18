
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

VERSION = "v17.73"
CONTRACT_NAME = "Automatic Update Runner Gate"

STAGING_INDEX_PATH = Path("data/update_packs/update_pack_staging_index.json")
ROLLBACK_INDEX_PATH = Path("data/update_packs/rollback_plan_index.json")
INTERNET_READINESS_PATH = Path("data/internet_readiness/internet_readiness_verification.json")

RUNNER_GATE_PATH = Path("data/update_packs/automatic_update_runner_gate.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/automatic_update_runner_gate_payload.json")

REQUIRED_GATE_CHECKS = [
    "staged_update_pack_exists",
    "rollback_plan_exists",
    "internet_readiness_checked",
    "source_trust_required",
    "operator_review_required",
    "validation_required",
    "rollback_required",
    "automatic_execution_disabled_until_approved",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def latest_item(index: Dict[str, Any], key: str, latest_key: str) -> Dict[str, Any]:
    latest = index.get(latest_key)
    if isinstance(latest, dict):
        return latest
    items = index.get(key)
    if isinstance(items, list) and items and isinstance(items[-1], dict):
        return items[-1]
    return {}


def gate_check(name: str, passed: bool, detail: str, severity: str = "blocker") -> Dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "detail": detail,
        "severity": severity,
    }


def build_checks(staging: Dict[str, Any], rollback: Dict[str, Any], internet: Dict[str, Any]) -> Dict[str, Any]:
    latest_pack = latest_item(staging, "packs", "latest_pack")
    latest_plan = latest_item(rollback, "plans", "latest_plan")
    staging_governance = staging.get("governance") if isinstance(staging.get("governance"), dict) else {}
    rollback_governance = rollback.get("governance") if isinstance(rollback.get("governance"), dict) else {}
    internet_governance = internet.get("governance") if isinstance(internet.get("governance"), dict) else {}
    internet_readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}

    checks = {
        "staged_update_pack_exists": gate_check(
            "staged_update_pack_exists",
            bool(latest_pack),
            "Latest staged update pack found." if latest_pack else "No staged update pack found. Run v17.71 first.",
        ),
        "rollback_plan_exists": gate_check(
            "rollback_plan_exists",
            bool(latest_plan),
            "Latest rollback plan found." if latest_plan else "No rollback plan found. Run v17.72 first.",
        ),
        "internet_readiness_checked": gate_check(
            "internet_readiness_checked",
            bool(internet),
            f"Internet readiness status: {internet.get('status', 'missing')}" if internet else "Internet readiness missing. Run v17.70 first.",
            "warning",
        ),
        "source_trust_required": gate_check(
            "source_trust_required",
            internet_governance.get("source_trust_required") is True or internet_governance.get("source_allowlist_required") is True,
            "Source trust / allowlist governance detected." if internet_governance else "Source trust governance not detected.",
        ),
        "operator_review_required": gate_check(
            "operator_review_required",
            staging_governance.get("operator_review_required") is True and rollback_governance.get("operator_review_required") is True,
            "Operator review is required by staging and rollback contracts.",
        ),
        "validation_required": gate_check(
            "validation_required",
            staging_governance.get("validation_required") is True or rollback_governance.get("validation_after_restore_required") is True,
            "Validation is required before update execution.",
        ),
        "rollback_required": gate_check(
            "rollback_required",
            staging_governance.get("rollback_required") is True and rollback_governance.get("rollback_plans_required") is True,
            "Rollback is required and rollback plans are required.",
        ),
        "automatic_execution_disabled_until_approved": gate_check(
            "automatic_execution_disabled_until_approved",
            latest_pack.get("automatic_execution_enabled") is False
            and latest_plan.get("automatic_execution_enabled") is False
            and staging_governance.get("automatic_execution_enabled") is False
            and rollback_governance.get("automatic_execution_enabled") is False,
            "Automatic execution is disabled by current staging and rollback contracts.",
        ),
    }

    if internet_readiness.get("automatic_updates_enabled") is True:
        checks["internet_readiness_checked"]["passed"] = False
        checks["internet_readiness_checked"]["detail"] = "Internet readiness says automatic updates are enabled before runner gate approval."
        checks["internet_readiness_checked"]["severity"] = "blocker"

    return checks


def determine_gate_state(checks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    blockers = [
        item["name"]
        for item in checks.values()
        if not item.get("passed") and item.get("severity") == "blocker"
    ]
    warnings = [
        item["name"]
        for item in checks.values()
        if not item.get("passed") and item.get("severity") == "warning"
    ]

    if blockers:
        status = "blocked"
    elif warnings:
        status = "warning"
    else:
        status = "gate_ready_but_execution_disabled"

    return {
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "all_checks_passed": not blockers and not warnings,
        "runner_can_execute_now": False,
        "automatic_execution_enabled": False,
        "manual_operator_approval_required": True,
    }


def build_automatic_update_runner_gate(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    staging, staging_source = read_json(root / STAGING_INDEX_PATH)
    rollback, rollback_source = read_json(root / ROLLBACK_INDEX_PATH)
    internet, internet_source = read_json(root / INTERNET_READINESS_PATH)

    latest_pack = latest_item(staging, "packs", "latest_pack")
    latest_plan = latest_item(rollback, "plans", "latest_plan")
    checks = build_checks(staging, rollback, internet)
    gate_state = determine_gate_state(checks)

    gate = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "sources": {
            "staging_index": staging_source,
            "rollback_index": rollback_source,
            "internet_readiness": internet_source,
        },
        "linked_update_pack": latest_pack,
        "linked_rollback_plan": latest_plan,
        "checks": checks,
        "gate_state": gate_state,
        "runner_contract": {
            "runner_registered": True,
            "runner_executes_updates": False,
            "runner_mode": "gate_only_no_execution",
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "background_execution_enabled": False,
            "requires_operator_approval_token": True,
            "requires_validation_gauntlet": True,
            "requires_rollback_plan": True,
            "requires_source_trust": True,
        },
        "blocked_operations": [
            "apply_update_pack",
            "execute_file_operations",
            "run_remote_code",
            "enable_background_updates",
            "bypass_operator_review",
            "bypass_rollback_plan",
            "bypass_validation",
        ],
        "governance": {
            "no_hidden_updates": True,
            "no_background_execution": True,
            "no_uncontrolled_self_modification": True,
            "operator_review_required": True,
            "rollback_required": True,
            "validation_required": True,
            "source_trust_required": True,
            "execution_still_disabled": True,
        },
        "next": [
            "v17.74 Update Governance Regression Lock",
            "v17.75 Full end-to-end proof pack",
        ],
    }

    write_json(root / RUNNER_GATE_PATH, gate)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": gate["generated_at"],
        "status": gate_state["status"],
        "blockers": gate_state["blockers"],
        "warnings": gate_state["warnings"],
        "runner_contract": gate["runner_contract"],
        "linked_update_pack": latest_pack,
        "linked_rollback_plan": latest_plan,
        "execution_enabled": False,
        "automatic_updates_enabled": False,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return gate


def automatic_update_runner_gate_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    gate = build_automatic_update_runner_gate(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": gate.get("gate_state", {}).get("status"),
        "blockers": gate.get("gate_state", {}).get("blockers", []),
        "warnings": gate.get("gate_state", {}).get("warnings", []),
        "runner_contract": gate.get("runner_contract"),
        "execution_enabled": False,
        "automatic_updates_enabled": False,
    }
