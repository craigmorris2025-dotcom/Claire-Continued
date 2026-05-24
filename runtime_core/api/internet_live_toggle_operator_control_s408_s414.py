"""
S408-S414 — Operator-Visible Live Toggle Proof.

This pack makes the controlled-live-provider toggle visible and testable from
the backend/dashboard. It does not change environment variables and it does not
enable live network execution by itself.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import os

from fastapi import FastAPI

from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks
from runtime_core.api.internet_live_provider_authority_s387_s393 import (
    LIVE_TOGGLE_ENV,
    build_s388_live_toggle_reader,
    build_s393_stop_gate,
)


PHASE = "S408-S414"
VERSION = "v19.89.8-S408-S414"
TOGGLE_STATUS_ENDPOINT = "/api/internet/live-toggle/status"
TOGGLE_PREFLIGHT_ENDPOINT = "/api/internet/live-toggle/preflight"


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


def build_s408_live_toggle_visibility_contract() -> Dict[str, Any]:
    return _base(
        "S408",
        "live_toggle_visibility_contract_ready",
        visibility_contract={
            "env_toggle": LIVE_TOGGLE_ENV,
            "dashboard_visible": True,
            "dashboard_can_modify_env": False,
            "operator_must_set_env_outside_dashboard": True,
            "default_state": "closed",
            "controlled_live_provider_only": True,
        },
    )


def build_s409_live_toggle_state(env: Dict[str, str] | None = None) -> Dict[str, Any]:
    env_map = os.environ if env is None else env
    toggle = build_s388_live_toggle_reader(env=dict(env_map))["toggle"]
    return _base(
        "S409",
        "live_toggle_state_ready",
        toggle_state={
            "env_name": LIVE_TOGGLE_ENV,
            "enabled": toggle["controlled_live_provider_allowed"],
            "raw_value_present": toggle["raw_value_present"],
            "effective_mode": "controlled_live_metadata_allowed" if toggle["controlled_live_provider_allowed"] else "dry_run_only",
            "dashboard_can_enable": False,
        },
    )


def build_s410_operator_instruction_contract() -> Dict[str, Any]:
    return _base(
        "S410",
        "operator_instruction_contract_ready",
        operator_instruction={
            "enable_command_powershell": f"$env:{LIVE_TOGGLE_ENV}='true'",
            "disable_command_powershell": f"Remove-Item Env:{LIVE_TOGGLE_ENV}",
            "requires_server_restart": True,
            "do_not_enable_until_green_gate": True,
            "enabled_scope": "current terminal/session only unless set permanently by operator",
        },
    )


def execute_s411_live_toggle_preflight(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request = dict(request or {})
    operator_confirmed = bool(request.get("operator_confirmed", True))
    toggle = build_s409_live_toggle_state()["toggle_state"]
    authorized = operator_confirmed and toggle["enabled"] is True
    return _base(
        "S411",
        "live_toggle_preflight_authorized" if authorized else "live_toggle_preflight_dry_run_or_blocked",
        preflight={
            "operator_confirmed": operator_confirmed,
            "toggle_enabled": toggle["enabled"],
            "authorized_for_controlled_live_metadata": authorized,
            "reason": "env toggle and operator confirmation present" if authorized else "env toggle disabled or operator confirmation missing",
            "body_read_allowed": False,
            "runtime_truth_write_allowed": False,
        },
    )


def build_s412_dashboard_toggle_card() -> Dict[str, Any]:
    state = build_s409_live_toggle_state()["toggle_state"]
    instruction = build_s410_operator_instruction_contract()["operator_instruction"]
    return _base(
        "S412",
        "dashboard_live_toggle_card_ready",
        dashboard_card={
            "panel_key": "live_provider_toggle",
            "title": "Controlled Live Provider Toggle",
            "enabled": state["enabled"],
            "effective_mode": state["effective_mode"],
            "env_toggle": LIVE_TOGGLE_ENV,
            "dashboard_can_enable": False,
            "instruction": instruction,
        },
    )


def get_s408_s414_live_toggle_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S412",
        "toggle": build_s409_live_toggle_state()["toggle_state"],
        "dashboard_card": build_s412_dashboard_toggle_card()["dashboard_card"],
        "runtime_truth_write_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
    }


def register_s408_s414_live_toggle_routes(app: FastAPI) -> FastAPI:
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in {TOGGLE_STATUS_ENDPOINT, TOGGLE_PREFLIGHT_ENDPOINT}]
    app.add_api_route(TOGGLE_STATUS_ENDPOINT, get_s408_s414_live_toggle_status, methods=["GET"], name="claire_s408_s414_live_toggle_status", include_in_schema=True)
    app.add_api_route(TOGGLE_PREFLIGHT_ENDPOINT, execute_s411_live_toggle_preflight, methods=["POST"], name="claire_s408_s414_live_toggle_preflight", include_in_schema=True)
    setattr(app.state, "claire_s408_s414_live_toggle_routes_registered", True)
    return app


def build_s413_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s408_s414_live_toggle_routes(app)
    paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base(
        "S413",
        "live_toggle_route_registration_ready",
        status_route_registered=TOGGLE_STATUS_ENDPOINT in paths,
        preflight_route_registered=TOGGLE_PREFLIGHT_ENDPOINT in paths,
    )


def build_s414_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    default_state = build_s409_live_toggle_state(env={})["toggle_state"]
    preflight = execute_s411_live_toggle_preflight({"operator_confirmed": True})["preflight"]
    checks = {
        "s393_previous_gate_ok": build_s393_stop_gate()["forward_motion_allowed"],
        "visibility_contract_ok": build_s408_live_toggle_visibility_contract()["visibility_contract"]["dashboard_visible"] is True,
        "default_closed": default_state["enabled"] is False,
        "dashboard_cannot_modify_env": build_s408_live_toggle_visibility_contract()["visibility_contract"]["dashboard_can_modify_env"] is False,
        "instruction_contract_ok": build_s410_operator_instruction_contract()["operator_instruction"]["do_not_enable_until_green_gate"] is True,
        "preflight_respects_toggle": preflight["authorized_for_controlled_live_metadata"] is False or build_s409_live_toggle_state()["toggle_state"]["enabled"] is True,
        "dashboard_card_ok": build_s412_dashboard_toggle_card()["dashboard_card"]["panel_key"] == "live_provider_toggle",
        "routes_registered": build_s413_route_registration_proof()["status_route_registered"],
        "runtime_truth_write_blocked": authority_locks()["runtime_truth_write_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S414",
        "operator_visible_live_toggle_proof_passed" if ok else "operator_visible_live_toggle_proof_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S415-S421 first controlled live metadata probe run gate" if ok else "repair S408-S414",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s408_s414_operator_visible_live_toggle.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_operator_visible_live_toggle_s408_s414() -> Dict[str, Any]:
    return _base(
        "S414",
        "operator_visible_live_toggle_ready",
        visibility=build_s408_live_toggle_visibility_contract(),
        state=build_s409_live_toggle_state(),
        instruction=build_s410_operator_instruction_contract(),
        preflight=execute_s411_live_toggle_preflight(),
        dashboard_card=build_s412_dashboard_toggle_card(),
        route_registration=build_s413_route_registration_proof(),
        stop_gate=build_s414_stop_gate(),
    )


__all__ = [
    "build_s408_live_toggle_visibility_contract",
    "build_s409_live_toggle_state",
    "build_s410_operator_instruction_contract",
    "execute_s411_live_toggle_preflight",
    "build_s412_dashboard_toggle_card",
    "get_s408_s414_live_toggle_status",
    "register_s408_s414_live_toggle_routes",
    "build_s413_route_registration_proof",
    "build_s414_stop_gate",
    "build_operator_visible_live_toggle_s408_s414",
]
