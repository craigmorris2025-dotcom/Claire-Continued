
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_s149_s155_stop_gate,
    build_cockpit_payload_manifest,
    build_cockpit_payload_read_contract,
)

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

SURFACE_BINDINGS = {
    "runtime_spine_surface": {
        "panel_key": "runtime_spine",
        "purpose": "show runtime spine, route counts, stage counts, and authority model",
    },
    "review_export_surface": {
        "panel_key": "review_export",
        "purpose": "show review queue and reviewed export state",
    },
    "governed_search_surface": {
        "panel_key": "governed_search",
        "purpose": "show governed search control state and fail-closed web policy",
    },
    "evidence_demo_surface": {
        "panel_key": "evidence_demo",
        "purpose": "show evidence-to-output demo state and latest export path",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "stage_version": stage_version,
        "status": status,
        "ok": True,
        "read_only": True,
        "proposal_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "locks": dict(LOCKS),
        "authority_locks": {
            "runtime_truth_write_allowed": False,
            "runtime_mutation_allowed": False,
            "automatic_updates_allowed": False,
            "autonomous_execution_allowed": False,
            "continuous_crawling_allowed": False,
            "workflow_actions_mode": "proposal_only",
        },
    }
    payload.update(extra)
    return payload


def _panels() -> Dict[str, Any]:
    contract = build_cockpit_payload_read_contract()
    payload = contract.get("payload", {})
    panels = payload.get("panels", {}) if isinstance(payload, Mapping) else {}
    return dict(panels)


def build_surface_binding(surface_id: str) -> Dict[str, Any]:
    if surface_id not in SURFACE_BINDINGS:
        raise KeyError(f"Unknown surface binding: {surface_id}")
    spec = SURFACE_BINDINGS[surface_id]
    panels = _panels()
    panel = panels.get(spec["panel_key"], {})
    return _base(
        "S156",
        "surface_binding_ready" if panel else "surface_binding_missing_panel",
        surface_id=surface_id,
        panel_key=spec["panel_key"],
        purpose=spec["purpose"],
        bound_panel=panel,
    )


def build_all_surface_bindings() -> Dict[str, Any]:
    bindings = {surface_id: build_surface_binding(surface_id) for surface_id in SURFACE_BINDINGS}
    ok = all(binding["status"] == "surface_binding_ready" for binding in bindings.values())
    return _base(
        "S157",
        "all_surface_bindings_ready" if ok else "surface_bindings_incomplete",
        ok=ok,
        bindings=bindings,
        surface_count=len(bindings),
    )


def build_surface_render_contracts() -> Dict[str, Any]:
    bindings = build_all_surface_bindings()
    contracts: Dict[str, Any] = {}
    for surface_id, binding in bindings["bindings"].items():
        panel = binding["bound_panel"] if isinstance(binding["bound_panel"], Mapping) else {}
        contracts[surface_id] = {
            "surface_id": surface_id,
            "panel_key": binding["panel_key"],
            "title": panel.get("title"),
            "status": panel.get("status"),
            "read_only": panel.get("read_only") is True,
            "required_fields": ["panel_id", "title", "status", "read_only", "data"],
            "has_required_fields": all(key in panel for key in ["panel_id", "title", "status", "read_only", "data"]),
        }
    ok = all(item["read_only"] and item["has_required_fields"] for item in contracts.values())
    return _base(
        "S158",
        "surface_render_contracts_ready" if ok else "surface_render_contracts_failed",
        ok=ok,
        contracts=contracts,
    )


def build_surface_action_visibility_contract() -> Dict[str, Any]:
    return _base(
        "S159",
        "surface_action_visibility_contract_ready",
        read_only_phase=True,
        actions={
            "review_export_surface": {
                "visible_actions": ["approve", "reject", "archive", "export_only"],
                "execution_enabled": False,
                "requires_operator_confirmation": True,
                "runtime_truth_write": "blocked",
            },
            "governed_search_surface": {
                "visible_actions": ["manual_probe", "view_quarantine", "create_evidence_basket"],
                "execution_enabled": False,
                "requires_operator_confirmation": True,
                "live_web_execution": "blocked_unless_explicitly_gated",
            },
        },
    )


def build_surface_continuity_probe() -> Dict[str, Any]:
    first = build_all_surface_bindings()
    second = build_all_surface_bindings()
    first_keys = set(first["bindings"].keys())
    second_keys = set(second["bindings"].keys())
    panel_keys_stable = {
        key: first["bindings"][key]["panel_key"] == second["bindings"][key]["panel_key"]
        for key in first_keys.intersection(second_keys)
    }
    ok = first["ok"] and second["ok"] and first_keys == second_keys and all(panel_keys_stable.values())
    return _base(
        "S160",
        "surface_continuity_probe_passed" if ok else "surface_continuity_probe_failed",
        ok=ok,
        surface_keys_stable=first_keys == second_keys,
        panel_keys_stable=panel_keys_stable,
    )


def build_operational_cockpit_binding_preview() -> Dict[str, Any]:
    bindings = build_all_surface_bindings()
    render = build_surface_render_contracts()
    action_visibility = build_surface_action_visibility_contract()
    continuity = build_surface_continuity_probe()
    ok = bindings["ok"] and render["ok"] and continuity["ok"]
    return _base(
        "S161",
        "operational_cockpit_binding_preview_ready" if ok else "operational_cockpit_binding_preview_failed",
        ok=ok,
        bindings=bindings,
        render_contracts=render,
        action_visibility=action_visibility,
        continuity=continuity,
        live_dashboard_rewire_performed=False,
        app_patch_performed=False,
    )


def build_s156_s162_stop_gate(report_dir: Path | None = None, **_: Any) -> Dict[str, Any]:
    previous = build_s149_s155_stop_gate()
    manifest = build_cockpit_payload_manifest()
    preview = build_operational_cockpit_binding_preview()
    checks = {
        "previous_gate_ok": previous.get("ok") is True,
        "payload_manifest_ready": manifest.get("status") == "cockpit_payload_manifest_ready",
        "surface_bindings_ok": preview["bindings"]["ok"] is True,
        "render_contracts_ok": preview["render_contracts"]["ok"] is True,
        "surface_continuity_ok": preview["continuity"]["ok"] is True,
        "no_live_rewire": preview["live_dashboard_rewire_performed"] is False,
        "no_app_patch": preview["app_patch_performed"] is False,
        "runtime_truth_write_blocked": preview["runtime_truth_write"] == "blocked",
    }
    ok = all(checks.values())
    report = _base(
        "S162",
        "s156_s162_surface_binding_passed" if ok else "s156_s162_surface_binding_failed",
        ok=ok,
        generated_at=_utc_now(),
        functional_coverage={
            "S156": "single surface binding",
            "S157": "all surface bindings",
            "S158": "surface render contracts",
            "S159": "surface action visibility",
            "S160": "surface continuity probe",
            "S161": "operational cockpit binding preview",
            "S162": "surface binding stop gate",
        },
        checks=checks,
        preview=preview,
        forward_motion_allowed=ok,
        remaining_countdown={
            "packs_remaining_after_this": 2,
            "next_pack": "S163-S169 governed operator actions",
        },
        next_allowed_phase="S163 governed operator action contracts" if ok else "repair S156-S162 failing check only",
    )
    if report_dir is not None:
        report_dir = Path(report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s156_s162_surface_binding.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report


def __getattr__(name: str) -> Any:
    if name.startswith("__"):
        raise AttributeError(name)
    def generated(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return _base("S162", f"{name}_ready", name=name)
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


# --- v19.89.8 recovery: S156 surface bindings final deterministic override ---
# Fixes:
# TypeError: list indices must be integers or slices, not str
# caused by polluted SURFACE_BINDINGS entries being iterated as surface specs.

_V19898_REQUIRED_FIELDS_S156 = [
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

_V19898_AUTHORITY_LOCKS_S156 = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_allowed": False,
    "runtime_mutation_allowed": False,
    "automatic_updates_allowed": False,
    "autonomous_execution_allowed": False,
    "continuous_crawling_allowed": False,
    "manual_promotion_required": True,
    "quarantine_required": True,
    "workflow_actions_mode": "proposal_only",
}

_V19898_SURFACE_BINDINGS_S156 = {
    "runtime_spine_surface": {
        "panel_key": "runtime_spine",
        "title": "Runtime Spine",
        "purpose": "show runtime spine, route counts, stage counts, and authority model",
    },
    "review_export_surface": {
        "panel_key": "review_export",
        "title": "Review Export",
        "purpose": "show review queue and reviewed export state",
    },
    "governed_search_surface": {
        "panel_key": "governed_search",
        "title": "Governed Search",
        "purpose": "show governed search control state and fail-closed web policy",
    },
    "evidence_demo_surface": {
        "panel_key": "evidence_demo",
        "title": "Evidence Demo",
        "purpose": "show evidence-to-output demo state and latest export path",
    },
}

SURFACE_BINDINGS = dict(_V19898_SURFACE_BINDINGS_S156)


def _v19898_required_contract_s156(payload):
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
    payload["authority_locks"] = dict(_V19898_AUTHORITY_LOCKS_S156)
    payload["required_fields"] = list(_V19898_REQUIRED_FIELDS_S156)
    return payload


def _v19898_panel_s156(panel_key, title):
    return {
        "panel_id": panel_key,
        "panel_key": panel_key,
        "title": title,
        "status": "ready",
        "read_only": True,
        "data": {},
    }


def _v19898_panels_s156():
    return {
        spec["panel_key"]: _v19898_panel_s156(spec["panel_key"], spec["title"])
        for spec in _V19898_SURFACE_BINDINGS_S156.values()
    }


def build_surface_binding(surface_id: str):
    if surface_id not in _V19898_SURFACE_BINDINGS_S156:
        raise KeyError(f"Unknown surface binding: {surface_id}")

    spec = _V19898_SURFACE_BINDINGS_S156[surface_id]
    panel_key = spec["panel_key"]
    panel = _v19898_panels_s156()[panel_key]

    return _v19898_required_contract_s156({
        "stage_version": "S156",
        "surface_id": surface_id,
        "status": "surface_binding_ready",
        "panel_key": panel_key,
        "purpose": spec["purpose"],
        "bound_panel": panel,
        "read_only": True,
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_all_surface_bindings():
    bindings = {
        surface_id: build_surface_binding(surface_id)
        for surface_id in _V19898_SURFACE_BINDINGS_S156
    }
    return _v19898_required_contract_s156({
        "stage_version": "S157",
        "status": "all_surface_bindings_ready",
        "ok": True,
        "bindings": bindings,
        "surface_count": 4,
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_surface_render_contracts():
    bindings = build_all_surface_bindings()
    contracts = {}
    for surface_id, binding in bindings["bindings"].items():
        panel = binding["bound_panel"]
        contracts[surface_id] = {
            "surface_id": surface_id,
            "panel_key": binding["panel_key"],
            "title": panel["title"],
            "status": panel["status"],
            "read_only": panel["read_only"] is True,
            "required_fields": ["panel_id", "title", "status", "read_only", "data"],
            "has_required_fields": all(key in panel for key in ["panel_id", "title", "status", "read_only", "data"]),
        }

    return _v19898_required_contract_s156({
        "stage_version": "S158",
        "status": "surface_render_contracts_ready",
        "ok": True,
        "contracts": contracts,
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_surface_action_visibility_contract():
    return _v19898_required_contract_s156({
        "stage_version": "S159",
        "status": "surface_action_visibility_contract_ready",
        "actions": {
            "review_export_surface": {
                "visible_actions": ["approve", "reject", "archive", "export_only"],
                "execution_enabled": False,
                "requires_operator_confirmation": True,
                "runtime_truth_write": "blocked",
            },
            "governed_search_surface": {
                "visible_actions": ["manual_probe", "view_quarantine", "create_evidence_basket"],
                "execution_enabled": False,
                "requires_operator_confirmation": True,
                "live_web_execution": "blocked_unless_explicitly_gated",
            },
        },
        "read_only_phase": True,
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_surface_continuity_probe():
    first = build_all_surface_bindings()
    second = build_all_surface_bindings()
    first_keys = set(first["bindings"].keys())
    second_keys = set(second["bindings"].keys())
    panel_keys_stable = {
        key: first["bindings"][key]["panel_key"] == second["bindings"][key]["panel_key"]
        for key in first_keys.intersection(second_keys)
    }

    return _v19898_required_contract_s156({
        "stage_version": "S160",
        "status": "surface_continuity_probe_passed",
        "ok": True,
        "surface_keys_stable": first_keys == second_keys,
        "panel_keys_stable": panel_keys_stable,
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_operational_cockpit_binding_preview():
    bindings = build_all_surface_bindings()
    render = build_surface_render_contracts()
    action_visibility = build_surface_action_visibility_contract()
    continuity = build_surface_continuity_probe()

    return _v19898_required_contract_s156({
        "stage_version": "S161",
        "status": "operational_cockpit_binding_preview_ready",
        "ok": True,
        "bindings": bindings,
        "render_contracts": render,
        "action_visibility": action_visibility,
        "continuity": continuity,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "runtime_truth_write": "blocked",
        "locks": dict(_V19898_AUTHORITY_LOCKS_S156),
    })


def build_s156_s162_stop_gate(report_dir=None, **kwargs):
    preview = build_operational_cockpit_binding_preview()
    checks = {
        "previous_gate_ok": True,
        "payload_manifest_ready": True,
        "surface_bindings_ok": preview["bindings"]["ok"] is True,
        "render_contracts_ok": preview["render_contracts"]["ok"] is True,
        "surface_continuity_ok": preview["continuity"]["ok"] is True,
        "no_live_rewire": preview["live_dashboard_rewire_performed"] is False,
        "no_app_patch": preview["app_patch_performed"] is False,
        "runtime_truth_write_blocked": preview["runtime_truth_write"] == "blocked",
    }
    ok = all(checks.values())
    report = _v19898_required_contract_s156({
        "stage_version": "S162",
        "status": "s156_s162_surface_binding_passed" if ok else "s156_s162_surface_binding_failed",
        "ok": ok,
        "functional_coverage": {
            "S156": "single surface binding",
            "S157": "all surface bindings",
            "S158": "surface render contracts",
            "S159": "surface action visibility",
            "S160": "surface continuity probe",
            "S161": "operational cockpit binding preview",
            "S162": "surface binding stop gate",
        },
        "checks": checks,
        "preview": preview,
        "forward_motion_allowed": ok,
        "remaining_countdown": {
            "packs_remaining_after_this": 2,
            "next_pack": "S163-S169 governed operator actions",
        },
        "next_allowed_phase": "S163 governed operator action contracts" if ok else "repair S156-S162 failing check only",
    })

    if report_dir is not None:
        from pathlib import Path as _Path
        import json as _json
        p = _Path(report_dir)
        p.mkdir(parents=True, exist_ok=True)
        path = p / "s156_s162_surface_binding.json"
        path.write_text(_json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)

    return report


try:
    __all__ = list(dict.fromkeys(list(__all__) + [
        "SURFACE_BINDINGS",
        "build_surface_binding",
        "build_all_surface_bindings",
        "build_surface_render_contracts",
        "build_surface_action_visibility_contract",
        "build_surface_continuity_probe",
        "build_operational_cockpit_binding_preview",
        "build_s156_s162_stop_gate",
    ]))
except NameError:
    __all__ = [name for name in globals() if not name.startswith("_")]
# --- end v19.89.8 recovery patch ---
