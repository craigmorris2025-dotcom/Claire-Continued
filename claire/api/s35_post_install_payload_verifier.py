from __future__ import annotations

"""
S35 Post-Install Payload Verifier.

Safe read-only verifier for the Claire dashboard payload bridge.
This replacement removes legacy recursive global wrapper behavior and never
monkey-patches module globals.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


VERSION = "v19.89.8-S35"


REQUIRED_PAYLOAD_KEYS: List[str] = [
    "governed_payload_reconciliation",
    "governed_web_safety_activation",
    "controlled_read_only_provider_probe_gate",
    "controlled_metadata_probe_executor",
    "explicit_one_shot_metadata_probe_runner",
    "operator_triggered_metadata_probe_endpoint",
    "blocked_authority_modes",
    "lifecycle_stages",
    "dashboard_panels",
]


FALSE_AUTHORITY_FLAGS: List[str] = [
    "live_web_execution_enabled",
    "autonomous_agent_execution_enabled",
    "runtime_truth_mutation_enabled",
    "automatic_updates_enabled",
    "network_request_performed",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_dashboard_payload() -> Dict[str, Any]:
    from claire.api.dashboard_payload_bridge import get_dashboard_payload

    payload = get_dashboard_payload()
    if not isinstance(payload, dict):
        raise TypeError("dashboard payload bridge did not return a dict")
    return payload


def verify_dashboard_payload(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Verify dashboard payload shape without mutating it."""
    active_payload = payload if isinstance(payload, dict) else _load_dashboard_payload()

    missing = [key for key in REQUIRED_PAYLOAD_KEYS if key not in active_payload]
    unsafe_flags = {
        key: active_payload.get(key)
        for key in FALSE_AUTHORITY_FLAGS
        if active_payload.get(key) is not False
    }

    stages = active_payload.get("lifecycle_stages") or active_payload.get("stages") or []
    lifecycle_count = len(stages) if isinstance(stages, list) else 0

    checks = {
        "payload_is_dict": isinstance(active_payload, dict),
        "required_keys_present": not missing,
        "authority_flags_false": not unsafe_flags,
        "lifecycle_has_30_stages": lifecycle_count == 30,
    }

    ok = all(checks.values())
    return {
        "version": VERSION,
        "stage": "S35",
        "status": "payload_verified" if ok else "payload_verification_failed",
        "ok": ok,
        "ready": ok,
        "checks": checks,
        "missing_keys": missing,
        "unsafe_flags": unsafe_flags,
        "lifecycle_stage_count": lifecycle_count,
        "payload_key_count": len(active_payload),
        "runtime_truth_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "created_at": _now(),
    }


def build_s35_post_install_payload_verifier_status(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return verify_dashboard_payload(payload)


def build_s35_post_install_payload_verifier(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return verify_dashboard_payload(payload)


def get_s35_post_install_payload_verifier_status(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return verify_dashboard_payload(payload)


def build_s35_stop_gate(report_dir: str | None = None) -> Dict[str, Any]:
    result = verify_dashboard_payload()
    result["forward_motion_allowed"] = bool(result["ok"])

    if report_dir:
        from pathlib import Path
        import json

        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s35_post_install_payload_verifier_stop_gate.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

    return result


__all__ = [
    "VERSION",
    "REQUIRED_PAYLOAD_KEYS",
    "FALSE_AUTHORITY_FLAGS",
    "verify_dashboard_payload",
    "build_s35_post_install_payload_verifier_status",
    "build_s35_post_install_payload_verifier",
    "get_s35_post_install_payload_verifier_status",
    "build_s35_stop_gate",
]
