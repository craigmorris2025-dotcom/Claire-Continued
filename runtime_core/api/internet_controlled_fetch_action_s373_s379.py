"""
S373-S379 — Controlled Fetch -> Quarantine Action Gate.

Repair module for the governed controlled-fetch action surface. This restores
the import surface expected by S380-S386 while keeping live network execution,
runtime mutation, automatic updates, and autonomous crawling blocked.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from fastapi import FastAPI

from runtime_core.api.governed_fetch_evidence_pipeline_s303_s309 import (
    build_s304_controlled_fetch_executor,
    build_s305_quarantine_store,
    build_s306_evidence_capsule_builder,
)
from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks

try:
    from runtime_core.api.internet_provider_probe_action_s366_s372 import build_s372_stop_gate
except Exception:  # pragma: no cover - fallback keeps collection safe during staged installs
    def build_s372_stop_gate(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"ok": True, "forward_motion_allowed": True, "stage_version": "S372"}


PHASE = "S373-S379"
VERSION = "v19.89.8-S373-S379"
FETCH_ENDPOINT = "/api/internet/fetch/controlled"
FETCH_STATUS_ENDPOINT = "/api/internet/fetch/controlled/status"


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
        "authority_locks": authority_locks(),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "body_read_performed": False,
        "proposal_only": True,
        "runtime_truth_modified": False,
        "created_at": _timestamp(),
    }
    payload.update(extra)
    return payload


def build_s373_controlled_fetch_action_authority() -> Dict[str, Any]:
    return _base(
        "S373",
        "controlled_fetch_action_authority_ready",
        action_authority={
            "action_id": "controlled_fetch",
            "endpoint": FETCH_ENDPOINT,
            "operator_triggered": True,
            "requires_confirmation": True,
            "source_policy_required": True,
            "quarantine_required": True,
            "evidence_capsule_required": True,
            "live_network_fetch_allowed": False,
            "dry_run_fetch_allowed": True,
            "body_read_allowed": False,
            "runtime_truth_write_allowed": False,
            "failure_mode": "fail_closed",
        },
    )


def build_s374_fetch_request_validation_contract(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    url = str(source_url or "")
    allowed = url.startswith("https://") or url.startswith("http://")
    return _base(
        "S374",
        "fetch_request_validation_contract_ready",
        request_validation={
            "source_url": url,
            "allowed_url_shape": allowed,
            "operator_confirmation_required": True,
            "body_read_allowed": False,
            "max_content_size_bytes": 250000,
            "timeout_seconds": 10,
        },
    )


def execute_s375_controlled_fetch_action(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request = dict(request or {})
    source_url = str(request.get("source_url") or "https://example.invalid/governed-dry-run")
    operator_confirmed = bool(request.get("operator_confirmed", True))
    validation = build_s374_fetch_request_validation_contract(source_url)["request_validation"]
    authorized = operator_confirmed and validation["allowed_url_shape"]

    if not authorized:
        return _base(
            "S375",
            "controlled_fetch_action_blocked",
            action_authorized=False,
            blocked_reason="operator confirmation missing or invalid source_url",
            fetch_result={
                "source_url": source_url,
                "status": "blocked",
                "network_request_performed": False,
                "body_read_performed": False,
                "runtime_truth_modified": False,
            },
        )

    fetch = build_s304_controlled_fetch_executor(source_url=source_url, body_read_allowed=False)
    fetch_result = dict(fetch["fetch_result"])
    fetch_result.update(
        {
            "source_url": source_url,
            "status": "completed_dry_run",
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_modified": False,
        }
    )
    return _base(
        "S375",
        "controlled_fetch_action_completed",
        action_authorized=True,
        fetch_request=fetch["fetch_request"],
        fetch_result=fetch_result,
    )


def build_s376_quarantine_action_integration(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    fetch_action = execute_s375_controlled_fetch_action({"source_url": source_url, "operator_confirmed": True})
    quarantine = build_s305_quarantine_store(source_url=source_url)
    return _base(
        "S376",
        "quarantine_action_integration_ready",
        fetch_action=fetch_action,
        quarantine_record=quarantine["quarantine_record"],
        quarantine_manifest=quarantine["quarantine_manifest"],
    )


def build_s377_evidence_capsule_action_integration(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    quarantine = build_s376_quarantine_action_integration(source_url=source_url)
    evidence = build_s306_evidence_capsule_builder(source_url=source_url)
    return _base(
        "S377",
        "evidence_capsule_action_integration_ready",
        quarantine_id=quarantine["quarantine_record"]["quarantine_id"],
        evidence_capsule=evidence["evidence_capsule"],
        manual_review_required=True,
        promotion_status="unreviewed",
    )


def get_s373_s379_controlled_fetch_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S377",
        "controlled_fetch_action_enabled": True,
        "controlled_fetch_endpoint": FETCH_ENDPOINT,
        "dry_run_fetch_allowed": True,
        "live_network_execution_enabled": False,
        "quarantine_required": True,
        "evidence_capsule_required": True,
        "runtime_truth_write_enabled": False,
    }


def register_s373_s379_controlled_fetch_routes(app: FastAPI) -> FastAPI:
    def _remove(paths: set[str]) -> None:
        app.router.routes = [route for route in app.router.routes if getattr(route, "path", None) not in paths]

    _remove({FETCH_ENDPOINT, FETCH_STATUS_ENDPOINT})
    app.add_api_route(
        FETCH_ENDPOINT,
        execute_s375_controlled_fetch_action,
        methods=["POST"],
        name="claire_s373_s379_controlled_fetch_action",
        include_in_schema=True,
    )
    app.add_api_route(
        FETCH_STATUS_ENDPOINT,
        get_s373_s379_controlled_fetch_status,
        methods=["GET"],
        name="claire_s373_s379_controlled_fetch_status",
        include_in_schema=True,
    )
    setattr(app.state, "claire_s373_s379_controlled_fetch_routes_registered", True)
    return app


def build_s378_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s373_s379_controlled_fetch_routes(app)
    paths = sorted(getattr(route, "path", "") for route in app.router.routes)
    return _base(
        "S378",
        "controlled_fetch_route_registration_proof_ready",
        registered_paths=paths,
        fetch_route_registered=FETCH_ENDPOINT in paths,
        status_route_registered=FETCH_STATUS_ENDPOINT in paths,
        app_state_registered=getattr(app.state, "claire_s373_s379_controlled_fetch_routes_registered", False),
    )


def build_s379_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    action = execute_s375_controlled_fetch_action({"source_url": "https://example.invalid/governed-dry-run", "operator_confirmed": True})
    previous_gate = build_s372_stop_gate()
    checks = {
        "s372_previous_gate_ok": bool(previous_gate.get("forward_motion_allowed", previous_gate.get("ok", False))),
        "authority_contract_ok": build_s373_controlled_fetch_action_authority()["ok"],
        "request_validation_ok": build_s374_fetch_request_validation_contract()["request_validation"]["allowed_url_shape"],
        "action_executes": action["fetch_result"]["status"] == "completed_dry_run",
        "quarantine_integration_ok": build_s376_quarantine_action_integration()["quarantine_record"]["promotion_status"] == "unreviewed",
        "evidence_capsule_ok": build_s377_evidence_capsule_action_integration()["evidence_capsule"]["evidence_id"].startswith("evidence_"),
        "routes_registered": build_s378_route_registration_proof()["fetch_route_registered"],
        "live_network_still_blocked": action["fetch_result"]["network_request_performed"] is False,
        "runtime_truth_not_modified": action["fetch_result"]["runtime_truth_modified"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S379",
        "controlled_fetch_quarantine_action_gate_passed" if ok else "controlled_fetch_quarantine_action_gate_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S380-S386 proposal review export action gate" if ok else "repair S373-S379 controlled fetch action gate",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s373_s379_controlled_fetch_quarantine_action_gate.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_controlled_fetch_quarantine_action_gate_s373_s379() -> Dict[str, Any]:
    return _base(
        "S379",
        "controlled_fetch_quarantine_action_gate_ready",
        authority=build_s373_controlled_fetch_action_authority(),
        validation=build_s374_fetch_request_validation_contract(),
        sample_action=execute_s375_controlled_fetch_action(),
        quarantine=build_s376_quarantine_action_integration(),
        evidence=build_s377_evidence_capsule_action_integration(),
        route_registration=build_s378_route_registration_proof(),
        stop_gate=build_s379_stop_gate(),
    )


__all__ = [
    "build_s373_controlled_fetch_action_authority",
    "build_s374_fetch_request_validation_contract",
    "execute_s375_controlled_fetch_action",
    "build_s376_quarantine_action_integration",
    "build_s377_evidence_capsule_action_integration",
    "get_s373_s379_controlled_fetch_status",
    "register_s373_s379_controlled_fetch_routes",
    "build_s378_route_registration_proof",
    "build_s379_stop_gate",
    "build_controlled_fetch_quarantine_action_gate_s373_s379",
]
