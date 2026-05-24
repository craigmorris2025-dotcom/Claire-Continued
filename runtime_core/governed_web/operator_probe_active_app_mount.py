from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

CONTRACT_VERSION = "v18.69.operator_probe_route_mount_into_active_app"

STATUS_PATH = "/api/dashboard/search/provider/status"
PROBE_PATH = "/api/dashboard/search/provider/probe"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class OperatorProbeActiveAppMountPolicy:
    explicit_mount_required: bool = True
    route_mount_explicit_only: bool = True
    real_provider_probe_not_triggered_by_mount: bool = True
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_mount_required": self.explicit_mount_required,
            "route_mount_explicit_only": self.route_mount_explicit_only,
            "real_provider_probe_not_triggered_by_mount": self.real_provider_probe_not_triggered_by_mount,
            "manual_enable_required": self.manual_enable_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
        }


def _gov(extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    data = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "uncontrolled_browsing": False,
        "fail_closed": True,
        "operator_review_required": True,
        "real_provider_probe_triggered": False,
    }
    if extra:
        data.update(dict(extra))
    return data


def build_operator_probe_router_for_active_app() -> Dict[str, Any]:
    policy = OperatorProbeActiveAppMountPolicy()
    try:
        from runtime_core.api.real_provider_operator_probe_routes import router, router_readiness
        readiness = router_readiness()
    except Exception as exc:
        try:
            from .real_provider_operator_probe_route import create_real_provider_operator_probe_router
            router = create_real_provider_operator_probe_router()
            readiness = {
                "contract_version": CONTRACT_VERSION,
                "status": "router_ready",
                "source": "fallback_create_real_provider_operator_probe_router",
                "routes": [
                    {"method": "GET", "path": STATUS_PATH},
                    {"method": "POST", "path": PROBE_PATH},
                ],
            }
        except Exception as inner_exc:
            return {
                "contract_version": CONTRACT_VERSION,
                "status": "blocked",
                "reason": "operator_probe_router_unavailable",
                "created_at": _now(),
                "router": None,
                "error_type": type(exc).__name__,
                "fallback_error_type": type(inner_exc).__name__,
                "policy": policy.to_dict(),
                "governance": _gov(),
            }

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "router_ready",
        "reason": "",
        "created_at": _now(),
        "router": router,
        "router_readiness": readiness,
        "paths": [STATUS_PATH, PROBE_PATH],
        "policy": policy.to_dict(),
        "governance": _gov({"router_build_only": True}),
    }


def inspect_operator_probe_route_table(app: Any) -> Dict[str, Any]:
    policy = OperatorProbeActiveAppMountPolicy()
    rows: List[Dict[str, Any]] = []

    for route in getattr(app, "routes", []) or []:
        path = str(getattr(route, "path", ""))
        methods = getattr(route, "methods", set()) or set()
        rows.append({
            "path": path,
            "methods": sorted(str(method) for method in methods),
            "name": str(getattr(route, "name", "")),
        })

    paths = {row["path"] for row in rows}
    status_present = STATUS_PATH in paths
    probe_present = PROBE_PATH in paths

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_probe_routes_present" if status_present and probe_present else "operator_probe_routes_missing",
        "created_at": _now(),
        "routes": rows,
        "status_path_present": status_present,
        "probe_path_present": probe_present,
        "required_paths": [STATUS_PATH, PROBE_PATH],
        "policy": policy.to_dict(),
        "governance": _gov({"route_table_inspection": True}),
    }


def mount_operator_probe_routes_into_app(
    app: Any,
    *,
    explicit_enable: bool = False,
    mount_once_marker: str = "_claire_operator_probe_routes_v18_69_mounted",
) -> Dict[str, Any]:
    policy = OperatorProbeActiveAppMountPolicy()

    if not explicit_enable:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_operator_probe_mount_enable_required",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": False,
            "paths": [STATUS_PATH, PROBE_PATH],
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": False}),
        }

    if app is None or not hasattr(app, "include_router"):
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_app_with_include_router_required",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": False,
            "paths": [STATUS_PATH, PROBE_PATH],
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True}),
        }

    if getattr(app, mount_once_marker, False) is True:
        table = inspect_operator_probe_route_table(app)
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "already_mounted",
            "reason": "",
            "created_at": _now(),
            "mount_attempted": False,
            "mounted": True,
            "route_table": table,
            "paths": [STATUS_PATH, PROBE_PATH],
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True, "idempotent": True}),
        }

    router_result = build_operator_probe_router_for_active_app()
    router = router_result.get("router")
    if router is None:
        return {
            **{k: v for k, v in router_result.items() if k != "router"},
            "mount_attempted": False,
            "mounted": False,
            "paths": [STATUS_PATH, PROBE_PATH],
        }

    try:
        app.include_router(router)
        setattr(app, mount_once_marker, True)
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "mount_failed",
            "reason": "include_router_exception",
            "created_at": _now(),
            "mount_attempted": True,
            "mounted": False,
            "error_type": type(exc).__name__,
            "paths": [STATUS_PATH, PROBE_PATH],
            "policy": policy.to_dict(),
            "governance": _gov({"explicit_enable": True}),
        }

    table = inspect_operator_probe_route_table(app)
    mounted = table.get("status_path_present") is True and table.get("probe_path_present") is True

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "mounted" if mounted else "mount_incomplete",
        "reason": "" if mounted else "mounted_route_table_missing_required_paths",
        "created_at": _now(),
        "mount_attempted": True,
        "mounted": mounted,
        "router_readiness": router_result.get("router_readiness", {}),
        "route_table": table,
        "paths": [STATUS_PATH, PROBE_PATH],
        "policy": policy.to_dict(),
        "governance": _gov({"explicit_enable": True}),
    }


def build_operator_probe_mount_smoke_app() -> Dict[str, Any]:
    policy = OperatorProbeActiveAppMountPolicy()
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from .real_provider_operator_probe_route import (
            build_operator_probe_request_payload,
            execute_operator_provider_probe_request,
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_or_operator_probe_contract_unavailable",
            "created_at": _now(),
            "error_type": type(exc).__name__,
            "policy": policy.to_dict(),
            "governance": _gov(),
        }

    app = FastAPI(title="Claire v18.69 Operator Probe Mounted Route Smoke App")
    mount_result = mount_operator_probe_routes_into_app(app, explicit_enable=True)
    route_table = inspect_operator_probe_route_table(app)
    client = TestClient(app)

    status_response = client.get(STATUS_PATH)
    probe_response = client.post(PROBE_PATH, json={
        "query": "google",
        "explicit_real_provider_probe": False,
        "provider": "operator-controlled-real-provider",
        "max_results": 3,
    })

    try:
        status_payload = status_response.json()
    except Exception:
        status_payload = {"raw_text": getattr(status_response, "text", "")}

    try:
        route_block_payload = probe_response.json()
    except Exception:
        route_block_payload = {"raw_text": getattr(probe_response, "text", "")}

    direct_block_payload = execute_operator_provider_probe_request(
        build_operator_probe_request_payload(query="google", explicit_real_provider_probe=False)
    )

    status_ok = status_response.status_code == 200 and isinstance(status_payload, dict)
    route_block_ok = (
        probe_response.status_code == 200
        and isinstance(route_block_payload, dict)
        and route_block_payload.get("status") == "blocked"
        and route_block_payload.get("reason") == "explicit_real_provider_probe_required"
    )
    direct_block_ok = (
        direct_block_payload.get("status") == "blocked"
        and direct_block_payload.get("reason") == "explicit_real_provider_probe_required"
    )

    passed = (
        mount_result.get("mounted") is True
        and route_table.get("status") == "operator_probe_routes_present"
        and status_ok
        and (route_block_ok or direct_block_ok)
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "operator_probe_mount_smoke_failed",
        "created_at": _now(),
        "mount_result": mount_result,
        "route_table": route_table,
        "status_http_status": status_response.status_code,
        "probe_http_status": probe_response.status_code,
        "status_payload": status_payload,
        "route_block_payload": route_block_payload,
        "direct_block_payload": direct_block_payload,
        "status_ok": status_ok,
        "route_block_ok": route_block_ok,
        "direct_block_ok": direct_block_ok,
        "blocked_probe_confirmed": bool(route_block_ok or direct_block_ok),
        "paths": {"status": STATUS_PATH, "probe": PROBE_PATH},
        "policy": policy.to_dict(),
        "governance": _gov({"mount_smoke_test": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "PROBE_PATH",
    "STATUS_PATH",
    "OperatorProbeActiveAppMountPolicy",
    "build_operator_probe_mount_smoke_app",
    "build_operator_probe_router_for_active_app",
    "inspect_operator_probe_route_table",
    "mount_operator_probe_routes_into_app",
]
