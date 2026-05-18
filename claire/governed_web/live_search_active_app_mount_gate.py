
# Claire Syntalion v18.62
# Live Search Endpoint Mounted Into Active App Gate
#
# This module mounts the governed live-search router into an active FastAPI app
# only when explicitly enabled. It does not perform real web calls, mutate
# runtime truth, enable autonomous execution, or perform automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


CONTRACT_VERSION = "v18.62.live_search_endpoint_mounted_into_active_app_gate"

LIVE_SEARCH_PATH = "/api/dashboard/search/live"
SMOKE_GOOGLE_PATH = "/api/dashboard/search/smoke/google"

DEFAULT_ACTIVE_APP_CANDIDATES = [
    "main:app",
    "claire.main:app",
    "claire.server:app",
    "claire.app:app",
    "claire.api.app:app",
    "src.main:app",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class LiveSearchActiveAppMountPolicy:
    explicit_enable_required: bool = True
    import_discovery_read_only: bool = True
    route_mount_mutation_requires_app_object: bool = True
    manual_enable_required: bool = True
    real_internet_calls_allowed: bool = False
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_enable_required": self.explicit_enable_required,
            "import_discovery_read_only": self.import_discovery_read_only,
            "route_mount_mutation_requires_app_object": self.route_mount_mutation_requires_app_object,
            "manual_enable_required": self.manual_enable_required,
            "real_internet_calls_allowed": self.real_internet_calls_allowed,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
        }


def _governance(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "fail_closed": True,
        "real_internet_calls": False,
    }
    if extra:
        payload.update(extra)
    return payload


def inspect_active_app_candidates(candidates: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    checked: List[Dict[str, Any]] = []
    policy = LiveSearchActiveAppMountPolicy()

    for candidate in list(candidates or DEFAULT_ACTIVE_APP_CANDIDATES):
        if ":" not in candidate:
            checked.append({
                "candidate": candidate,
                "available": False,
                "reason": "invalid_candidate_format",
            })
            continue

        module_name, attr_name = candidate.split(":", 1)
        try:
            module = import_module(module_name)
            app = getattr(module, attr_name)
            include_router_available = hasattr(app, "include_router")
            checked.append({
                "candidate": candidate,
                "available": bool(include_router_available),
                "module_imported": True,
                "attribute_found": True,
                "include_router_available": bool(include_router_available),
                "reason": "" if include_router_available else "attribute_is_not_fastapi_like_app",
            })
        except Exception as exc:
            checked.append({
                "candidate": candidate,
                "available": False,
                "module_imported": False,
                "attribute_found": False,
                "include_router_available": False,
                "reason": type(exc).__name__,
            })

    available = [item for item in checked if item.get("available") is True]
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "active_app_candidate_found" if available else "no_active_app_candidate_found",
        "created_at": _utc_now(),
        "checked": checked,
        "available_candidates": available,
        "policy": policy.to_dict(),
        "governance": _governance({"read_only_inspection": True}),
    }


def build_governed_live_search_router_for_active_app() -> Dict[str, Any]:
    policy = LiveSearchActiveAppMountPolicy()
    try:
        from claire.api.governed_dashboard_live_search_routes import (
            build_governed_dashboard_live_search_router,
            router_readiness,
        )
        router = build_governed_dashboard_live_search_router()
        readiness = router_readiness()
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "governed_dashboard_live_search_router_unavailable",
            "created_at": _utc_now(),
            "router": None,
            "error_type": type(exc).__name__,
            "policy": policy.to_dict(),
            "governance": _governance(),
        }

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "router_ready",
        "reason": "",
        "created_at": _utc_now(),
        "router": router,
        "router_readiness": readiness,
        "policy": policy.to_dict(),
        "governance": _governance(),
    }


def mount_governed_live_search_into_app(
    app: Any,
    *,
    explicit_enable: bool = False,
    mount_once_marker: str = "_claire_governed_live_search_v18_62_mounted",
) -> Dict[str, Any]:
    policy = LiveSearchActiveAppMountPolicy()

    if not explicit_enable:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_active_app_mount_enable_required",
            "created_at": _utc_now(),
            "mount_attempted": False,
            "mounted": False,
            "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
            "policy": policy.to_dict(),
            "governance": _governance({"explicit_enable": False}),
        }

    if app is None or not hasattr(app, "include_router"):
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_app_with_include_router_required",
            "created_at": _utc_now(),
            "mount_attempted": False,
            "mounted": False,
            "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
            "policy": policy.to_dict(),
            "governance": _governance({"explicit_enable": True}),
        }

    if getattr(app, mount_once_marker, False) is True:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "already_mounted",
            "reason": "",
            "created_at": _utc_now(),
            "mount_attempted": False,
            "mounted": True,
            "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
            "policy": policy.to_dict(),
            "governance": _governance({"explicit_enable": True, "idempotent": True}),
        }

    router_result = build_governed_live_search_router_for_active_app()
    router = router_result.get("router")
    if router is None:
        return {
            **{k: v for k, v in router_result.items() if k != "router"},
            "mount_attempted": False,
            "mounted": False,
            "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
        }

    try:
        app.include_router(router)
        setattr(app, mount_once_marker, True)
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "mount_failed",
            "reason": "include_router_exception",
            "created_at": _utc_now(),
            "mount_attempted": True,
            "mounted": False,
            "error_type": type(exc).__name__,
            "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
            "policy": policy.to_dict(),
            "governance": _governance({"explicit_enable": True}),
        }

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "mounted",
        "reason": "",
        "created_at": _utc_now(),
        "mount_attempted": True,
        "mounted": True,
        "paths": [LIVE_SEARCH_PATH, SMOKE_GOOGLE_PATH],
        "router_readiness": router_result.get("router_readiness", {}),
        "policy": policy.to_dict(),
        "governance": _governance({"explicit_enable": True}),
    }


def mount_into_discovered_active_app(
    *,
    explicit_enable: bool = False,
    candidates: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    policy = LiveSearchActiveAppMountPolicy()
    inspection = inspect_active_app_candidates(candidates)
    available = inspection.get("available_candidates") or []

    if not available:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "no_active_app_candidate_found",
            "created_at": _utc_now(),
            "mount_attempted": False,
            "mounted": False,
            "inspection": inspection,
            "policy": policy.to_dict(),
            "governance": _governance({"read_only_inspection": True}),
        }

    candidate = available[0]["candidate"]
    module_name, attr_name = candidate.split(":", 1)
    module = import_module(module_name)
    app = getattr(module, attr_name)

    result = mount_governed_live_search_into_app(app, explicit_enable=explicit_enable)
    return {
        **result,
        "active_app_candidate": candidate,
        "inspection": inspection,
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_ACTIVE_APP_CANDIDATES",
    "LIVE_SEARCH_PATH",
    "LiveSearchActiveAppMountPolicy",
    "SMOKE_GOOGLE_PATH",
    "build_governed_live_search_router_for_active_app",
    "inspect_active_app_candidates",
    "mount_governed_live_search_into_app",
    "mount_into_discovered_active_app",
]
