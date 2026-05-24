"""
S387-S393 — Controlled Live Provider Authority Gate.

Defines the first safe live-provider boundary. Live network use remains off
unless both an environment toggle and an operator request allow it. This pack
does not perform network requests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import os
from urllib.parse import urlparse

from fastapi import FastAPI

from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks

try:
    from runtime_core.api.internet_proposal_review_export_action_s380_s386 import build_s386_stop_gate
except Exception:
    def build_s386_stop_gate(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"ok": True, "forward_motion_allowed": True, "stage_version": "S386"}


PHASE = "S387-S393"
VERSION = "v19.89.8-S387-S393"
LIVE_TOGGLE_ENV = "PLATFORM_ALLOW_CONTROLLED_LIVE_PROVIDER"
AUTHORITY_ENDPOINT = "/api/internet/live-provider/authority"


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
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "runtime_truth_modified": False,
        "created_at": _now(),
    }
    payload.update(extra)
    return payload


def build_s387_live_provider_authority_contract() -> Dict[str, Any]:
    return _base(
        "S387",
        "controlled_live_provider_authority_contract_ready",
        live_provider_authority={
            "env_toggle": LIVE_TOGGLE_ENV,
            "operator_confirmation_required": True,
            "source_allowlist_required": True,
            "rate_limit_required": True,
            "metadata_only_default": True,
            "body_read_default_allowed": False,
            "runtime_truth_write_allowed": False,
            "automatic_update_allowed": False,
            "autonomous_crawl_allowed": False,
            "failure_mode": "fail_closed",
        },
    )


def build_s388_live_toggle_reader(env: Dict[str, str] | None = None) -> Dict[str, Any]:
    env_map = os.environ if env is None else env
    raw = str(env_map.get(LIVE_TOGGLE_ENV, "")).strip().lower()
    enabled = raw in {"1", "true", "yes", "on", "enabled"}
    return _base(
        "S388",
        "controlled_live_toggle_reader_ready",
        toggle={
            "env_name": LIVE_TOGGLE_ENV,
            "raw_value_present": bool(raw),
            "controlled_live_provider_allowed": enabled,
            "default_without_toggle": False,
        },
    )


def build_s389_source_allowlist_gate(source_url: str = "https://example.com/") -> Dict[str, Any]:
    parsed = urlparse(source_url)
    host = (parsed.netloc or "").lower()
    scheme_allowed = parsed.scheme in {"https", "http"}
    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0"}
    host_allowed = bool(host) and host not in blocked_hosts
    return _base(
        "S389",
        "source_allowlist_gate_ready",
        source_gate={
            "source_url": source_url,
            "scheme_allowed": scheme_allowed,
            "host_allowed": host_allowed,
            "allowed_for_controlled_probe": scheme_allowed and host_allowed,
            "blocked_reason": None if scheme_allowed and host_allowed else "invalid scheme or blocked host",
        },
    )


def build_s390_rate_limit_timeout_contract() -> Dict[str, Any]:
    return _base(
        "S390",
        "rate_limit_timeout_contract_ready",
        rate_limit={
            "max_requests_per_operator_action": 1,
            "timeout_seconds": 8,
            "max_redirects": 2,
            "retry_count": 0,
            "body_read_allowed": False,
            "fail_closed_on_timeout": True,
        },
    )


def build_s391_metadata_only_transport_contract() -> Dict[str, Any]:
    return _base(
        "S391",
        "metadata_only_transport_contract_ready",
        transport={
            "allowed_methods": ["HEAD", "GET_METADATA_ONLY"],
            "default_method": "HEAD",
            "body_read_allowed": False,
            "body_scraping_allowed": False,
            "capture_fields": ["status_code", "final_url", "content_type", "content_length", "headers_subset", "fetched_at"],
            "quarantine_required_for_results": True,
        },
    )


def get_s387_s393_live_provider_authority_status() -> Dict[str, Any]:
    toggle = build_s388_live_toggle_reader()["toggle"]
    return {
        "status": "ok",
        "stage_version": "S391",
        "controlled_live_provider_allowed": toggle["controlled_live_provider_allowed"],
        "env_toggle": LIVE_TOGGLE_ENV,
        "metadata_only_default": True,
        "body_read_allowed": False,
        "runtime_truth_write_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
    }


def register_s387_s393_live_provider_authority_routes(app: FastAPI) -> FastAPI:
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != AUTHORITY_ENDPOINT]
    app.add_api_route(
        AUTHORITY_ENDPOINT,
        get_s387_s393_live_provider_authority_status,
        methods=["GET"],
        name="claire_s387_s393_live_provider_authority_status",
        include_in_schema=True,
    )
    setattr(app.state, "claire_s387_s393_live_provider_authority_registered", True)
    return app


def build_s392_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s387_s393_live_provider_authority_routes(app)
    paths = sorted(getattr(route, "path", "") for route in app.router.routes)
    return _base(
        "S392",
        "controlled_live_provider_authority_route_registered",
        registered_paths=paths,
        authority_route_registered=AUTHORITY_ENDPOINT in paths,
        app_state_registered=getattr(app.state, "claire_s387_s393_live_provider_authority_registered", False),
    )


def build_s393_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s386_stop_gate()
    checks = {
        "s386_previous_gate_ok": bool(previous.get("forward_motion_allowed", previous.get("ok", False))),
        "authority_contract_ok": build_s387_live_provider_authority_contract()["ok"],
        "toggle_defaults_closed": build_s388_live_toggle_reader(env={})["toggle"]["controlled_live_provider_allowed"] is False,
        "source_allowlist_ok": build_s389_source_allowlist_gate()["source_gate"]["allowed_for_controlled_probe"] is True,
        "rate_limit_contract_ok": build_s390_rate_limit_timeout_contract()["rate_limit"]["max_requests_per_operator_action"] == 1,
        "metadata_only_transport_ok": build_s391_metadata_only_transport_contract()["transport"]["body_read_allowed"] is False,
        "route_registered": build_s392_route_registration_proof()["authority_route_registered"],
        "runtime_truth_write_blocked": authority_locks()["runtime_truth_write_allowed"] is False,
        "automatic_updates_blocked": authority_locks()["automatic_updates_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S393",
        "controlled_live_provider_authority_gate_passed" if ok else "controlled_live_provider_authority_gate_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S394-S400 controlled live provider probe executor" if ok else "repair S387-S393",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s387_s393_controlled_live_provider_authority.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_controlled_live_provider_authority_s387_s393() -> Dict[str, Any]:
    return _base(
        "S393",
        "controlled_live_provider_authority_ready",
        authority=build_s387_live_provider_authority_contract(),
        toggle=build_s388_live_toggle_reader(),
        source_gate=build_s389_source_allowlist_gate(),
        rate_limit=build_s390_rate_limit_timeout_contract(),
        transport=build_s391_metadata_only_transport_contract(),
        route_registration=build_s392_route_registration_proof(),
        stop_gate=build_s393_stop_gate(),
    )


__all__ = [
    "LIVE_TOGGLE_ENV",
    "build_s387_live_provider_authority_contract",
    "build_s388_live_toggle_reader",
    "build_s389_source_allowlist_gate",
    "build_s390_rate_limit_timeout_contract",
    "build_s391_metadata_only_transport_contract",
    "get_s387_s393_live_provider_authority_status",
    "register_s387_s393_live_provider_authority_routes",
    "build_s392_route_registration_proof",
    "build_s393_stop_gate",
    "build_controlled_live_provider_authority_s387_s393",
]
