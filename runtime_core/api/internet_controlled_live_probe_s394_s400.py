"""
S394-S400 — Controlled Live Provider Probe Executor.

Adds a real governed probe endpoint. By default it completes as a dry-run.
If future operator request and env toggle allow it, it may perform one metadata
request only. Tests do not perform network requests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import urllib.request
import urllib.error

from fastapi import FastAPI

from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks
from runtime_core.api.internet_live_provider_authority_s387_s393 import (
    LIVE_TOGGLE_ENV,
    build_s388_live_toggle_reader,
    build_s389_source_allowlist_gate,
    build_s390_rate_limit_timeout_contract,
    build_s393_stop_gate,
)


PHASE = "S394-S400"
VERSION = "v19.89.8-S394-S400"
PROBE_ENDPOINT = "/api/internet/live-provider/probe"
PROBE_STATUS_ENDPOINT = "/api/internet/live-provider/probe/status"


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
        "body_read_performed": False,
        "runtime_truth_modified": False,
        "created_at": _now(),
    }
    payload.update(extra)
    return payload


def build_s394_probe_executor_authority() -> Dict[str, Any]:
    return _base(
        "S394",
        "controlled_live_probe_executor_authority_ready",
        authority={
            "endpoint": PROBE_ENDPOINT,
            "operator_triggered": True,
            "env_toggle_required": LIVE_TOGGLE_ENV,
            "allow_live_execution_field_required": True,
            "metadata_only": True,
            "body_read_allowed": False,
            "network_default": "blocked",
        },
    )


def build_s395_probe_request_validation(source_url: str = "https://example.com", allow_live_execution: bool = False) -> Dict[str, Any]:
    toggle = build_s388_live_toggle_reader()
    gate = build_s389_source_allowlist_gate(source_url)
    authorized_live = (
        allow_live_execution is True
        and toggle["toggle"]["controlled_live_provider_allowed"] is True
        and gate["source_gate"]["allowed_for_controlled_probe"] is True
    )
    return _base(
        "S395",
        "controlled_live_probe_request_validation_ready",
        validation={
            "source_url": source_url,
            "allow_live_execution_requested": allow_live_execution,
            "env_toggle_allows_live": toggle["toggle"]["controlled_live_provider_allowed"],
            "source_allowed": gate["source_gate"]["allowed_for_controlled_probe"],
            "authorized_live_execution": authorized_live,
            "dry_run_mode": not authorized_live,
        },
    )


def _metadata_probe(source_url: str, timeout: int) -> Dict[str, Any]:
    request = urllib.request.Request(source_url, method="HEAD")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return {
            "status_code": getattr(response, "status", None),
            "final_url": response.geturl(),
            "content_type": response.headers.get("content-type"),
            "content_length": response.headers.get("content-length"),
            "headers_subset": {
                "server": response.headers.get("server"),
                "date": response.headers.get("date"),
            },
        }


def execute_s396_controlled_live_probe(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request = dict(request or {})
    source_url = str(request.get("source_url") or "https://example.com")
    allow_live = bool(request.get("allow_live_execution", False))
    validation = build_s395_probe_request_validation(source_url, allow_live)["validation"]
    timeout = build_s390_rate_limit_timeout_contract()["rate_limit"]["timeout_seconds"]

    if not validation["authorized_live_execution"]:
        return _base(
            "S396",
            "controlled_live_probe_completed_dry_run",
            probe_result={
                "source_url": source_url,
                "mode": "dry_run",
                "network_request_performed": False,
                "body_read_performed": False,
                "runtime_truth_modified": False,
                "metadata": {
                    "status_code": None,
                    "final_url": source_url,
                    "content_type": "not_fetched_dry_run",
                    "content_length": None,
                },
            },
        )

    try:
        metadata = _metadata_probe(source_url, timeout=timeout)
        status = "controlled_live_probe_completed_metadata_only"
        error = None
        performed = True
    except Exception as exc:
        metadata = {
            "status_code": None,
            "final_url": source_url,
            "content_type": None,
            "content_length": None,
        }
        status = "controlled_live_probe_failed_closed"
        error = repr(exc)
        performed = False

    return _base(
        "S396",
        status,
        probe_result={
            "source_url": source_url,
            "mode": "live_metadata_only",
            "network_request_performed": performed,
            "body_read_performed": False,
            "runtime_truth_modified": False,
            "metadata": metadata,
            "error": error,
        },
    )


def build_s397_probe_quarantine_draft() -> Dict[str, Any]:
    probe = execute_s396_controlled_live_probe({"source_url": "https://example.com", "allow_live_execution": False})
    return _base(
        "S397",
        "probe_quarantine_draft_ready",
        quarantine_draft={
            "quarantine_required": True,
            "promotion_status": "unreviewed",
            "probe_result": probe["probe_result"],
            "runtime_truth_write": "blocked",
        },
    )


def build_s398_dashboard_action_patch() -> Dict[str, Any]:
    return _base(
        "S398",
        "controlled_live_probe_dashboard_action_patch_ready",
        action_registry_patch={
            "controlled_live_provider_probe": {
                "visible": True,
                "enabled": True,
                "endpoint": PROBE_ENDPOINT,
                "method": "POST",
                "requires_confirmation": True,
                "default_mode": "dry_run_until_env_toggle_enabled",
            }
        },
    )


def get_s394_s400_live_probe_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S398",
        "controlled_live_probe_endpoint": PROBE_ENDPOINT,
        "default_mode": "dry_run",
        "body_read_allowed": False,
        "runtime_truth_write_enabled": False,
    }


def register_s394_s400_live_probe_routes(app: FastAPI) -> FastAPI:
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in {PROBE_ENDPOINT, PROBE_STATUS_ENDPOINT}]
    app.add_api_route(PROBE_ENDPOINT, execute_s396_controlled_live_probe, methods=["POST"], name="claire_s394_s400_live_probe", include_in_schema=True)
    app.add_api_route(PROBE_STATUS_ENDPOINT, get_s394_s400_live_probe_status, methods=["GET"], name="claire_s394_s400_live_probe_status", include_in_schema=True)
    setattr(app.state, "claire_s394_s400_live_probe_routes_registered", True)
    return app


def build_s399_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s394_s400_live_probe_routes(app)
    paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base(
        "S399",
        "controlled_live_probe_route_registration_ready",
        probe_route_registered=PROBE_ENDPOINT in paths,
        status_route_registered=PROBE_STATUS_ENDPOINT in paths,
    )


def build_s400_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    probe = execute_s396_controlled_live_probe({"source_url": "https://example.com", "allow_live_execution": False})
    checks = {
        "s393_previous_gate_ok": build_s393_stop_gate()["forward_motion_allowed"],
        "authority_ok": build_s394_probe_executor_authority()["ok"],
        "validation_defaults_dry_run": build_s395_probe_request_validation()["validation"]["dry_run_mode"] is True,
        "probe_dry_run_ok": probe["probe_result"]["mode"] == "dry_run",
        "no_network_in_default_probe": probe["probe_result"]["network_request_performed"] is False,
        "body_read_blocked": probe["probe_result"]["body_read_performed"] is False,
        "quarantine_draft_ok": build_s397_probe_quarantine_draft()["quarantine_draft"]["promotion_status"] == "unreviewed",
        "route_registered": build_s399_route_registration_proof()["probe_route_registered"],
    }
    ok = all(checks.values())
    payload = _base(
        "S400",
        "controlled_live_probe_executor_gate_passed" if ok else "controlled_live_probe_executor_gate_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S401-S407 controlled live metadata quarantine evidence" if ok else "repair S394-S400",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s394_s400_controlled_live_probe_executor.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_controlled_live_probe_executor_s394_s400() -> Dict[str, Any]:
    return _base(
        "S400",
        "controlled_live_probe_executor_ready",
        authority=build_s394_probe_executor_authority(),
        validation=build_s395_probe_request_validation(),
        sample_probe=execute_s396_controlled_live_probe(),
        quarantine_draft=build_s397_probe_quarantine_draft(),
        dashboard_action=build_s398_dashboard_action_patch(),
        route_registration=build_s399_route_registration_proof(),
        stop_gate=build_s400_stop_gate(),
    )


__all__ = [
    "build_s394_probe_executor_authority",
    "build_s395_probe_request_validation",
    "execute_s396_controlled_live_probe",
    "build_s397_probe_quarantine_draft",
    "build_s398_dashboard_action_patch",
    "get_s394_s400_live_probe_status",
    "register_s394_s400_live_probe_routes",
    "build_s399_route_registration_proof",
    "build_s400_stop_gate",
    "build_controlled_live_probe_executor_s394_s400",
]
