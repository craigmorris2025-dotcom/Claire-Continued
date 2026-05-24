from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.internet_live_metadata_quarantine_s401_s407 import (
    build_controlled_live_metadata_quarantine_evidence_s401_s407,
    build_s401_live_metadata_fetch_authority,
    build_s402_metadata_quarantine_record,
    build_s403_metadata_evidence_candidate,
    build_s404_metadata_update_candidate,
    build_s405_dashboard_live_metadata_summary,
    build_s406_route_registration_proof,
    build_s407_stop_gate,
    execute_s401_s407_live_metadata_fetch,
    register_s401_s407_live_metadata_routes,
)


def test_s401_live_metadata_authority_is_metadata_only():
    payload = build_s401_live_metadata_fetch_authority()
    assert payload["stage_version"] == "S401"
    assert payload["authority"]["metadata_only"] is True
    assert payload["authority"]["body_read_allowed"] is False


def test_s402_quarantine_record_writes_when_requested(tmp_path):
    payload = build_s402_metadata_quarantine_record(write_dir=tmp_path)
    record = payload["quarantine_record"]
    assert payload["stage_version"] == "S402"
    assert record["promotion_status"] == "unreviewed"
    assert "stored_path" in record


def test_s403_evidence_candidate_requires_review():
    payload = build_s403_metadata_evidence_candidate()
    evidence = payload["evidence_candidate"]
    assert payload["stage_version"] == "S403"
    assert evidence["manual_review_required"] is True
    assert evidence["runtime_truth_write_allowed"] is False


def test_s404_update_candidate_requires_review():
    payload = build_s404_metadata_update_candidate()
    candidate = payload["update_candidate"]
    assert payload["stage_version"] == "S404"
    assert candidate["requires_review"] is True
    assert candidate["self_apply_allowed"] is False


def test_s405_dashboard_summary_blocks_mutation():
    payload = build_s405_dashboard_live_metadata_summary()
    summary = payload["dashboard_summary"]
    assert payload["stage_version"] == "S405"
    assert summary["runtime_mutation_status"] == "blocked"
    assert summary["body_read_status"] == "blocked"


def test_s406_routes_work(tmp_path, monkeypatch):
    import runtime_core.api.internet_live_metadata_quarantine_s401_s407 as module

    monkeypatch.setattr(module, "LIVE_METADATA_DIR", tmp_path)
    app = FastAPI()
    module.register_s401_s407_live_metadata_routes(app)
    client = TestClient(app)
    response = client.post("/api/internet/live-metadata/fetch", json={"source_url": "https://example.com", "allow_live_execution": False, "operator_confirmed": True})
    assert response.status_code == 200
    assert response.json()["body_read_performed"] is False
    status = client.get("/api/internet/live-metadata/status")
    assert status.status_code == 200
    assert status.json()["quarantine_enabled"] is True


def test_s407_stop_gate_passes(tmp_path, monkeypatch):
    import runtime_core.api.internet_live_metadata_quarantine_s401_s407 as module

    monkeypatch.setattr(module, "LIVE_METADATA_DIR", tmp_path / "live_metadata")
    payload = build_s407_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S407"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["body_read_blocked"] is True
    assert "report_path" in payload


def test_s401_s407_rollup_ready():
    payload = build_controlled_live_metadata_quarantine_evidence_s401_s407()
    assert payload["stage_version"] == "S407"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
