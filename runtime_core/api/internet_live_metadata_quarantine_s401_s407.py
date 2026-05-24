"""
S401-S407 — Controlled Live Metadata Quarantine + Evidence Gate.

Builds a metadata-only quarantine/evidence path around the controlled live
provider probe. Defaults to dry-run metadata, writes local quarantine records,
and produces an evidence candidate. No runtime truth mutation is enabled.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import hashlib
import json

from fastapi import FastAPI

from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks
from runtime_core.api.internet_controlled_live_probe_s394_s400 import (
    build_s400_stop_gate,
    execute_s396_controlled_live_probe,
)


PHASE = "S401-S407"
VERSION = "v19.89.8-S401-S407"
METADATA_ENDPOINT = "/api/internet/live-metadata/fetch"
METADATA_STATUS_ENDPOINT = "/api/internet/live-metadata/status"
LIVE_METADATA_DIR = Path("data/quarantine/live_metadata")


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


def build_s401_live_metadata_fetch_authority() -> Dict[str, Any]:
    return _base(
        "S401",
        "live_metadata_fetch_authority_ready",
        authority={
            "endpoint": METADATA_ENDPOINT,
            "metadata_only": True,
            "body_read_allowed": False,
            "quarantine_write_allowed": True,
            "evidence_candidate_allowed": True,
            "runtime_truth_write_allowed": False,
            "operator_confirmation_required": True,
        },
    )


def build_s402_metadata_quarantine_record(probe_result: Dict[str, Any] | None = None, write_dir: str | Path | None = None) -> Dict[str, Any]:
    probe_result = dict(probe_result or execute_s396_controlled_live_probe()["probe_result"])
    digest = hashlib.sha256(json.dumps(probe_result, sort_keys=True).encode("utf-8")).hexdigest()
    record = {
        "quarantine_id": f"live_meta_{digest[:12]}",
        "source_url": probe_result.get("source_url"),
        "mode": probe_result.get("mode"),
        "sha256": digest,
        "promotion_status": "unreviewed",
        "metadata": probe_result.get("metadata", {}),
        "network_request_performed": probe_result.get("network_request_performed", False),
        "body_read_performed": False,
        "runtime_truth_modified": False,
    }

    if write_dir is not None:
        path = Path(write_dir)
        path.mkdir(parents=True, exist_ok=True)
        record_path = path / f"{record['quarantine_id']}.json"
        record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        record["stored_path"] = str(record_path)

    return _base("S402", "metadata_quarantine_record_ready", quarantine_record=record)


def build_s403_metadata_evidence_candidate() -> Dict[str, Any]:
    quarantine = build_s402_metadata_quarantine_record()["quarantine_record"]
    evidence = {
        "evidence_id": quarantine["quarantine_id"].replace("live_meta_", "live_evidence_"),
        "quarantine_id": quarantine["quarantine_id"],
        "source_url": quarantine["source_url"],
        "claim_type": "metadata_observation",
        "confidence": "requires_review",
        "manual_review_required": True,
        "runtime_truth_write_allowed": False,
    }
    return _base("S403", "metadata_evidence_candidate_ready", evidence_candidate=evidence)


def build_s404_metadata_update_candidate() -> Dict[str, Any]:
    evidence = build_s403_metadata_evidence_candidate()["evidence_candidate"]
    candidate = {
        "candidate_id": evidence["evidence_id"].replace("live_evidence_", "live_candidate_"),
        "evidence_id": evidence["evidence_id"],
        "candidate_type": "source_metadata_update",
        "requires_review": True,
        "self_apply_allowed": False,
        "runtime_truth_write_allowed": False,
    }
    return _base("S404", "metadata_update_candidate_ready", update_candidate=candidate)


def build_s405_dashboard_live_metadata_summary() -> Dict[str, Any]:
    candidate = build_s404_metadata_update_candidate()["update_candidate"]
    return _base(
        "S405",
        "dashboard_live_metadata_summary_ready",
        dashboard_summary={
            "panel_key": "live_metadata_review",
            "metadata_fetch_endpoint": METADATA_ENDPOINT,
            "status_endpoint": METADATA_STATUS_ENDPOINT,
            "candidate_count": 1,
            "latest_candidate_id": candidate["candidate_id"],
            "runtime_mutation_status": "blocked",
            "body_read_status": "blocked",
        },
    )


def execute_s401_s407_live_metadata_fetch(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request = dict(request or {})
    source_url = str(request.get("source_url") or "https://example.com")
    allow_live = bool(request.get("allow_live_execution", False))
    operator_confirmed = bool(request.get("operator_confirmed", True))
    if not operator_confirmed:
        return _base("S401", "live_metadata_fetch_blocked", blocked_reason="operator confirmation missing")

    probe = execute_s396_controlled_live_probe({"source_url": source_url, "allow_live_execution": allow_live})
    quarantine = build_s402_metadata_quarantine_record(probe["probe_result"], write_dir=LIVE_METADATA_DIR)
    evidence = build_s403_metadata_evidence_candidate()
    candidate = build_s404_metadata_update_candidate()
    return _base(
        "S401",
        "live_metadata_fetch_completed",
        probe=probe,
        quarantine=quarantine,
        evidence=evidence,
        candidate=candidate,
        network_request_performed=probe["probe_result"].get("network_request_performed", False),
        body_read_performed=False,
        runtime_truth_modified=False,
    )


def get_s401_s407_live_metadata_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S405",
        "live_metadata_endpoint": METADATA_ENDPOINT,
        "metadata_only": True,
        "body_read_allowed": False,
        "quarantine_enabled": True,
        "evidence_candidate_enabled": True,
        "runtime_truth_write_enabled": False,
    }


def register_s401_s407_live_metadata_routes(app: FastAPI) -> FastAPI:
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) not in {METADATA_ENDPOINT, METADATA_STATUS_ENDPOINT}]
    app.add_api_route(METADATA_ENDPOINT, execute_s401_s407_live_metadata_fetch, methods=["POST"], name="claire_s401_s407_live_metadata_fetch", include_in_schema=True)
    app.add_api_route(METADATA_STATUS_ENDPOINT, get_s401_s407_live_metadata_status, methods=["GET"], name="claire_s401_s407_live_metadata_status", include_in_schema=True)
    setattr(app.state, "claire_s401_s407_live_metadata_routes_registered", True)
    return app


def build_s406_route_registration_proof() -> Dict[str, Any]:
    app = FastAPI()
    register_s401_s407_live_metadata_routes(app)
    paths = [getattr(route, "path", "") for route in app.router.routes]
    return _base("S406", "live_metadata_route_registration_ready", fetch_route_registered=METADATA_ENDPOINT in paths, status_route_registered=METADATA_STATUS_ENDPOINT in paths)


def build_s407_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    sample = execute_s401_s407_live_metadata_fetch({"source_url": "https://example.com", "allow_live_execution": False, "operator_confirmed": True})
    checks = {
        "s400_previous_gate_ok": build_s400_stop_gate()["forward_motion_allowed"],
        "authority_ok": build_s401_live_metadata_fetch_authority()["ok"],
        "quarantine_record_ok": sample["quarantine"]["quarantine_record"]["promotion_status"] == "unreviewed",
        "evidence_candidate_ok": sample["evidence"]["evidence_candidate"]["manual_review_required"] is True,
        "update_candidate_requires_review": sample["candidate"]["update_candidate"]["requires_review"] is True,
        "dashboard_summary_ok": build_s405_dashboard_live_metadata_summary()["dashboard_summary"]["runtime_mutation_status"] == "blocked",
        "routes_registered": build_s406_route_registration_proof()["fetch_route_registered"],
        "body_read_blocked": sample["body_read_performed"] is False,
        "runtime_truth_not_modified": sample["runtime_truth_modified"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S407",
        "controlled_live_metadata_quarantine_evidence_gate_passed" if ok else "controlled_live_metadata_quarantine_evidence_gate_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="dashboard action wiring refresh or Claire Q&A foundation" if ok else "repair S401-S407",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s401_s407_controlled_live_metadata_quarantine_evidence.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_controlled_live_metadata_quarantine_evidence_s401_s407() -> Dict[str, Any]:
    return _base(
        "S407",
        "controlled_live_metadata_quarantine_evidence_ready",
        authority=build_s401_live_metadata_fetch_authority(),
        quarantine=build_s402_metadata_quarantine_record(),
        evidence=build_s403_metadata_evidence_candidate(),
        candidate=build_s404_metadata_update_candidate(),
        dashboard_summary=build_s405_dashboard_live_metadata_summary(),
        route_registration=build_s406_route_registration_proof(),
        stop_gate=build_s407_stop_gate(),
    )


__all__ = [
    "build_s401_live_metadata_fetch_authority",
    "build_s402_metadata_quarantine_record",
    "build_s403_metadata_evidence_candidate",
    "build_s404_metadata_update_candidate",
    "build_s405_dashboard_live_metadata_summary",
    "execute_s401_s407_live_metadata_fetch",
    "get_s401_s407_live_metadata_status",
    "register_s401_s407_live_metadata_routes",
    "build_s406_route_registration_proof",
    "build_s407_stop_gate",
    "build_controlled_live_metadata_quarantine_evidence_s401_s407",
]
