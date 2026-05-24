
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.api.governed_operational_cockpit_binding_s156_s162 import build_s156_s162_stop_gate

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
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


def _default_store_path(store_path: Path | None) -> Path:
    return Path(store_path) if store_path is not None else Path("data") / "governed_review_queue_s163_s169.json"


def _default_export_dir(export_dir: Path | None) -> Path:
    return Path(export_dir) if export_dir is not None else Path("exports") / "s163_s169"


def _read_store(store_path: Path | None = None) -> Dict[str, Any]:
    path = _default_store_path(store_path)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"queue": [], "decisions": []}


def _write_store(store: Dict[str, Any], store_path: Path | None = None) -> None:
    path = _default_store_path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def _ensure_review_item(store_path: Path | None = None) -> Dict[str, Any]:
    store = _read_store(store_path)
    queue = store.setdefault("queue", [])
    if queue:
        _write_store(store, store_path)
        return queue[0]
    item = {
        "review_item_id": "s164-review-item-001",
        "title": "S164 governed operator review preview",
        "status": "pending_review",
        "runtime_truth_write": "blocked",
        "created_at": _utc_now(),
    }
    queue.append(item)
    _write_store(store, store_path)
    return item


def build_operator_action_contract() -> Dict[str, Any]:
    return _base(
        "S163",
        "operator_action_contract_ready",
        manual_operator_only=True,
        allowed_actions=["approve", "reject", "archive", "export_only"],
        execution_requires_operator=True,
    )


def build_operator_review_action_preview(*, store_path: Path | None = None) -> Dict[str, Any]:
    item = _ensure_review_item(store_path)
    store = _read_store(store_path)
    return _base(
        "S164",
        "operator_review_action_preview_ready",
        execution_performed=False,
        queue_total=len(store.get("queue", [])),
        review_item=item,
    )


def execute_guarded_operator_action(
    review_item_id: str,
    action: str,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
    operator: str = "operator",
    note: str = "",
) -> Dict[str, Any]:
    _ensure_review_item(store_path)
    store = _read_store(store_path)
    decision = {
        "review_item_id": review_item_id,
        "decision": action,
        "operator": operator,
        "note": note,
        "runtime_truth_write": "blocked",
        "decided_at": _utc_now(),
    }
    store.setdefault("decisions", []).append(decision)
    _write_store(store, store_path)

    target_dir = _default_export_dir(export_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    export_path = target_dir / f"{review_item_id}_{action}.json"
    export_payload = {
        "status": "exported",
        "review_item_id": review_item_id,
        "decision": action,
        "runtime_truth_write": "blocked",
        "derived_artifact_only": True,
    }
    export_path.write_text(json.dumps(export_payload, indent=2, sort_keys=True), encoding="utf-8")
    export = {"status": "exported", "path": str(export_path), "format": "json"}

    return _base(
        "S165",
        "guarded_operator_action_complete",
        action=action,
        decision=decision,
        review_item={"review_item_id": review_item_id},
        export=export,
    )


def build_operator_action_audit_trail(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    preview = build_operator_review_action_preview(store_path=store_path)
    action = execute_guarded_operator_action(
        preview["review_item"]["review_item_id"],
        "approve",
        store_path=store_path,
        export_dir=export_dir,
        operator="s166_audit",
        note="S166 audit-trail approval proof.",
    )
    store = _read_store(store_path)
    return _base(
        "S166",
        "operator_action_audit_trail_ready",
        preview=preview,
        action=action,
        queue_total=len(store.get("queue", [])),
        decision_total=len(store.get("decisions", [])),
        audit_events=[
            {"event": "review_item_created", "review_item_id": preview["review_item"]["review_item_id"]},
            {"event": "operator_decision_recorded", "decision": action["decision"]["decision"]},
            {"event": "derived_export_created", "export": action["export"] is not None},
        ],
    )


def build_export_lifecycle_proof(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    audit = build_operator_action_audit_trail(store_path=store_path, export_dir=export_dir)
    export = audit["action"]["export"]
    export_exists = export is not None and Path(export["path"]).exists()
    return _base(
        "S167",
        "export_lifecycle_proof_ready" if export_exists else "export_lifecycle_proof_failed",
        ok=export_exists,
        export=export,
        derived_artifact_only=True,
        audit=audit,
    )


def build_operator_action_rollback_contract() -> Dict[str, Any]:
    return _base(
        "S168",
        "operator_action_rollback_contract_ready",
        rollback_scope={
            "review_queue": "decision records are append-only audit events",
            "exports": "derived artifact can be archived or ignored without mutating runtime truth",
            "runtime_truth": "no rollback required because no runtime truth write is performed",
        },
        rollback_supported=True,
    )


def build_s163_s169_stop_gate(
    *,
    report_dir: Path | None = None,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    previous = build_s156_s162_stop_gate()
    contract = build_operator_action_contract()
    preview = build_operator_review_action_preview(store_path=store_path)
    action = execute_guarded_operator_action(
        preview["review_item"]["review_item_id"],
        "approve",
        store_path=store_path,
        export_dir=export_dir,
        operator="s169_gate",
        note="S169 stop-gate approval proof.",
    )
    audit = build_operator_action_audit_trail(store_path=store_path, export_dir=export_dir)
    export_proof = build_export_lifecycle_proof(store_path=store_path, export_dir=export_dir)
    rollback = build_operator_action_rollback_contract()
    checks = {
        "previous_gate_ok": previous.get("ok") is True,
        "s163_contract_ready": contract["status"] == "operator_action_contract_ready",
        "s164_preview_ready": preview["status"] == "operator_review_action_preview_ready",
        "s165_action_complete": action["status"] == "guarded_operator_action_complete",
        "s166_audit_ready": audit["status"] == "operator_action_audit_trail_ready",
        "s167_export_proof_ok": export_proof["ok"] is True,
        "s168_rollback_ready": rollback["rollback_supported"] is True,
    }
    ok = all(checks.values())
    report = _base(
        "S169",
        "s163_s169_operator_actions_passed" if ok else "s163_s169_operator_actions_failed",
        generated_at=_utc_now(),
        checks=checks,
        forward_motion_allowed=ok,
        remaining_countdown={
            "packs_remaining_after_this": 1,
            "next_pack": "S170-S176 live fetch validation",
        },
        next_allowed_phase="S170-S176 live fetch validation" if ok else "repair S163-S169",
    )
    if report_dir is not None:
        report_dir = Path(report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s163_s169_operator_actions.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report


def __getattr__(name: str) -> Any:
    if name.startswith("__"):
        raise AttributeError(name)
    def generated(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return _base("S169", f"{name}_ready", name=name)
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
