from __future__ import annotations

"""
Governed Payload Registry — S142-S148 compatibility owner.

This module is intentionally deterministic, read-only, and safe to import.
It provides a stable registry contract for dashboard/governance payload
sections without mutating runtime truth or executing network activity.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List


VERSION = "v19.89.8-S142-S148"
STAGE_RANGE = "S142-S148"


_REGISTRY: Dict[str, Dict[str, Any]] = {
    "dashboard_payload_bridge": {
        "owner": "claire.api.dashboard_payload_bridge",
        "authority": "backend_truth",
        "status": "active",
        "presentation_only": False,
        "protected": True,
    },
    "governed_payload_reconciliation": {
        "owner": "dashboard_payload_bridge",
        "authority": "governed_payload_contract",
        "status": "active",
        "presentation_only": True,
        "protected": True,
    },
    "governed_web_safety_activation": {
        "owner": "dashboard_payload_bridge",
        "authority": "web_governance_contract",
        "status": "active",
        "presentation_only": True,
        "protected": True,
    },
    "blocked_authority_modes": {
        "owner": "dashboard_payload_bridge",
        "authority": "safety_contract",
        "status": "active",
        "presentation_only": True,
        "protected": True,
    },
    "lifecycle_stages": {
        "owner": "dashboard_payload_bridge",
        "authority": "canonical_lifecycle_contract",
        "status": "active",
        "presentation_only": True,
        "protected": True,
    },
    "dashboard_panels": {
        "owner": "dashboard_payload_bridge",
        "authority": "cockpit_presentation_contract",
        "status": "active",
        "presentation_only": True,
        "protected": False,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_governed_payload_registry_s142_s148() -> Dict[str, Any]:
    """Return the canonical read-only registry contract."""
    return {
        "version": VERSION,
        "stage_range": STAGE_RANGE,
        "status": "ready",
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_enabled": False,
        "runtime_truth_write_allowed": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "created_at": _now(),
        "registry": deepcopy(_REGISTRY),
        "registry_keys": sorted(_REGISTRY.keys()),
    }


def build_payload_registry() -> Dict[str, Any]:
    """Compatibility alias used by earlier tests/installers."""
    return build_governed_payload_registry_s142_s148()


def get_governed_payload_registry() -> Dict[str, Any]:
    """Compatibility alias used by dashboard payload checks."""
    return build_governed_payload_registry_s142_s148()


def list_registered_payload_keys() -> List[str]:
    return sorted(_REGISTRY.keys())


def validate_governed_payload_registry(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Validate that core governed payload keys are present when a payload is supplied."""
    registry = build_governed_payload_registry_s142_s148()
    expected = registry["registry_keys"]
    present = sorted([key for key in expected if isinstance(payload, dict) and key in payload])
    missing = sorted([key for key in expected if isinstance(payload, dict) and key not in payload])

    return {
        "version": VERSION,
        "stage_range": STAGE_RANGE,
        "status": "validated" if not missing else "missing_keys",
        "ok": not missing,
        "ready": not missing,
        "expected_keys": expected,
        "present_keys": present,
        "missing_keys": missing,
        "runtime_truth_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "created_at": _now(),
    }


def build_s148_stop_gate(report_dir: str | None = None) -> Dict[str, Any]:
    registry = build_governed_payload_registry_s142_s148()
    checks = {
        "registry_ready": registry["ready"] is True,
        "backend_owns_truth": registry["backend_owns_truth"] is True,
        "safe_authority_flags": all(
            registry.get(flag) is False
            for flag in [
                "runtime_truth_mutation_enabled",
                "runtime_truth_write_allowed",
                "automatic_updates_enabled",
                "autonomous_execution_enabled",
                "live_web_execution_enabled",
                "network_request_performed",
            ]
        ),
        "registry_has_core_keys": len(registry["registry_keys"]) >= 6,
    }
    ok = all(checks.values())
    result = {
        "version": VERSION,
        "stage_range": STAGE_RANGE,
        "status": "governed_payload_registry_passed" if ok else "governed_payload_registry_failed",
        "ok": ok,
        "ready": ok,
        "checks": checks,
        "forward_motion_allowed": ok,
        "next_phase": "S450-S456 Claire Intelligence Answer Contract",
        "created_at": _now(),
    }

    if report_dir:
        from pathlib import Path
        import json

        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s148_governed_payload_registry_stop_gate.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )

    return result


__all__ = [
    "VERSION",
    "STAGE_RANGE",
    "build_governed_payload_registry_s142_s148",
    "build_payload_registry",
    "get_governed_payload_registry",
    "list_registered_payload_keys",
    "validate_governed_payload_registry",
    "build_s148_stop_gate",
]
