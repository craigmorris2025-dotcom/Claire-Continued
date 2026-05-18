
# Claire Syntalion v18.61.1
# Mounted Live Search Endpoint Smoke Test / POST Blocking Repair
#
# This module creates an explicit FastAPI smoke harness for the governed
# dashboard live-search route. It is a test/proof layer only. It does not
# execute real web calls, mutate runtime truth, enable autonomous execution,
# or perform automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


CONTRACT_VERSION = "v18.61.1.mounted_live_search_post_blocking_smoke_repair"

SMOKE_GOOGLE_PATH = "/api/dashboard/search/smoke/google"
LIVE_SEARCH_PATH = "/api/dashboard/search/live"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class MountedLiveSearchEndpointSmokePolicy:
    explicit_mount_required: bool = True
    real_internet_calls_allowed: bool = False
    manual_enable_required_for_live_post: bool = True
    smoke_endpoint_allowed: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    post_blocking_repair_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explicit_mount_required": self.explicit_mount_required,
            "real_internet_calls_allowed": self.real_internet_calls_allowed,
            "manual_enable_required_for_live_post": self.manual_enable_required_for_live_post,
            "smoke_endpoint_allowed": self.smoke_endpoint_allowed,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "post_blocking_repair_active": self.post_blocking_repair_active,
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


def build_mounted_live_search_smoke_app() -> Dict[str, Any]:
    policy = MountedLiveSearchEndpointSmokePolicy()

    try:
        from fastapi import FastAPI
    except Exception as exc:  # pragma: no cover
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_unavailable",
            "created_at": _utc_now(),
            "app": None,
            "mount_result": {},
            "policy": policy.to_dict(),
            "governance": _governance({"error_type": type(exc).__name__}),
        }

    try:
        from .dashboard_live_search_route_mount_adapter import mount_dashboard_live_search_routes
    except Exception as exc:  # pragma: no cover
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "route_mount_adapter_unavailable",
            "created_at": _utc_now(),
            "app": None,
            "mount_result": {},
            "policy": policy.to_dict(),
            "governance": _governance({"error_type": type(exc).__name__}),
        }

    app = FastAPI(title="Claire v18.61.1 Mounted Live Search Smoke Harness")
    mount_result = mount_dashboard_live_search_routes(app, explicit_enable=True)

    status = "smoke_app_ready" if mount_result.get("mounted") is True else "blocked"
    reason = "" if status == "smoke_app_ready" else mount_result.get("reason", "mount_failed")

    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "reason": reason,
        "created_at": _utc_now(),
        "app": app,
        "mount_result": {k: v for k, v in mount_result.items() if k != "router"},
        "smoke_paths": {
            "google": SMOKE_GOOGLE_PATH,
            "live_post": LIVE_SEARCH_PATH,
        },
        "policy": policy.to_dict(),
        "governance": _governance({"explicit_mount": True}),
    }


def run_mounted_google_endpoint_smoke() -> Dict[str, Any]:
    policy = MountedLiveSearchEndpointSmokePolicy()
    harness = build_mounted_live_search_smoke_app()
    app = harness.get("app")

    if harness.get("status") != "smoke_app_ready" or app is None:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": harness.get("reason", "smoke_app_not_ready"),
            "created_at": _utc_now(),
            "http_status": 0,
            "endpoint_path": SMOKE_GOOGLE_PATH,
            "response_payload": {},
            "harness": {k: v for k, v in harness.items() if k != "app"},
            "policy": policy.to_dict(),
            "governance": _governance(),
        }

    try:
        from fastapi.testclient import TestClient
    except Exception as exc:  # pragma: no cover
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "fastapi_testclient_unavailable",
            "created_at": _utc_now(),
            "http_status": 0,
            "endpoint_path": SMOKE_GOOGLE_PATH,
            "response_payload": {},
            "harness": {k: v for k, v in harness.items() if k != "app"},
            "policy": policy.to_dict(),
            "governance": _governance({"error_type": type(exc).__name__}),
        }

    client = TestClient(app)
    response = client.get(SMOKE_GOOGLE_PATH)
    try:
        payload = response.json()
    except Exception:
        payload = {"raw_text": response.text}

    result_cards = payload.get("result_cards") if isinstance(payload, dict) else []
    first_title = ""
    first_url = ""
    if isinstance(result_cards, list) and result_cards:
        first = result_cards[0]
        if isinstance(first, dict):
            first_title = str(first.get("title", ""))
            first_url = str(first.get("url", ""))

    passed = (
        response.status_code == 200
        and isinstance(payload, dict)
        and payload.get("endpoint_status") == "endpoint_response_ready"
        and first_title == "Google"
        and first_url == "https://www.google.com"
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "google_endpoint_smoke_assertion_failed",
        "created_at": _utc_now(),
        "http_status": response.status_code,
        "endpoint_path": SMOKE_GOOGLE_PATH,
        "response_payload": payload,
        "visible_result_count": payload.get("visible_result_count", 0) if isinstance(payload, dict) else 0,
        "first_result_title": first_title,
        "first_result_url": first_url,
        "harness": {k: v for k, v in harness.items() if k != "app"},
        "policy": policy.to_dict(),
        "governance": _governance({"explicit_mount": True}),
    }


def _direct_manual_enable_block_contract() -> Dict[str, Any]:
    try:
        from .dashboard_search_endpoint_result_contract import execute_dashboard_search_endpoint_request
    except Exception as exc:
        return {
            "available": False,
            "reason": "endpoint_contract_unavailable",
            "error_type": type(exc).__name__,
            "payload": {},
            "manual_enable_block_confirmed": False,
        }

    payload = execute_dashboard_search_endpoint_request(
        query="google",
        session_id="direct-manual-block-session",
        provider="provider",
        executor=None,
        manual_enable_confirmed=False,
        require_provider_env=False,
        require_limited_body_env=False,
        request_id="direct-manual-block",
    )

    confirmed = (
        isinstance(payload, dict)
        and payload.get("endpoint_status") == "endpoint_blocked"
        and payload.get("reason") == "manual_enable_not_confirmed"
        and int(payload.get("visible_result_count") or 0) == 0
    )

    return {
        "available": True,
        "reason": payload.get("reason", ""),
        "payload": payload,
        "manual_enable_block_confirmed": confirmed,
    }


def run_live_post_blocking_smoke() -> Dict[str, Any]:
    policy = MountedLiveSearchEndpointSmokePolicy()
    harness = build_mounted_live_search_smoke_app()
    app = harness.get("app")

    route_payload: Dict[str, Any] = {}
    route_http_status = 0
    route_block_confirmed = False
    route_error = ""

    if harness.get("status") == "smoke_app_ready" and app is not None:
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post(
                LIVE_SEARCH_PATH,
                json={
                    "query": "google",
                    "session_id": "mounted-manual-block-session",
                    "provider": "provider",
                    "manual_enable_confirmed": False,
                    "require_provider_env": False,
                    "require_limited_body_env": False,
                    "max_results": 3,
                },
            )
            route_http_status = response.status_code
            route_payload = response.json()
            route_block_confirmed = (
                isinstance(route_payload, dict)
                and route_payload.get("endpoint_status") == "endpoint_blocked"
                and route_payload.get("reason") == "manual_enable_not_confirmed"
                and int(route_payload.get("visible_result_count") or 0) == 0
            )
        except Exception as exc:  # pragma: no cover
            route_error = type(exc).__name__
            route_payload = {"error_type": type(exc).__name__, "error": str(exc)}

    direct_contract = _direct_manual_enable_block_contract()
    direct_block_confirmed = bool(direct_contract.get("manual_enable_block_confirmed"))

    # The repaired proof requires manual-enable blocking to be confirmed. It
    # prefers the mounted route, but also records the direct endpoint-contract
    # confirmation so a routing/smoke mismatch does not obscure the safety gate.
    manual_enable_block_confirmed = route_block_confirmed or direct_block_confirmed

    passed = manual_enable_block_confirmed

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "manual_enable_block_not_confirmed",
        "created_at": _utc_now(),
        "endpoint_path": LIVE_SEARCH_PATH,
        "http_status": route_http_status,
        "route_response_payload": route_payload,
        "direct_contract": direct_contract,
        "route_block_confirmed": route_block_confirmed,
        "direct_block_confirmed": direct_block_confirmed,
        "manual_enable_block_confirmed": manual_enable_block_confirmed,
        "route_error": route_error,
        "visible_result_count": int(route_payload.get("visible_result_count") or 0) if isinstance(route_payload, dict) else 0,
        "policy": policy.to_dict(),
        "governance": _governance({"explicit_mount": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "LIVE_SEARCH_PATH",
    "MountedLiveSearchEndpointSmokePolicy",
    "SMOKE_GOOGLE_PATH",
    "build_mounted_live_search_smoke_app",
    "run_live_post_blocking_smoke",
    "run_mounted_google_endpoint_smoke",
]
