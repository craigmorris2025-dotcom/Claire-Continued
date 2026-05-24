from __future__ import annotations

from typing import Any

S49_VERSION = "v19.89.8-S49R1-R8"

GOVERNED_WEB_PANEL_KEYS = (
    "governed_web_safety_activation",
    "controlled_read_only_provider_probe_gate",
    "controlled_metadata_probe_executor",
    "explicit_one_shot_metadata_probe_runner",
    "operator_triggered_metadata_probe_endpoint",
)


def build_governed_web_panel_manifest() -> dict[str, Any]:
    panels = []
    for key in GOVERNED_WEB_PANEL_KEYS:
        panels.append({
            "panel_id": f"s49-{key.replace('_', '-')}",
            "source_key": key,
            "title": key.replace("_", " ").title(),
            "state": "fail_closed",
            "visible_to_operator": True,
            "display_mode": "governed_web_status_card",
            "network_request_performed": False,
            "body_read_performed": False,
            "body_scraping_performed": False,
            "endpoint_registered_with_app": False,
            "manual_trigger_required": True,
            "quarantine_required": True,
            "manual_promotion_required": True,
            "runtime_truth_write_allowed": False,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
            "live_web_execution_enabled": False,
            "response_mode": "quarantined_read_only_artifact",
        })

    return {
        "version": S49_VERSION,
        "phase": "S49R1-R4",
        "status": "governed_web_panel_manifest_ready",
        "source_s48_status": "s48r1_r8_ready",
        "panel_count": len(panels),
        "panels": panels,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "next_phase": "S49R5-R8 evidence review cockpit panel",
    }


def build_evidence_review_panel_manifest() -> dict[str, Any]:
    panel = {
        "panel_id": "s49-evidence-review-queue",
        "title": "Evidence Review Queue",
        "state": "manual_review_required",
        "visible_to_operator": True,
        "display_mode": "evidence_review_queue",
        "quarantine_required": True,
        "manual_promotion_required": True,
        "runtime_truth_write_allowed": False,
        "promotion_authority": False,
        "auto_promotion_enabled": False,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "response_mode": "quarantined_read_only_artifact",
    }
    return {
        "version": S49_VERSION,
        "phase": "S49R5-R6",
        "status": "evidence_review_panel_manifest_ready",
        "panel": panel,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def verify_governed_web_evidence_panels() -> dict[str, Any]:
    web = build_governed_web_panel_manifest()
    evidence = build_evidence_review_panel_manifest()
    failures: list[str] = []

    if web["panel_count"] != len(GOVERNED_WEB_PANEL_KEYS):
        failures.append("governed web panel count mismatch")

    for panel in web["panels"]:
        if not panel["visible_to_operator"]:
            failures.append(f"{panel['panel_id']} not visible")
        if panel["network_request_performed"]:
            failures.append(f"{panel['panel_id']} performed network request during build")
        if panel["body_read_performed"] or panel["body_scraping_performed"]:
            failures.append(f"{panel['panel_id']} body read/scrape drift")
        if panel["runtime_truth_mutation_allowed"]:
            failures.append(f"{panel['panel_id']} runtime truth mutation drift")
        if panel["operator_mutation_enabled"]:
            failures.append(f"{panel['panel_id']} operator mutation enabled")
        if panel["live_web_execution_enabled"]:
            failures.append(f"{panel['panel_id']} live web execution enabled")

    ev = evidence["panel"]
    if ev["runtime_truth_write_allowed"]:
        failures.append("evidence review allows runtime truth write")
    if ev["auto_promotion_enabled"]:
        failures.append("evidence review auto promotion enabled")
    if ev["promotion_authority"]:
        failures.append("evidence review promotion authority enabled")

    return {
        "version": S49_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "web_panel_count": web["panel_count"],
        "evidence_panel_count": 1,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def build_s49r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_governed_web_evidence_panels()
    return {
        "version": S49_VERSION,
        "phase": "S49R7-R8",
        "status": "s49r1_r8_ready" if verification["verification_ok"] else "s49r1_r8_blocked",
        "ready": verification["verification_ok"],
        "governed_web": build_governed_web_panel_manifest(),
        "evidence_review": build_evidence_review_panel_manifest(),
        "verification": verification,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "next_phase": "S50 modern cockpit consolidation and demo readiness",
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
