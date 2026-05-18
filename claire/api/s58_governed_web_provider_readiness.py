from __future__ import annotations
from typing import Any

S58_VERSION = "v19.89.8-S58R1-R8"
PROVIDERS = ("google_search","metadata_head_probe","bounded_fetch_capsule","operator_triggered_probe","evidence_review_queue")

def _authority() -> dict[str, Any]:
    return {"backend_owns_truth": True, "cockpit_presentation_only": True, "presentation_only": True, "read_only": True, "runtime_truth_mutation_allowed": False, "runtime_truth_write_allowed": False, "operator_mutation_enabled": False, "automatic_updates_enabled": False, "autonomous_execution_enabled": False, "live_web_execution_enabled": False, "network_request_performed": False, "body_read_performed": False, "manual_promotion_required": True, "quarantine_required": True, "response_mode": "quarantined_read_only_artifact"}

def build_provider_readiness_manifest() -> dict[str, Any]:
    providers = []
    for provider in PROVIDERS:
        providers.append({"provider_id": provider, "state": "configured_fail_closed", "operator_trigger_required": True, "manual_approval_required": True, "quarantine_first": True, "dry_run_available": True, **_authority()})
    return {"version": S58_VERSION, "status": "provider_readiness_manifest_ready", "provider_count": len(providers), "providers": providers, **_authority(), "next_phase": "S59 controlled probe request contracts"}

def verify_provider_readiness_manifest() -> dict[str, Any]:
    manifest = build_provider_readiness_manifest()
    failures = []
    if manifest["provider_count"] != 5: failures.append("provider count mismatch")
    for provider in manifest["providers"]:
        if provider["network_request_performed"]: failures.append(provider["provider_id"] + " network performed")
        if provider["live_web_execution_enabled"]: failures.append(provider["provider_id"] + " live enabled")
        if not provider["quarantine_first"]: failures.append(provider["provider_id"] + " not quarantine first")
    return {"version": S58_VERSION, "verification_ok": failures == [], "failures": failures, "provider_count": manifest["provider_count"], **_authority()}

def build_s58r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_provider_readiness_manifest()
    return {"version": S58_VERSION, "status": "s58r1_r8_ready" if verification["verification_ok"] else "s58r1_r8_blocked", "ready": verification["verification_ok"], "manifest": build_provider_readiness_manifest(), "verification": verification, **_authority(), "next_phase": "S59 controlled probe request contracts"}

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
    # recursion recovery: wrapping disabled
    return fn


# recursion recovery: automatic payload wrapping disabled
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
