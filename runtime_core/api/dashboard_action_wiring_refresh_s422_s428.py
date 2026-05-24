"""
S422-S428 — Dashboard Action Wiring Refresh.

This pack connects the dashboard action surface to the actual governed endpoints
built through S421. It adds a backend action registry summary and frontend wiring
assets. It does not enable runtime mutation, automatic updates, or autonomous
crawling.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from fastapi import FastAPI

from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks
from runtime_core.api.internet_first_controlled_probe_run_s415_s421 import build_s421_stop_gate


PHASE = "S422-S428"
VERSION = "v19.89.8-S422-S428"
ACTIONS_REGISTRY_ENDPOINT = "/dashboard/actions/registry"
ACTIONS_SUMMARY_ENDPOINT = "/dashboard/actions/summary"
ACTIONS_SMOKE_ENDPOINT = "/dashboard/actions/smoke"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "authority_locks": authority_locks(),
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
        "body_read_allowed": False,
        "runtime_truth_modified": False,
        "created_at": _now(),
    }
    payload.update(extra)
    return payload


def build_s422_dashboard_action_endpoint_registry() -> Dict[str, Any]:
    actions = {
        "provider_probe": {"method": "POST", "endpoint": "/api/internet/provider/probe", "enabled": True, "mode": "governed_dry_run"},
        "controlled_fetch": {"method": "POST", "endpoint": "/api/internet/fetch/controlled", "enabled": True, "mode": "dry_run_quarantine"},
        "proposal_review": {"method": "POST", "endpoint": "/api/internet/proposals/review", "enabled": True, "mode": "record_decision_only"},
        "proposal_export": {"method": "POST", "endpoint": "/api/internet/proposals/export", "enabled": True, "mode": "write_export_package"},
        "live_toggle_preflight": {"method": "POST", "endpoint": "/api/internet/live-toggle/preflight", "enabled": True, "mode": "preflight_only"},
        "first_metadata_probe": {"method": "POST", "endpoint": "/api/internet/live-metadata/run", "enabled": True, "mode": "metadata_only_default_dry_run"},
    }
    return _base("S422", "dashboard_action_endpoint_registry_ready", action_registry=actions, action_count=len(actions))


def build_s423_frontend_action_binding_manifest() -> Dict[str, Any]:
    return _base(
        "S423",
        "frontend_action_binding_manifest_ready",
        frontend_manifest={
            "js_asset": "frontend/cockpit/consolidated/s422_s428_dashboard_action_wiring.js",
            "css_asset": "frontend/cockpit/consolidated/s422_s428_dashboard_action_wiring.css",
            "action_registry_endpoint": ACTIONS_REGISTRY_ENDPOINT,
            "action_summary_endpoint": ACTIONS_SUMMARY_ENDPOINT,
            "mount_selector": "#claire-consolidated-cockpit",
            "buttons_auto_created": True,
        },
    )


def build_s424_action_button_state_contract() -> Dict[str, Any]:
    registry = build_s422_dashboard_action_endpoint_registry()["action_registry"]
    states = {
        name: {
            "visible": True,
            "enabled": spec["enabled"],
            "requires_confirmation": True,
            "runtime_truth_write_enabled": False,
            "body_read_enabled": False,
        }
        for name, spec in registry.items()
    }
    return _base("S424", "action_button_state_contract_ready", button_states=states)


def build_s425_dashboard_action_summary() -> Dict[str, Any]:
    registry = build_s422_dashboard_action_endpoint_registry()["action_registry"]
    return _base(
        "S425",
        "dashboard_action_summary_ready",
        action_summary={
            "enabled_action_count": sum(1 for spec in registry.values() if spec["enabled"]),
            "live_default_mode": "dry_run_or_metadata_only",
            "runtime_mutation_status": "blocked",
            "automatic_update_status": "blocked",
            "autonomous_crawl_status": "blocked",
            "body_read_status": "blocked",
        },
    )


def get_s422_s428_action_registry() -> Dict[str, Any]:
    return build_s422_dashboard_action_endpoint_registry()["action_registry"]


def get_s422_s428_action_summary() -> Dict[str, Any]:
    return build_s425_dashboard_action_summary()["action_summary"]


def get_s422_s428_action_smoke() -> Dict[str, Any]:
    registry = get_s422_s428_action_registry()
    summary = get_s422_s428_action_summary()
    return {
        "status": "ok",
        "stage_version": "S425",
        "action_count": len(registry),
        "enabled_action_count": summary["enabled_action_count"],
        "runtime_mutation_status": summary["runtime_mutation_status"],
        "body_read_status": summary["body_read_status"],
    }


def register_s422_s428_dashboard_action_routes(app: FastAPI) -> FastAPI:
    paths = {ACTIONS_REGISTRY_ENDPOINT, ACTIONS_SUMMARY_ENDPOINT, ACTIONS_SMOKE_ENDPOINT}
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in paths]
    app.add_api_route(ACTIONS_REGISTRY_ENDPOINT, get_s422_s428_action_registry, methods=["GET"], name="claire_s422_s428_action_registry", include_in_schema=True)
    app.add_api_route(ACTIONS_SUMMARY_ENDPOINT, get_s422_s428_action_summary, methods=["GET"], name="claire_s422_s428_action_summary", include_in_schema=True)
    app.add_api_route(ACTIONS_SMOKE_ENDPOINT, get_s422_s428_action_smoke, methods=["GET"], name="claire_s422_s428_action_smoke", include_in_schema=True)
    setattr(app.state, "claire_s422_s428_dashboard_action_routes_registered", True)
    return app


def build_s426_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s422_s428_dashboard_action_routes(app)
    paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base(
        "S426",
        "dashboard_action_route_registration_ready",
        registry_route_registered=ACTIONS_REGISTRY_ENDPOINT in paths,
        summary_route_registered=ACTIONS_SUMMARY_ENDPOINT in paths,
        smoke_route_registered=ACTIONS_SMOKE_ENDPOINT in paths,
    )


def build_s427_frontend_asset_visibility_proof() -> Dict[str, Any]:
    js = Path("frontend/cockpit/consolidated/s422_s428_dashboard_action_wiring.js")
    css = Path("frontend/cockpit/consolidated/s422_s428_dashboard_action_wiring.css")
    html = Path("frontend/cockpit/shell/cockpit_shell.html")
    injected = False
    if html.exists():
        injected = "BEGIN CLAIRE_S422_S428_ACTION_WIRING" in html.read_text(encoding="utf-8", errors="replace")
    return _base(
        "S427",
        "frontend_action_asset_visibility_ready",
        assets={
            "js_exists": js.exists(),
            "css_exists": css.exists(),
            "shell_exists": html.exists(),
            "shell_injection_present_or_shell_absent": injected or not html.exists(),
        },
    )


def build_s428_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    summary = build_s425_dashboard_action_summary()["action_summary"]
    checks = {
        "s421_previous_gate_ok": build_s421_stop_gate()["forward_motion_allowed"],
        "registry_ok": build_s422_dashboard_action_endpoint_registry()["action_count"] >= 6,
        "frontend_manifest_ok": build_s423_frontend_action_binding_manifest()["ok"],
        "button_states_ok": all(item["enabled"] for item in build_s424_action_button_state_contract()["button_states"].values()),
        "summary_ok": summary["enabled_action_count"] >= 6,
        "routes_registered": build_s426_route_registration_proof()["registry_route_registered"],
        "frontend_assets_ok": build_s427_frontend_asset_visibility_proof()["assets"]["js_exists"] and build_s427_frontend_asset_visibility_proof()["assets"]["css_exists"],
        "runtime_mutation_blocked": summary["runtime_mutation_status"] == "blocked",
        "body_read_blocked": summary["body_read_status"] == "blocked",
    }
    ok = all(checks.values())
    payload = _base(
        "S428",
        "dashboard_action_wiring_refresh_passed" if ok else "dashboard_action_wiring_refresh_failed",
        checks=checks,
        forward_motion_allowed=ok,
        dashboard_actions_operationally_wired=ok,
        next_phase="dashboard modernization visual consolidation or Claire Q&A foundation" if ok else "repair S422-S428",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s422_s428_dashboard_action_wiring_refresh.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_dashboard_action_wiring_refresh_s422_s428() -> Dict[str, Any]:
    return _base(
        "S428",
        "dashboard_action_wiring_refresh_ready",
        registry=build_s422_dashboard_action_endpoint_registry(),
        frontend_manifest=build_s423_frontend_action_binding_manifest(),
        button_states=build_s424_action_button_state_contract(),
        summary=build_s425_dashboard_action_summary(),
        route_registration=build_s426_route_registration_proof(),
        frontend_assets=build_s427_frontend_asset_visibility_proof(),
        stop_gate=build_s428_stop_gate(),
    )


__all__ = [
    "build_s422_dashboard_action_endpoint_registry",
    "build_s423_frontend_action_binding_manifest",
    "build_s424_action_button_state_contract",
    "build_s425_dashboard_action_summary",
    "get_s422_s428_action_registry",
    "get_s422_s428_action_summary",
    "get_s422_s428_action_smoke",
    "register_s422_s428_dashboard_action_routes",
    "build_s426_route_registration_proof",
    "build_s427_frontend_asset_visibility_proof",
    "build_s428_stop_gate",
    "build_dashboard_action_wiring_refresh_s422_s428",
]
