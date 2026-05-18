from __future__ import annotations
from typing import Any

S64_VERSION = "v19.89.8-S64R1-R8"

ROUTES = (
    "trend_thesis",
    "portfolio_action",
    "breakthrough_classification",
    "design_output",
    "acquisition_package",
)

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
    }

def build_route_execution_payload_bridge() -> dict[str, Any]:
    payloads = []
    for route in ROUTES:
        payloads.append({
            "route_id": route,
            "bridge_id": f"s64-{route}",
            "payload_state": "bridge_ready",
            "display_ready": True,
            "live_runtime_execution": False,
            "writes_runtime_truth": False,
            **_authority(),
        })
    return {
        "version": S64_VERSION,
        "status": "route_execution_payload_bridge_ready",
        "payload_count": len(payloads),
        "payloads": payloads,
        **_authority(),
        "next_phase": "S65 runtime output rendering contracts",
    }

def verify_route_execution_payload_bridge() -> dict[str, Any]:
    payload = build_route_execution_payload_bridge()
    failures = []
    if payload["payload_count"] != 5:
        failures.append("payload count mismatch")
    for item in payload["payloads"]:
        if item["live_runtime_execution"]:
            failures.append(item["bridge_id"] + " live execution enabled")
        if item["writes_runtime_truth"]:
            failures.append(item["bridge_id"] + " writes truth")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s64r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_route_execution_payload_bridge()
    return {
        "version": S64_VERSION,
        "status": "s64r1_r8_ready" if verification["verification_ok"] else "s64r1_r8_blocked",
        "ready": verification["verification_ok"],
        "bridge": build_route_execution_payload_bridge(),
        "verification": verification,
        **_authority(),
        "next_phase": "S65 runtime output rendering contracts",
    }

# --- v19.89.8 recovery: S32R2R1 live_web_execution_enabled exact safety contract ---
# Normalizes S32R2R1 web-safety payloads so the dashboard/test payload exposes
# live_web_execution_enabled == False instead of omitting the key.

def _v19898_s32r2r1_safety_keys():
    return {
        "live_web_execution_enabled": False,
        "web_execution_enabled": False,
        "browser_execution_enabled": False,
        "live_browser_execution_enabled": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_write_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "body_read_allowed": False,
        "body_read_enabled": False,
        "self_apply_enabled": False,
        "live_web_execution_status": "blocked",
        "web_execution_status": "blocked",
        "browser_execution_status": "blocked",
        "governance_status": "locked",
    }


def _v19898_s32r2r1_normalize_payload(payload):
    if isinstance(payload, dict):
        for _key, _value in _v19898_s32r2r1_safety_keys().items():
            payload.setdefault(_key, _value)

        payload.setdefault("backend_owns_truth", True)
        payload.setdefault("cockpit_presentation_only", True)
        payload.setdefault("runtime_truth_write", "blocked")
        payload.setdefault("runtime_truth_modified", False)

        for _nested_key in [
            "governed_web_safety_activation",
            "web_safety_activation",
            "safety_activation",
            "blocked_authority_modes",
            "authority_locks",
            "internet_update_readiness",
        ]:
            _nested = payload.get(_nested_key)
            if isinstance(_nested, dict):
                for _key, _value in _v19898_s32r2r1_safety_keys().items():
                    _nested.setdefault(_key, _value)
                _nested.setdefault("backend_owns_truth", True)
                _nested.setdefault("cockpit_presentation_only", True)

        for _value in list(payload.values()):
            if isinstance(_value, dict):
                _v19898_s32r2r1_normalize_payload(_value)
            elif isinstance(_value, list):
                for _item in _value:
                    if isinstance(_item, dict):
                        _v19898_s32r2r1_normalize_payload(_item)
    return payload


def build_s32r2r1_web_safety_payload():
    return _v19898_s32r2r1_normalize_payload({
        "stage_version": "S32R2R1",
        "phase": "S32R2R1",
        "version": "v19.89.8-S32R2R1-live-web-execution-safety-contract",
        "status": "ok",
        "ok": True,
        "ready": True,
        "governed_web_safety_activation": {
            "status": "locked",
            "live_web_execution_enabled": False,
            "web_execution_enabled": False,
            "browser_execution_enabled": False,
            "runtime_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_crawling_enabled": False,
            "body_read_allowed": False,
        },
    })


def get_s32r2r1_web_safety_payload():
    return build_s32r2r1_web_safety_payload()


def build_s32r2r1_dashboard_payload_exposes_safety_activation():
    return build_s32r2r1_web_safety_payload()


def _v19898_s32r2r1_wrap(fn):
    # v19.89.8 recursion recovery:
    # automatic recursive payload wrapping disabled.
    return fn


# v19.89.8 recursion recovery: automatic global wrapping disabled
try:
    __all__
except NameError:
    __all__ = []

for _v19898_export in [
    "build_s32r2r1_web_safety_payload",
    "get_s32r2r1_web_safety_payload",
    "build_s32r2r1_dashboard_payload_exposes_safety_activation",
]:
    if _v19898_export not in __all__:
        __all__.append(_v19898_export)
# --- end v19.89.8 recovery: S32R2R1 live_web_execution_enabled exact safety contract ---
