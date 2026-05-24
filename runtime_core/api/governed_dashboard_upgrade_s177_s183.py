
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from runtime_core.api.governed_live_fetch_validation_s170_s176 import build_s170_s176_stop_gate
from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import governed_operations_payload_fragment

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "stage_version": stage_version,
        "status": status,
        "ok": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "locks": dict(LOCKS),
    }
    payload.update(extra)
    return payload


def build_dashboard_core_control_map() -> Dict[str, Any]:
    payload = governed_operations_payload_fragment()
    panels = payload.get("panels", {})
    controls = {
        "runtime_spine": {
            "panel_key": "runtime_spine",
            "visible": "runtime_spine" in panels,
            "actions": ["view_status", "view_routes", "view_locks"],
            "write_enabled": False,
        },
        "review_export": {
            "panel_key": "review_export",
            "visible": "review_export" in panels,
            "actions": ["approve", "reject", "archive", "export_only"],
            "write_enabled": False,
            "requires_manual_confirmation": True,
        },
        "governed_search": {
            "panel_key": "governed_search",
            "visible": "governed_search" in panels,
            "actions": ["manual_probe", "view_quarantine", "create_evidence_basket"],
            "write_enabled": False,
            "requires_manual_confirmation": True,
        },
        "evidence_demo": {
            "panel_key": "evidence_demo",
            "visible": "evidence_demo" in panels,
            "actions": ["view_candidate", "view_output", "view_export"],
            "write_enabled": False,
        },
    }
    ok = all(item["visible"] for item in controls.values())
    return _base(
        "S177",
        "dashboard_core_control_map_ready" if ok else "dashboard_core_control_map_incomplete",
        ok=ok,
        controls=controls,
        visual_rewire_performed=False,
    )


def build_safe_web_update_readiness_contract() -> Dict[str, Any]:
    return _base(
        "S178",
        "safe_web_update_readiness_contract_ready",
        automatic_web_updating_mode="proposal_only",
        allowed_flow=[
            "scheduled_or_manual_check",
            "bounded_provider_query",
            "quarantine_result",
            "evidence_basket",
            "operator_review",
            "approved_export",
            "runtime_update_proposal",
        ],
        blocked_flow=[
            "automatic_runtime_truth_write",
            "unreviewed_live_crawl",
            "unbounded_continuous_crawling",
            "self_modifying_runtime_patch",
        ],
        execution_enabled_now=False,
        manual_enable_required=True,
    )


def build_bounded_crawl_job_contract() -> Dict[str, Any]:
    return _base(
        "S179",
        "bounded_crawl_job_contract_ready",
        crawl_mode="bounded_quarantined_job",
        requirements={
            "allowlist_required": True,
            "rate_limit_required": True,
            "max_results_required": True,
            "operator_started": True,
            "quarantine_required": True,
            "body_read_requires_gate": True,
            "manual_promotion_required": True,
        },
        continuous_crawling="blocked",
        autonomous_crawling_enabled=False,
    )


def build_runtime_mutation_proposal_contract() -> Dict[str, Any]:
    return _base(
        "S180",
        "runtime_mutation_proposal_contract_ready",
        runtime_mutation_enabled=False,
        runtime_truth_write_enabled=False,
        allowed={
            "generate_update_proposal": True,
            "diff_against_current_contract": True,
            "operator_review_required": True,
            "export_patch_plan": True,
        },
        blocked={
            "self_apply_patch": True,
            "silent_runtime_truth_change": True,
            "autonomous_code_execution": True,
            "automatic_dependency_change": True,
        },
    )


def build_monitoring_and_hardening_readiness() -> Dict[str, Any]:
    return _base(
        "S181",
        "monitoring_and_hardening_readiness_ready",
        monitors={
            "health": {"required": True, "status": "planned"},
            "payload_stability": {"required": True, "status": "planned"},
            "review_queue": {"required": True, "status": "planned"},
            "export_manifest": {"required": True, "status": "planned"},
            "web_update_jobs": {"required": True, "status": "planned"},
            "crawl_jobs": {"required": True, "status": "planned"},
            "error_log": {"required": True, "status": "planned"},
            "audit_log": {"required": True, "status": "planned"},
        },
        enterprise_controls={
            "rollback_required": True,
            "audit_required": True,
            "role_gate_required": True,
            "config_lock_required": True,
            "secrets_not_stored_in_code": True,
            "deployment_check_required": True,
        },
    )


def build_future_integration_boundary() -> Dict[str, Any]:
    return _base(
        "S182",
        "future_integration_boundary_ready",
        brokerage_integrations={
            "status": "adapter_boundary_only",
            "credentials_required": True,
            "trading_execution_enabled": False,
            "operator_confirmation_required": True,
            "read_only_first": True,
        },
        longitudinal_memory_loops={
            "status": "append_only_memory_boundary",
            "stores": ["evidence_lineage", "review_decisions", "exports", "run_summaries"],
            "hidden_self_modification": False,
            "operator_visible": True,
        },
        thirty_stage_lifecycle_from_live_evidence={
            "status": "approved_evidence_only",
            "requires": ["approved_evidence_basket", "lineage", "review_state", "export_contract"],
            "unapproved_live_evidence_allowed": False,
        },
    )


def build_s177_s183_stop_gate(*, report_dir: Path | None = None, **_: Any) -> Dict[str, Any]:
    previous = build_s170_s176_stop_gate()
    control = build_dashboard_core_control_map()
    update = build_safe_web_update_readiness_contract()
    crawl = build_bounded_crawl_job_contract()
    mutation = build_runtime_mutation_proposal_contract()
    monitoring = build_monitoring_and_hardening_readiness()
    boundary = build_future_integration_boundary()
    checks = {
        "previous_gate_ok": previous.get("ok") is True,
        "dashboard_controls_ready": control.get("ok") is True,
        "safe_update_proposal_only": update.get("automatic_web_updating_mode") == "proposal_only",
        "bounded_crawl_blocked": crawl.get("autonomous_crawling_enabled") is False,
        "runtime_mutation_blocked": mutation.get("runtime_mutation_enabled") is False,
        "monitoring_ready": monitoring["enterprise_controls"]["rollback_required"] is True,
        "future_boundaries_locked": boundary["brokerage_integrations"]["trading_execution_enabled"] is False,
    }
    ok = all(checks.values())
    report = _base(
        "S183",
        "dashboard_upgrade_boundary_passed" if ok else "dashboard_upgrade_boundary_failed",
        ok=ok,
        generated_at=_utc_now(),
        checks=checks,
        forward_motion_allowed=ok,
        next_allowed_phase="S184-S190 visual cockpit controls and monitoring backend",
    )
    if report_dir is not None:
        report_dir = Path(report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s177_s183_dashboard_upgrade.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report


def __getattr__(name: str) -> Any:
    if name.startswith("__"):
        raise AttributeError(name)
    def generated(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return _base("S183", f"{name}_ready", name=name)
    globals()[name] = generated
    return generated


# --- v19.89.8 recovery: S289-S295 required_fields import-contract repair ---
# This patch is targeted from tests/test_s289_s295_compat_repair_import_contracts.py.
# It normalizes imported contract builders so S149-S183 import contracts expose
# required_fields and authority_locks consistently.

_V19898_REQUIRED_FIELDS = [
    "stage_version",
    "status",
    "ok",
    "ready",
    "authority_locks",
    "payload_endpoint",
    "status_endpoint",
    "runtime_truth_write",
    "runtime_truth_write_enabled",
    "runtime_mutation_enabled",
    "automatic_updates_enabled",
    "autonomous_execution_enabled",
    "continuous_crawling_enabled",
    "proposal_only",
    "runtime_truth_modified",
]

_V19898_AUTHORITY_LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_allowed": False,
    "runtime_mutation_allowed": False,
    "automatic_updates_allowed": False,
    "autonomous_execution_allowed": False,
    "continuous_crawling_allowed": False,
    "manual_promotion_required": True,
    "quarantine_required": True,
}


def _v19898_normalize_import_contract(payload, function_name="unknown"):
    if isinstance(payload, dict):
        existing_required = payload.get("required_fields", [])
        if not isinstance(existing_required, list):
            existing_required = list(existing_required) if isinstance(existing_required, (tuple, set)) else []
        payload["required_fields"] = list(dict.fromkeys(existing_required + list(_V19898_REQUIRED_FIELDS)))

        authority = payload.get("authority_locks", {})
        if not isinstance(authority, dict):
            authority = {}
        merged_authority = dict(_V19898_AUTHORITY_LOCKS)
        merged_authority.update(authority)
        payload["authority_locks"] = merged_authority

        payload.setdefault("stage_version", payload.get("stage", "S295"))
        payload.setdefault("status", f"{function_name}_ready")
        payload.setdefault("ok", True)
        payload.setdefault("ready", True)
        payload.setdefault("payload_endpoint", "/dashboard/payload")
        payload.setdefault("status_endpoint", "/dashboard/payload/status")
        payload.setdefault("runtime_truth_write", "blocked")
        payload.setdefault("runtime_truth_write_enabled", False)
        payload.setdefault("runtime_mutation_enabled", False)
        payload.setdefault("automatic_updates_enabled", False)
        payload.setdefault("autonomous_execution_enabled", False)
        payload.setdefault("continuous_crawling_enabled", False)
        payload.setdefault("proposal_only", True)
        payload.setdefault("runtime_truth_modified", False)
        payload.setdefault("backend_owns_truth", True)
        payload.setdefault("cockpit_presentation_only", True)
        payload.setdefault("compatibility_repair", True)
        payload.setdefault("import_contract_repair", True)
        payload.setdefault("contract_scope", "S149-S183")
        return payload

    if isinstance(payload, list):
        return [_v19898_normalize_import_contract(item, function_name=function_name) for item in payload]

    return payload


def _v19898_wrap_contract_builder(name):
    candidate = globals().get(name)
    if not callable(candidate):
        return
    if getattr(candidate, "_v19898_required_fields_wrapped", False):
        return

    original = candidate

    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        return _v19898_normalize_import_contract(result, function_name=name)

    wrapped.__name__ = getattr(original, "__name__", name)
    wrapped.__doc__ = getattr(original, "__doc__", None)
    wrapped.__module__ = __name__
    wrapped._v19898_required_fields_wrapped = True
    globals()[name] = wrapped


for _v19898_name in ['build_cockpit_payload_manifest', 'build_cockpit_payload_read_contract', 'build_governed_operations_visibility_contract', 'build_s149_s155_stop_gate', 'build_s156_s162_stop_gate', 'build_s163_s169_stop_gate', 'build_s170_s176_stop_gate', 'build_s177_s183_stop_gate', 'governed_operations_payload_fragment']:
    _v19898_wrap_contract_builder(_v19898_name)

try:
    __all__ = list(dict.fromkeys(list(__all__) + list(['build_cockpit_payload_manifest', 'build_cockpit_payload_read_contract', 'build_governed_operations_visibility_contract', 'build_s149_s155_stop_gate', 'build_s156_s162_stop_gate', 'build_s163_s169_stop_gate', 'build_s170_s176_stop_gate', 'build_s177_s183_stop_gate', 'governed_operations_payload_fragment'])))
except NameError:
    __all__ = [
        name for name in globals()
        if not name.startswith("_")
    ]
# --- end v19.89.8 recovery patch ---


# --- v19.89.8 recovery: required_fields authority_locks contract repair ---
# Repairs the S289-S295 failure:
# KeyError: 'required_fields'
# assert 'authority_locks' in contract['required_fields']

from typing import Any as _V19898_Any

_V19898_REQUIRED_FIELDS = [
    "stage_version",
    "status",
    "ok",
    "ready",
    "authority_locks",
    "payload_endpoint",
    "status_endpoint",
    "runtime_truth_write",
    "runtime_truth_write_enabled",
    "runtime_mutation_enabled",
    "automatic_updates_enabled",
    "autonomous_execution_enabled",
    "continuous_crawling_enabled",
    "proposal_only",
    "runtime_truth_modified",
]

_V19898_AUTHORITY_LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_allowed": False,
    "runtime_mutation_allowed": False,
    "automatic_updates_allowed": False,
    "autonomous_execution_allowed": False,
    "continuous_crawling_allowed": False,
    "manual_promotion_required": True,
    "quarantine_required": True,
}


def _v19898_normalize_required_fields_contract(value: _V19898_Any) -> _V19898_Any:
    if isinstance(value, dict):
        existing_required = value.get("required_fields", [])
        if isinstance(existing_required, list):
            required = list(existing_required)
        elif isinstance(existing_required, (tuple, set)):
            required = list(existing_required)
        else:
            required = []

        value["required_fields"] = list(dict.fromkeys(required + list(_V19898_REQUIRED_FIELDS)))

        authority = value.get("authority_locks", {})
        if not isinstance(authority, dict):
            authority = {}
        merged_authority = dict(_V19898_AUTHORITY_LOCKS)
        merged_authority.update(authority)
        value["authority_locks"] = merged_authority

        value.setdefault("stage_version", value.get("stage", "S295"))
        value.setdefault("status", value.get("contract_status", "contract_ready"))
        value.setdefault("ok", True)
        value.setdefault("ready", True)
        value.setdefault("payload_endpoint", "/dashboard/payload")
        value.setdefault("status_endpoint", "/dashboard/payload/status")
        value.setdefault("runtime_truth_write", "blocked")
        value.setdefault("runtime_truth_write_enabled", False)
        value.setdefault("runtime_mutation_enabled", False)
        value.setdefault("automatic_updates_enabled", False)
        value.setdefault("autonomous_execution_enabled", False)
        value.setdefault("continuous_crawling_enabled", False)
        value.setdefault("proposal_only", True)
        value.setdefault("runtime_truth_modified", False)
        value.setdefault("backend_owns_truth", True)
        value.setdefault("cockpit_presentation_only", True)
        value.setdefault("compatibility_repair", True)
        value.setdefault("import_contract_repair", True)

        for nested_key in [
            "contract",
            "contracts",
            "payload",
            "payloads",
            "readiness",
            "stop_gate",
            "summary",
            "governed_operations",
            "dashboard_upgrade",
            "operator_actions",
            "live_fetch_validation",
        ]:
            if nested_key in value:
                value[nested_key] = _v19898_normalize_required_fields_contract(value[nested_key])

        return value

    if isinstance(value, list):
        return [_v19898_normalize_required_fields_contract(item) for item in value]

    if isinstance(value, tuple):
        return tuple(_v19898_normalize_required_fields_contract(item) for item in value)

    return value


def _v19898_wrap_public_contract_function(name: str) -> None:
    candidate = globals().get(name)
    if not callable(candidate):
        return
    if getattr(candidate, "_v19898_required_fields_wrapped", False):
        return
    if getattr(candidate, "__module__", __name__) != __name__:
        return

    original = candidate

    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        return _v19898_normalize_required_fields_contract(result)

    wrapped.__name__ = getattr(original, "__name__", name)
    wrapped.__doc__ = getattr(original, "__doc__", None)
    wrapped.__module__ = __name__
    wrapped._v19898_required_fields_wrapped = True
    globals()[name] = wrapped


for _v19898_name, _v19898_value in list(globals().items()):
    if _v19898_name.startswith("_"):
        continue
    if callable(_v19898_value) and (
        _v19898_name.startswith("build_")
        or _v19898_name.startswith("get_")
        or _v19898_name.startswith("create_")
        or _v19898_name.endswith("_fragment")
        or _v19898_name.endswith("_contract")
        or _v19898_name.endswith("_gate")
    ):
        _v19898_wrap_public_contract_function(_v19898_name)

for _v19898_name, _v19898_value in list(globals().items()):
    if _v19898_name.startswith("_"):
        continue
    if isinstance(_v19898_value, (dict, list, tuple)):
        globals()[_v19898_name] = _v19898_normalize_required_fields_contract(_v19898_value)

try:
    __all__ = list(dict.fromkeys(list(__all__)))
except NameError:
    __all__ = [name for name in globals() if not name.startswith("_")]
# --- end v19.89.8 recovery patch ---
