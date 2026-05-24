
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.74"
CONTRACT_NAME = "Update Governance Regression Lock"

STAGING_INDEX_PATH = Path("data/update_packs/update_pack_staging_index.json")
ROLLBACK_INDEX_PATH = Path("data/update_packs/rollback_plan_index.json")
RUNNER_GATE_PATH = Path("data/update_packs/automatic_update_runner_gate.json")
INTERNET_READINESS_PATH = Path("data/internet_readiness/internet_readiness_verification.json")

LOCK_PATH = Path("data/update_packs/update_governance_regression_lock.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/update_governance_regression_lock_payload.json")

FORBIDDEN_TRUE_FLAGS = [
    "execution_enabled",
    "automatic_execution_enabled",
    "background_execution_enabled",
    "runner_executes_updates",
    "automatic_updates_enabled",
    "live_internet_enabled",
]

REQUIRED_GOVERNANCE_TRUE_FLAGS = [
    "operator_review_required",
    "rollback_required",
    "validation_required",
    "source_trust_required",
]

REQUIRED_LOCK_INPUTS = [
    "staging_index",
    "rollback_index",
    "runner_gate",
    "internet_readiness",
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


def bool_at(payload: Dict[str, Any], path: List[str]) -> Optional[bool]:
    cur: Any = payload
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    if isinstance(cur, bool):
        return cur
    return None


def latest_item(index: Dict[str, Any], collection_key: str, latest_key: str) -> Dict[str, Any]:
    latest = index.get(latest_key)
    if isinstance(latest, dict):
        return latest
    items = index.get(collection_key)
    if isinstance(items, list) and items and isinstance(items[-1], dict):
        return items[-1]
    return {}


def collect_forbidden_flags(staging: Dict[str, Any], rollback: Dict[str, Any], runner: Dict[str, Any], internet: Dict[str, Any]) -> Dict[str, Any]:
    latest_pack = latest_item(staging, "packs", "latest_pack")
    latest_plan = latest_item(rollback, "plans", "latest_plan")
    runner_contract = runner.get("runner_contract") if isinstance(runner.get("runner_contract"), dict) else {}
    runner_state = runner.get("gate_state") if isinstance(runner.get("gate_state"), dict) else {}
    internet_readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}

    checks = {
        "staging_governance_execution_enabled": bool_at(staging, ["governance", "execution_enabled"]),
        "staging_governance_automatic_execution_enabled": bool_at(staging, ["governance", "automatic_execution_enabled"]),
        "latest_pack_execution_enabled": latest_pack.get("execution_enabled") if isinstance(latest_pack.get("execution_enabled"), bool) else None,
        "latest_pack_automatic_execution_enabled": latest_pack.get("automatic_execution_enabled") if isinstance(latest_pack.get("automatic_execution_enabled"), bool) else None,
        "rollback_governance_execution_enabled": bool_at(rollback, ["governance", "execution_enabled"]),
        "rollback_governance_automatic_execution_enabled": bool_at(rollback, ["governance", "automatic_execution_enabled"]),
        "latest_plan_execution_enabled": latest_plan.get("execution_enabled") if isinstance(latest_plan.get("execution_enabled"), bool) else None,
        "latest_plan_automatic_execution_enabled": latest_plan.get("automatic_execution_enabled") if isinstance(latest_plan.get("automatic_execution_enabled"), bool) else None,
        "runner_contract_runner_executes_updates": runner_contract.get("runner_executes_updates") if isinstance(runner_contract.get("runner_executes_updates"), bool) else None,
        "runner_contract_execution_enabled": runner_contract.get("execution_enabled") if isinstance(runner_contract.get("execution_enabled"), bool) else None,
        "runner_contract_automatic_execution_enabled": runner_contract.get("automatic_execution_enabled") if isinstance(runner_contract.get("automatic_execution_enabled"), bool) else None,
        "runner_contract_background_execution_enabled": runner_contract.get("background_execution_enabled") if isinstance(runner_contract.get("background_execution_enabled"), bool) else None,
        "runner_state_runner_can_execute_now": runner_state.get("runner_can_execute_now") if isinstance(runner_state.get("runner_can_execute_now"), bool) else None,
        "runner_state_automatic_execution_enabled": runner_state.get("automatic_execution_enabled") if isinstance(runner_state.get("automatic_execution_enabled"), bool) else None,
        "internet_readiness_live_internet_enabled": internet_readiness.get("live_internet_enabled") if isinstance(internet_readiness.get("live_internet_enabled"), bool) else None,
        "internet_readiness_automatic_updates_enabled": internet_readiness.get("automatic_updates_enabled") if isinstance(internet_readiness.get("automatic_updates_enabled"), bool) else None,
        "internet_readiness_safe_for_automatic_updates": internet_readiness.get("safe_for_automatic_updates") if isinstance(internet_readiness.get("safe_for_automatic_updates"), bool) else None,
    }

    violations = [
        name for name, value in checks.items()
        if value is True
    ]

    unknown = [
        name for name, value in checks.items()
        if value is None
    ]

    return {
        "checks": checks,
        "violations": violations,
        "unknown": unknown,
    }


def collect_required_governance(staging: Dict[str, Any], rollback: Dict[str, Any], runner: Dict[str, Any], internet: Dict[str, Any]) -> Dict[str, Any]:
    staging_g = staging.get("governance") if isinstance(staging.get("governance"), dict) else {}
    rollback_g = rollback.get("governance") if isinstance(rollback.get("governance"), dict) else {}
    runner_g = runner.get("governance") if isinstance(runner.get("governance"), dict) else {}
    internet_g = internet.get("governance") if isinstance(internet.get("governance"), dict) else {}

    checks = {
        "staging_operator_review_required": staging_g.get("operator_review_required") is True,
        "staging_rollback_required": staging_g.get("rollback_required") is True,
        "staging_validation_required": staging_g.get("validation_required") is True,
        "rollback_operator_review_required": rollback_g.get("operator_review_required") is True,
        "rollback_validation_after_restore_required": rollback_g.get("validation_after_restore_required") is True,
        "runner_operator_review_required": runner_g.get("operator_review_required") is True,
        "runner_rollback_required": runner_g.get("rollback_required") is True,
        "runner_validation_required": runner_g.get("validation_required") is True,
        "runner_source_trust_required": runner_g.get("source_trust_required") is True,
        "internet_source_trust_required": internet_g.get("source_trust_required") is True or internet_g.get("source_allowlist_required") is True,
        "internet_quarantine_required": internet_g.get("quarantine_required") is True,
    }

    missing = [name for name, passed in checks.items() if not passed]
    return {"checks": checks, "missing": missing}


def determine_lock_state(input_sources: Dict[str, Any], forbidden: Dict[str, Any], required: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    for name, source in input_sources.items():
        if source.get("status") != "loaded":
            blockers.append(f"missing_or_invalid_input:{name}")

    for violation in forbidden["violations"]:
        blockers.append(f"forbidden_true_flag:{violation}")

    for missing in required["missing"]:
        blockers.append(f"missing_required_governance:{missing}")

    if forbidden["unknown"]:
        warnings.append("some execution/governance flags were not explicitly present: " + ", ".join(forbidden["unknown"][:20]))

    if blockers:
        status = "locked_with_blockers"
    elif warnings:
        status = "locked_with_warnings"
    else:
        status = "locked_passed"

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "regression_lock_active": True,
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "background_execution_enabled": False,
        "automatic_updates_enabled": False,
    }


def build_update_governance_regression_lock(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    staging, staging_source = read_json(root / STAGING_INDEX_PATH)
    rollback, rollback_source = read_json(root / ROLLBACK_INDEX_PATH)
    runner, runner_source = read_json(root / RUNNER_GATE_PATH)
    internet, internet_source = read_json(root / INTERNET_READINESS_PATH)

    input_sources = {
        "staging_index": staging_source,
        "rollback_index": rollback_source,
        "runner_gate": runner_source,
        "internet_readiness": internet_source,
    }

    forbidden = collect_forbidden_flags(staging, rollback, runner, internet)
    required = collect_required_governance(staging, rollback, runner, internet)
    lock_state = determine_lock_state(input_sources, forbidden, required)

    lock = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "input_sources": input_sources,
        "lock_state": lock_state,
        "forbidden_execution_flags": forbidden,
        "required_governance_flags": required,
        "regression_rules": {
            "no_hidden_updates": True,
            "no_background_execution": True,
            "no_uncontrolled_self_modification": True,
            "no_update_execution_without_operator_review": True,
            "no_update_execution_without_rollback": True,
            "no_update_execution_without_validation": True,
            "no_update_execution_without_source_trust": True,
            "automatic_updates_remain_disabled": True,
            "internet_live_execution_remains_disabled": True,
        },
        "locked_endpoints": {
            "runner_gate": "/updates/runner-gate",
            "staging": "/updates/staging",
            "rollback_plan": "/updates/rollback-plan",
            "internet_readiness": "/internet/readiness",
        },
        "next": [
            "v17.75 Full end-to-end proof pack",
        ],
    }

    write_json(root / LOCK_PATH, lock)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": lock["generated_at"],
        "status": lock_state["status"],
        "blockers": lock_state["blockers"],
        "warnings": lock_state["warnings"],
        "regression_lock_active": True,
        "execution_enabled": False,
        "automatic_updates_enabled": False,
        "input_sources": input_sources,
        "regression_rules": lock["regression_rules"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return lock


def update_governance_regression_lock_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    lock = build_update_governance_regression_lock(project_root)
    state = lock.get("lock_state", {})
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": state.get("status"),
        "blockers": state.get("blockers", []),
        "warnings": state.get("warnings", []),
        "regression_lock_active": True,
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
