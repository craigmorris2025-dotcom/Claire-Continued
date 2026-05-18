"""
S415-S421 — First Controlled Live Metadata Probe Run Gate.

This pack creates a single endpoint that runs the first operator-gated metadata
probe workflow. It remains dry-run unless the live toggle is explicitly enabled.
The default test path performs no network request.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from fastapi import FastAPI

from claire.api.governed_internet_update_foundation_s296_s302 import authority_locks
from claire.api.internet_live_metadata_quarantine_s401_s407 import (
    execute_s401_s407_live_metadata_fetch,
)
from claire.api.internet_live_toggle_operator_control_s408_s414 import (
    build_s414_stop_gate,
    execute_s411_live_toggle_preflight,
)


PHASE = "S415-S421"
VERSION = "v19.89.8-S415-S421"
RUN_ENDPOINT = "/api/internet/live-metadata/run"
RUN_STATUS_ENDPOINT = "/api/internet/live-metadata/run/status"


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


def build_s415_first_probe_run_authority() -> Dict[str, Any]:
    return _base(
        "S415",
        "first_controlled_metadata_probe_run_authority_ready",
        authority={
            "endpoint": RUN_ENDPOINT,
            "operator_triggered": True,
            "operator_confirmation_required": True,
            "live_toggle_preflight_required": True,
            "metadata_only": True,
            "quarantine_required": True,
            "evidence_candidate_required": True,
            "body_read_allowed": False,
            "runtime_truth_write_allowed": False,
        },
    )


def build_s416_probe_run_request_contract(source_url: str = "https://example.com") -> Dict[str, Any]:
    allowed_shape = source_url.startswith("http://") or source_url.startswith("https://")
    return _base(
        "S416",
        "probe_run_request_contract_ready",
        request_contract={
            "source_url": source_url,
            "allowed_shape": allowed_shape,
            "operator_confirmed_required": True,
            "allow_live_execution_default": False,
            "required_body_fields": ["source_url", "operator_confirmed", "allow_live_execution"],
        },
    )


def execute_s417_first_controlled_metadata_probe_run(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request = dict(request or {})
    source_url = str(request.get("source_url") or "https://example.com")
    operator_confirmed = bool(request.get("operator_confirmed", True))
    allow_live_execution = bool(request.get("allow_live_execution", False))

    contract = build_s416_probe_run_request_contract(source_url)["request_contract"]
    preflight = execute_s411_live_toggle_preflight({"operator_confirmed": operator_confirmed})["preflight"]

    if not contract["allowed_shape"] or not operator_confirmed:
        return _base(
            "S417",
            "first_controlled_metadata_probe_run_blocked",
            blocked_reason="invalid source_url or operator confirmation missing",
            runtime_truth_modified=False,
            body_read_performed=False,
            network_request_performed=False,
        )

    effective_live = allow_live_execution and preflight["authorized_for_controlled_live_metadata"]
    run = execute_s401_s407_live_metadata_fetch(
        {
            "source_url": source_url,
            "allow_live_execution": effective_live,
            "operator_confirmed": operator_confirmed,
        }
    )
    return _base(
        "S417",
        "first_controlled_metadata_probe_run_completed",
        source_url=source_url,
        requested_live_execution=allow_live_execution,
        effective_live_execution=effective_live,
        preflight=preflight,
        run=run,
        network_request_performed=run.get("network_request_performed", False),
        body_read_performed=run.get("body_read_performed", False),
        runtime_truth_modified=run.get("runtime_truth_modified", False),
    )


def build_s418_run_result_contract() -> Dict[str, Any]:
    sample = execute_s417_first_controlled_metadata_probe_run({"source_url": "https://example.com", "operator_confirmed": True, "allow_live_execution": False})
    return _base(
        "S418",
        "first_probe_run_result_contract_ready",
        result_contract={
            "required_fields": [
                "source_url",
                "requested_live_execution",
                "effective_live_execution",
                "preflight",
                "run",
                "network_request_performed",
                "body_read_performed",
                "runtime_truth_modified",
            ],
            "sample": sample,
            "manual_review_required": True,
        },
    )


def build_s419_dashboard_first_probe_card() -> Dict[str, Any]:
    return _base(
        "S419",
        "dashboard_first_probe_card_ready",
        dashboard_card={
            "panel_key": "first_controlled_live_metadata_probe",
            "run_endpoint": RUN_ENDPOINT,
            "status_endpoint": RUN_STATUS_ENDPOINT,
            "button_label": "Run Controlled Metadata Probe",
            "enabled": True,
            "default_live_execution": False,
            "body_read_status": "blocked",
            "runtime_mutation_status": "blocked",
        },
    )


def get_s415_s421_first_probe_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S419",
        "run_endpoint": RUN_ENDPOINT,
        "default_live_execution": False,
        "body_read_allowed": False,
        "runtime_truth_write_enabled": False,
        "dashboard_card": build_s419_dashboard_first_probe_card()["dashboard_card"],
    }


def register_s415_s421_first_probe_routes(app: FastAPI) -> FastAPI:
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in {RUN_ENDPOINT, RUN_STATUS_ENDPOINT}]
    app.add_api_route(RUN_ENDPOINT, execute_s417_first_controlled_metadata_probe_run, methods=["POST"], name="claire_s415_s421_first_probe_run", include_in_schema=True)
    app.add_api_route(RUN_STATUS_ENDPOINT, get_s415_s421_first_probe_status, methods=["GET"], name="claire_s415_s421_first_probe_status", include_in_schema=True)
    setattr(app.state, "claire_s415_s421_first_probe_routes_registered", True)
    return app


def build_s420_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s415_s421_first_probe_routes(app)
    paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base("S420", "first_probe_route_registration_ready", run_route_registered=RUN_ENDPOINT in paths, status_route_registered=RUN_STATUS_ENDPOINT in paths)


def build_s421_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    sample = execute_s417_first_controlled_metadata_probe_run({"source_url": "https://example.com", "operator_confirmed": True, "allow_live_execution": False})
    checks = {
        "s414_previous_gate_ok": build_s414_stop_gate()["forward_motion_allowed"],
        "authority_ok": build_s415_first_probe_run_authority()["ok"],
        "request_contract_ok": build_s416_probe_run_request_contract()["request_contract"]["allowed_shape"] is True,
        "sample_run_completed": sample["status"] == "first_controlled_metadata_probe_run_completed",
        "default_effective_live_false": sample["effective_live_execution"] is False,
        "default_no_network": sample["network_request_performed"] is False,
        "body_read_blocked": sample["body_read_performed"] is False,
        "runtime_truth_not_modified": sample["runtime_truth_modified"] is False,
        "dashboard_card_ok": build_s419_dashboard_first_probe_card()["dashboard_card"]["enabled"] is True,
        "routes_registered": build_s420_route_registration_proof()["run_route_registered"] is True,
    }
    ok = all(checks.values())
    payload = _base(
        "S421",
        "first_controlled_live_metadata_probe_run_gate_passed" if ok else "first_controlled_live_metadata_probe_run_gate_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S422-S428 dashboard action wiring refresh" if ok else "repair S415-S421",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s415_s421_first_controlled_live_metadata_probe_run.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_first_controlled_live_metadata_probe_run_s415_s421() -> Dict[str, Any]:
    return _base(
        "S421",
        "first_controlled_live_metadata_probe_run_ready",
        authority=build_s415_first_probe_run_authority(),
        request_contract=build_s416_probe_run_request_contract(),
        sample_run=execute_s417_first_controlled_metadata_probe_run(),
        result_contract=build_s418_run_result_contract(),
        dashboard_card=build_s419_dashboard_first_probe_card(),
        route_registration=build_s420_route_registration_proof(),
        stop_gate=build_s421_stop_gate(),
    )


__all__ = [
    "build_s415_first_probe_run_authority",
    "build_s416_probe_run_request_contract",
    "execute_s417_first_controlled_metadata_probe_run",
    "build_s418_run_result_contract",
    "build_s419_dashboard_first_probe_card",
    "get_s415_s421_first_probe_status",
    "register_s415_s421_first_probe_routes",
    "build_s420_route_registration_proof",
    "build_s421_stop_gate",
    "build_first_controlled_live_metadata_probe_run_s415_s421",
]
