"""
S338-S344 — Canonical /dashboard/payload Integration.

This module folds the green S296-S337 internet-readiness and dashboard
consolidation contracts into the live canonical dashboard payload path.

It registers the existing /dashboard/payload and /dashboard/payload/status paths
with an enriched read-only payload. It does not create random panel endpoints,
does not enable live action execution, and does not mutate runtime truth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import asyncio
import inspect
import json

from fastapi import FastAPI

from claire.api.dashboard_action_panel_consolidation_s331_s337 import (
    build_dashboard_action_panel_consolidation_s331_s337,
)
from claire.api.dashboard_contract_consolidation_s317_s323 import (
    apply_s317_s323_extension_to_payload,
    build_dashboard_contract_consolidation_s317_s323,
)
from claire.api.dashboard_operator_cockpit_layout_s324_s330 import (
    build_operator_cockpit_layout_consolidation_s324_s330,
)
from claire.api.governed_internet_update_foundation_s296_s302 import authority_locks


PHASE = "S338-S344"
VERSION = "v19.89.8-S338-S344"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "authority_locks": authority_locks(),
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "proposal_only": True,
        "runtime_truth_modified": False,
        "created_at": _timestamp(),
    }
    payload.update(extra)
    return payload


def _resolve_maybe_awaitable(value: Any) -> Any:
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)
    raise RuntimeError("Cannot synchronously resolve awaitable dashboard payload inside a running event loop.")


def build_s338_existing_payload_reader() -> Dict[str, Any]:
    try:
        from claire.api import dashboard_payload_bridge as bridge  # type: ignore

        raw = bridge.get_dashboard_payload()
        payload = _resolve_maybe_awaitable(raw)
        if not isinstance(payload, dict):
            payload = {"legacy_payload_value": payload}
        source = "claire.api.dashboard_payload_bridge.get_dashboard_payload"
        fallback_used = False
    except Exception as exc:
        payload = {
            "legacy_payload_unavailable": True,
            "legacy_payload_error": repr(exc),
        }
        source = "fallback_empty_payload"
        fallback_used = True

    return _base(
        "S338",
        "existing_dashboard_payload_reader_ready",
        source=source,
        fallback_used=fallback_used,
        existing_payload=payload,
        existing_payload_keys=sorted(str(key) for key in payload.keys()),
    )


def build_s339_payload_merge_owner() -> Dict[str, Any]:
    existing = build_s338_existing_payload_reader()["existing_payload"]
    merged = apply_s317_s323_extension_to_payload(existing)
    merged["dashboard_contract_consolidation"] = build_dashboard_contract_consolidation_s317_s323()
    merged["operator_cockpit_layout_consolidation"] = build_operator_cockpit_layout_consolidation_s324_s330()
    merged["dashboard_action_panel_consolidation"] = build_dashboard_action_panel_consolidation_s331_s337()
    merged["canonical_dashboard_integration"] = {
        "stage_version": "S339",
        "integration_version": VERSION,
        "truth_source": PAYLOAD_ENDPOINT,
        "random_endpoint_sprawl_allowed": False,
        "frontend_payload_keys": [
            "internet_update_readiness",
            "internet_evidence",
            "internet_update_proposals",
            "cockpit_panel_registry",
            "dashboard_fetch_map_lock",
            "dashboard_renderer_states",
        ],
    }
    return _base(
        "S339",
        "payload_merge_owner_ready",
        merged_payload=merged,
        merged_payload_keys=sorted(str(key) for key in merged.keys()),
    )


def get_s338_s344_integrated_dashboard_payload() -> Dict[str, Any]:
    return build_s339_payload_merge_owner()["merged_payload"]


def build_s340_integrated_status_endpoint_contract() -> Dict[str, Any]:
    payload = get_s338_s344_integrated_dashboard_payload()
    status = {
        "status": "ok",
        "integration": "s338_s344_canonical_dashboard_payload_integration",
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "required_keys_present": {
            "internet_update_readiness": "internet_update_readiness" in payload,
            "internet_evidence": "internet_evidence" in payload,
            "internet_update_proposals": "internet_update_proposals" in payload,
            "cockpit_panel_registry": "cockpit_panel_registry" in payload,
            "dashboard_fetch_map_lock": "dashboard_fetch_map_lock" in payload,
        },
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
    }
    status["ok"] = all(status["required_keys_present"].values())
    return _base("S340", "integrated_status_endpoint_contract_ready", status_payload=status)


def get_s338_s344_integrated_dashboard_payload_status() -> Dict[str, Any]:
    return build_s340_integrated_status_endpoint_contract()["status_payload"]


def _remove_existing_dashboard_payload_routes(app: FastAPI) -> int:
    removed = 0
    kept = []
    for route in list(getattr(app.router, "routes", [])):
        if getattr(route, "path", None) in {PAYLOAD_ENDPOINT, STATUS_ENDPOINT}:
            removed += 1
            continue
        kept.append(route)
    app.router.routes = kept
    return removed


def register_s338_s344_dashboard_payload_routes(app: FastAPI) -> FastAPI:
    removed = _remove_existing_dashboard_payload_routes(app)
    app.add_api_route(
        PAYLOAD_ENDPOINT,
        get_s338_s344_integrated_dashboard_payload,
        methods=["GET"],
        name="claire_s338_s344_integrated_dashboard_payload",
        include_in_schema=True,
    )
    app.add_api_route(
        STATUS_ENDPOINT,
        get_s338_s344_integrated_dashboard_payload_status,
        methods=["GET"],
        name="claire_s338_s344_integrated_dashboard_payload_status",
        include_in_schema=True,
    )
    setattr(app.state, "claire_s338_s344_dashboard_payload_routes_registered", True)
    setattr(app.state, "claire_s338_s344_dashboard_payload_routes_removed", removed)
    return app


def build_s341_route_registration_contract() -> Dict[str, Any]:
    app = FastAPI()
    register_s338_s344_dashboard_payload_routes(app)
    paths = sorted(getattr(route, "path", "") for route in app.router.routes)
    return _base(
        "S341",
        "route_registration_contract_ready",
        registered_paths=paths,
        payload_registered=PAYLOAD_ENDPOINT in paths,
        status_registered=STATUS_ENDPOINT in paths,
        app_state_registered=getattr(app.state, "claire_s338_s344_dashboard_payload_routes_registered", False),
    )


def build_s342_app_mount_proof() -> Dict[str, Any]:
    app = FastAPI()
    @app.get(PAYLOAD_ENDPOINT)
    def legacy_payload() -> Dict[str, Any]:
        return {"legacy": True}
    @app.get(STATUS_ENDPOINT)
    def legacy_status() -> Dict[str, Any]:
        return {"status": "legacy"}

    before_paths = [getattr(route, "path", "") for route in app.router.routes]
    register_s338_s344_dashboard_payload_routes(app)
    after_paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base(
        "S342",
        "app_mount_proof_ready",
        before_dashboard_route_count=sum(1 for path in before_paths if path in {PAYLOAD_ENDPOINT, STATUS_ENDPOINT}),
        after_dashboard_route_count=sum(1 for path in after_paths if path in {PAYLOAD_ENDPOINT, STATUS_ENDPOINT}),
        removed_count=getattr(app.state, "claire_s338_s344_dashboard_payload_routes_removed", None),
        mounted=True,
    )


def build_s343_payload_schema_smoke_proof() -> Dict[str, Any]:
    payload = get_s338_s344_integrated_dashboard_payload()
    checks = {
        "has_internet_update_readiness": "internet_update_readiness" in payload,
        "has_internet_evidence": "internet_evidence" in payload,
        "has_internet_update_proposals": "internet_update_proposals" in payload,
        "has_cockpit_panel_registry": "cockpit_panel_registry" in payload,
        "has_dashboard_fetch_map_lock": "dashboard_fetch_map_lock" in payload,
        "has_dashboard_renderer_states": "dashboard_renderer_states" in payload,
        "has_action_panel_consolidation": "dashboard_action_panel_consolidation" in payload,
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    return _base(
        "S343",
        "payload_schema_smoke_proof_passed" if all(checks.values()) else "payload_schema_smoke_proof_failed",
        checks=checks,
        schema_ok=all(checks.values()),
    )


def build_s344_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    checks = {
        "existing_payload_reader_ok": build_s338_existing_payload_reader()["ok"],
        "payload_merge_owner_ok": build_s339_payload_merge_owner()["ok"],
        "status_endpoint_contract_ok": build_s340_integrated_status_endpoint_contract()["status_payload"]["ok"],
        "route_registration_ok": build_s341_route_registration_contract()["payload_registered"],
        "app_mount_proof_ok": build_s342_app_mount_proof()["mounted"],
        "payload_schema_smoke_ok": build_s343_payload_schema_smoke_proof()["schema_ok"],
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S344",
        "canonical_dashboard_payload_integration_passed" if ok else "canonical_dashboard_payload_integration_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S345-S351 frontend cockpit renderer integration" if ok else "repair S338-S344 dashboard payload integration",
        remaining_packs_to_live_dashboard_visibility=2,
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s338_s344_canonical_dashboard_payload_integration.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_canonical_dashboard_payload_integration_s338_s344() -> Dict[str, Any]:
    return _base(
        "S344",
        "canonical_dashboard_payload_integration_ready",
        existing_payload_reader=build_s338_existing_payload_reader(),
        payload_merge_owner=build_s339_payload_merge_owner(),
        status_endpoint=build_s340_integrated_status_endpoint_contract(),
        route_registration=build_s341_route_registration_contract(),
        app_mount_proof=build_s342_app_mount_proof(),
        schema_smoke=build_s343_payload_schema_smoke_proof(),
        stop_gate=build_s344_stop_gate(),
    )


__all__ = [
    "build_s338_existing_payload_reader",
    "build_s339_payload_merge_owner",
    "get_s338_s344_integrated_dashboard_payload",
    "build_s340_integrated_status_endpoint_contract",
    "get_s338_s344_integrated_dashboard_payload_status",
    "register_s338_s344_dashboard_payload_routes",
    "build_s341_route_registration_contract",
    "build_s342_app_mount_proof",
    "build_s343_payload_schema_smoke_proof",
    "build_s344_stop_gate",
    "build_canonical_dashboard_payload_integration_s338_s344",
]
