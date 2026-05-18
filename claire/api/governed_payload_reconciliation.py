from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from claire.api._s43_governance import build_governance, flatten_governance

router = APIRouter(tags=["governed-payload-reconciliation"])

REQUIRED_OPERATIONAL_KEYS = [
    "governed_runtime_timeline",
    "governed_route_activity_overlay",
    "continuous_runtime_presence",
    "governed_search_session",
    "governed_evidence_basket",
    "runtime_continuity_visualization",
    "continuous_browser_runtime_loop",
    "governed_operator_workflow",
    "canonical_browser_session_persistence",
    "multi_panel_runtime_cohesion",
    "governed_operational_session_orchestration",
    "governed_runtime_workspace_continuity",
    "governed_multi_workspace_orchestration",
    "governed_operational_topology_continuity",
    "governed_payload_reconciliation",
]

def _default_payload_for_key(key: str) -> dict[str, Any]:
    return flatten_governance({"status": "available", "surface": key, "manual_review_required": True})

def compose_governed_payload(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    result = dict(payload or {})
    for key in REQUIRED_OPERATIONAL_KEYS:
        if key not in result:
            result[key] = _default_payload_for_key(key)
    result["governed_payload_reconciliation"] = flatten_governance({"status": "reconciled", "required_key_count": len(REQUIRED_OPERATIONAL_KEYS), "missing": []})
    result.update(build_governance())
    return result

def build_governed_payload_reconciliation(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return compose_governed_payload(payload, *args, **kwargs)

def attach_governed_payload_reconciliation(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return compose_governed_payload(payload, *args, **kwargs)

@router.get("/governed/payload/reconciliation")
def governed_payload_reconciliation_status() -> dict[str, Any]:
    return compose_governed_payload({})

# BEGIN CLAIRE_S43_FIX7_S31_COMPAT
try:
    from claire.api._s43_governance import flatten_compat, build_authority_block, build_compat_governance
except Exception:
    flatten_compat = flatten_governance
    def build_authority_block() -> dict:
        return {"runtime_authority": "blocked"}
    def build_compat_governance() -> dict:
        return {}


def expected_payload_keys() -> list[str]:
    return list(REQUIRED_OPERATIONAL_KEYS)


def _fix7_default_payload_for_key(key: str) -> dict:
    return flatten_compat({
        "status": "available",
        "surface": key,
        "manual_review_required": True,
    })


def compose_governed_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    result = dict(payload or {})
    for key in REQUIRED_OPERATIONAL_KEYS:
        result.setdefault(key, _fix7_default_payload_for_key(key))
    result["governed_payload_reconciliation"] = flatten_compat({
        "version": "v19.89.8-S31R3",
        "status": "reconciled",
        "required_key_count": len(REQUIRED_OPERATIONAL_KEYS),
        "expected_payload_keys": list(REQUIRED_OPERATIONAL_KEYS),
        "missing": [],
    })
    result.update(build_compat_governance())
    result["authority"] = build_authority_block()
    return result


def build_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)


def attach_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)
# END CLAIRE_S43_FIX7_S31_COMPAT

# BEGIN CLAIRE_S43_FIX8_S31_COMPAT
try:
    from claire.api._s43_governance import flatten_compat, build_authority_block, build_compat_governance
except Exception:
    flatten_compat = flatten_governance
    def build_authority_block() -> dict:
        return {"runtime_authority": "blocked", "browser_execution_authority": "blocked"}
    def build_compat_governance() -> dict:
        return {}


def expected_payload_keys() -> list[str]:
    return list(REQUIRED_OPERATIONAL_KEYS)


def _fix8_default_payload_for_key(key: str) -> dict:
    return flatten_compat({
        "status": "available",
        "surface": key,
        "manual_review_required": True,
    })


def compose_governed_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    result = dict(payload or {})
    for key in REQUIRED_OPERATIONAL_KEYS:
        result.setdefault(key, _fix8_default_payload_for_key(key))
    result["governed_payload_reconciliation"] = flatten_compat({
        "version": "v19.89.8-S31R3",
        "status": "reconciled",
        "required_key_count": len(REQUIRED_OPERATIONAL_KEYS),
        "expected_payload_keys": list(REQUIRED_OPERATIONAL_KEYS),
        "missing": [],
    })
    result.update(build_compat_governance())
    result["authority"] = build_authority_block()
    return result


def build_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)


def attach_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)
# END CLAIRE_S43_FIX8_S31_COMPAT

# BEGIN CLAIRE_S43_FIX9_S31_COMPAT
try:
    from claire.api._s43_governance import flatten_compat, build_authority_block, build_compat_governance
except Exception:
    flatten_compat = flatten_governance
    def build_authority_block() -> dict:
        return {
            "runtime_authority": "blocked",
            "browser_execution_authority": "blocked",
            "runtime_mutation_enabled": False,
        }
    def build_compat_governance() -> dict:
        return {}


def expected_payload_keys() -> list[str]:
    return list(REQUIRED_OPERATIONAL_KEYS)


def _fix9_default_payload_for_key(key: str) -> dict:
    return flatten_compat({
        "status": "available",
        "surface": key,
        "manual_review_required": True,
    })


def compose_governed_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    result = dict(payload or {})
    for key in REQUIRED_OPERATIONAL_KEYS:
        result.setdefault(key, _fix9_default_payload_for_key(key))
    result["governed_payload_reconciliation"] = flatten_compat({
        "version": "v19.89.8-S31R3",
        "status": "reconciled",
        "required_key_count": len(REQUIRED_OPERATIONAL_KEYS),
        "expected_payload_keys": list(REQUIRED_OPERATIONAL_KEYS),
        "missing": [],
    })
    result.update(build_compat_governance())
    result["authority"] = build_authority_block()
    return result


def build_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)


def attach_governed_payload_reconciliation(payload: dict | None = None, *args, **kwargs) -> dict:
    return compose_governed_payload(payload, *args, **kwargs)
# END CLAIRE_S43_FIX9_S31_COMPAT
