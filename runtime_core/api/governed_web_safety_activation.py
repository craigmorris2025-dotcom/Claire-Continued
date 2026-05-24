"""
S32R2R1 — Governed Web Safety Activation.

Authoritative full replacement.

This module is deliberately non-recursive and fail-closed. It performs no
network call and enables no live web execution, autonomous agent execution,
runtime mutation, automatic updates, crawling, body reads, or self-apply.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


PHASE = "S32R2R1"
VERSION = "v19.89.8-S32R2R1-authoritative-full-replacement"

FALSE_FLAGS: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "web_execution_enabled": False,
    "browser_execution_enabled": False,
    "live_browser_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "autonomous_agents_enabled": False,
    "agent_execution_enabled": False,
    "runtime_truth_mutation_enabled": False,
    "runtime_mutation_enabled": False,
    "runtime_truth_write_enabled": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "continuous_crawling_enabled": False,
    "body_read_allowed": False,
    "body_read_enabled": False,
    "self_apply_enabled": False,
    "network_request_performed": False,
    "network_performed": False,
    "network_call_performed": False,
    "provider_probe_performed": False,
    "live_probe_performed": False,
}

STATUS_FLAGS: Dict[str, str] = {
    "live_web_execution_status": "blocked",
    "web_execution_status": "blocked",
    "browser_execution_status": "blocked",
    "autonomous_agent_execution_status": "blocked",
    "runtime_truth_mutation_status": "blocked",
    "runtime_mutation_status": "blocked",
    "runtime_truth_write_status": "blocked",
    "automatic_updates_status": "blocked",
    "autonomous_crawling_status": "blocked",
    "continuous_crawling_status": "blocked",
    "body_read_status": "blocked",
    "self_apply_status": "blocked",
    "governance_status": "locked",
}

AUTHORITY: Dict[str, str] = {
    "browser_execution_authority": "blocked",
    "runtime_authority": "blocked",
    "runtime_truth_mutation": "blocked",
    "live_web_execution": "blocked",
    "autonomous_agent_execution": "blocked",
    "automatic_updates": "blocked",
    "body_read": "blocked",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safety_key_contract() -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    payload.update(FALSE_FLAGS)
    payload.update(STATUS_FLAGS)
    return payload


def authority_contract() -> Dict[str, str]:
    return dict(AUTHORITY)


def authority_locks_contract() -> Dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "live_web_execution_allowed": False,
        "web_execution_allowed": False,
        "browser_execution_allowed": False,
        "autonomous_agent_execution_allowed": False,
        "runtime_truth_write_allowed": False,
        "runtime_mutation_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "automatic_updates_allowed": False,
        "autonomous_crawling_allowed": False,
        "continuous_crawling_allowed": False,
        "body_read_allowed": False,
        "self_apply_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def build_governed_web_safety_activation() -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": PHASE,
        "phase": PHASE,
        "version": VERSION,
        "status": "locked",
        "ok": True,
        "ready": True,
        "created_at": _now(),
        "activation_state": "governed_locked",
        "activation_ready": True,
        "safe_to_display": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_modified": False,
        "authority": authority_contract(),
        "authority_locks": authority_locks_contract(),
        "governed_web_safety_activation": {
            "stage_version": PHASE,
            "status": "locked",
            "activation_state": "governed_locked",
            "authority": authority_contract(),
            "authority_locks": authority_locks_contract(),
        },
        "blocked_authority_modes": {
            "live_web_execution": "blocked",
            "autonomous_agent_execution": "blocked",
            "runtime_truth_mutation": "blocked",
            "automatic_updates": "blocked",
            "autonomous_crawling": "blocked",
            "body_read": "blocked",
            "self_apply": "blocked",
        },
    }
    flags = safety_key_contract()
    payload.update(flags)
    payload["governed_web_safety_activation"].update(flags)
    return payload


def normalize_s32r2r1_safety_payload(payload: Any) -> Any:
    """One-level finalizer. It does not recursively walk arbitrary payloads."""
    if not isinstance(payload, dict):
        return payload

    payload.update(safety_key_contract())
    payload.setdefault("stage_version", PHASE)
    payload.setdefault("phase", PHASE)
    payload.setdefault("version", VERSION)
    payload.setdefault("status", "ok")
    payload.setdefault("backend_owns_truth", True)
    payload.setdefault("cockpit_presentation_only", True)
    payload.setdefault("runtime_truth_write", "blocked")
    payload.setdefault("runtime_truth_modified", False)
    payload.setdefault("authority", authority_contract())
    payload.setdefault("authority_locks", authority_locks_contract())
    payload.setdefault("governed_payload_reconciliation", {"status": "ok", "present": True})

    safety = payload.setdefault("governed_web_safety_activation", {})
    if not isinstance(safety, dict):
        safety = {}
        payload["governed_web_safety_activation"] = safety
    safety.update(safety_key_contract())
    safety.setdefault("status", "locked")
    safety.setdefault("authority", authority_contract())
    safety.setdefault("authority_locks", authority_locks_contract())

    return payload


def get_governed_web_safety_activation() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def build_web_safety_activation() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def get_web_safety_activation() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def build_s32r2r1_web_safety_payload() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def get_s32r2r1_web_safety_payload() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def build_s32r2r1_dashboard_payload_exposes_safety_activation() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def build_s32r2r1_ast_bridge_web_safety_payload() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def build_s32r2r1_safety_activation() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def governed_web_safety_activation_payload() -> Dict[str, Any]:
    return build_governed_web_safety_activation()


def register_governed_web_safety_activation_routes(app: Any) -> Any:
    paths = {
        "/dashboard/safety-activation",
        "/api/dashboard/safety-activation",
        "/dashboard/web-safety",
        "/api/dashboard/web-safety",
        "/dashboard/governed-web-safety-activation",
    }
    app.router.routes = [route for route in app.router.routes if getattr(route, "path", None) not in paths]

    async def _route() -> Dict[str, Any]:
        return build_governed_web_safety_activation()

    for path in sorted(paths):
        app.add_api_route(
            path,
            _route,
            methods=["GET"],
            name=("claire_s32r2r1_web_safety_" + path.strip("/").replace("/", "_").replace("-", "_"))[:120],
            include_in_schema=True,
        )

    setattr(app.state, "claire_s32r2r1_web_safety_activation_routes_registered", True)
    return app


def register_s32r2r1_web_safety_routes(app: Any) -> Any:
    return register_governed_web_safety_activation_routes(app)


__all__ = [
    "FALSE_FLAGS",
    "STATUS_FLAGS",
    "AUTHORITY",
    "safety_key_contract",
    "authority_contract",
    "authority_locks_contract",
    "normalize_s32r2r1_safety_payload",
    "build_governed_web_safety_activation",
    "get_governed_web_safety_activation",
    "build_web_safety_activation",
    "get_web_safety_activation",
    "build_s32r2r1_web_safety_payload",
    "get_s32r2r1_web_safety_payload",
    "build_s32r2r1_dashboard_payload_exposes_safety_activation",
    "build_s32r2r1_ast_bridge_web_safety_payload",
    "build_s32r2r1_safety_activation",
    "governed_web_safety_activation_payload",
    "register_governed_web_safety_activation_routes",
    "register_s32r2r1_web_safety_routes",
]
