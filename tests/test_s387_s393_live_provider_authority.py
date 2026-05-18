from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.internet_live_provider_authority_s387_s393 import (
    build_controlled_live_provider_authority_s387_s393,
    build_s387_live_provider_authority_contract,
    build_s388_live_toggle_reader,
    build_s389_source_allowlist_gate,
    build_s390_rate_limit_timeout_contract,
    build_s391_metadata_only_transport_contract,
    build_s392_route_registration_proof,
    build_s393_stop_gate,
    register_s387_s393_live_provider_authority_routes,
)


def test_s387_live_provider_authority_is_fail_closed():
    payload = build_s387_live_provider_authority_contract()
    authority = payload["live_provider_authority"]
    assert payload["stage_version"] == "S387"
    assert authority["failure_mode"] == "fail_closed"
    assert authority["body_read_default_allowed"] is False
    assert authority["runtime_truth_write_allowed"] is False


def test_s388_toggle_defaults_closed_and_can_enable():
    closed = build_s388_live_toggle_reader(env={})
    enabled = build_s388_live_toggle_reader(env={"CLAIRE_ALLOW_CONTROLLED_LIVE_PROVIDER": "true"})
    assert closed["stage_version"] == "S388"
    assert closed["toggle"]["controlled_live_provider_allowed"] is False
    assert enabled["toggle"]["controlled_live_provider_allowed"] is True


def test_s389_source_allowlist_blocks_localhost():
    allowed = build_s389_source_allowlist_gate("https://example.com")
    blocked = build_s389_source_allowlist_gate("http://localhost")
    assert allowed["source_gate"]["allowed_for_controlled_probe"] is True
    assert blocked["source_gate"]["allowed_for_controlled_probe"] is False


def test_s390_rate_limit_allows_one_request_only():
    payload = build_s390_rate_limit_timeout_contract()
    assert payload["stage_version"] == "S390"
    assert payload["rate_limit"]["max_requests_per_operator_action"] == 1
    assert payload["rate_limit"]["body_read_allowed"] is False


def test_s391_metadata_only_transport_forbids_body_read():
    payload = build_s391_metadata_only_transport_contract()
    assert payload["stage_version"] == "S391"
    assert payload["transport"]["body_read_allowed"] is False
    assert payload["transport"]["quarantine_required_for_results"] is True


def test_s392_route_registration_and_status_endpoint():
    payload = build_s392_route_registration_proof()
    assert payload["stage_version"] == "S392"
    assert payload["authority_route_registered"] is True

    app = FastAPI()
    register_s387_s393_live_provider_authority_routes(app)
    response = TestClient(app).get("/api/internet/live-provider/authority")
    assert response.status_code == 200
    assert response.json()["body_read_allowed"] is False


def test_s393_stop_gate_passes(tmp_path):
    payload = build_s393_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S393"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["toggle_defaults_closed"] is True
    assert "report_path" in payload


def test_s387_s393_rollup_ready():
    payload = build_controlled_live_provider_authority_s387_s393()
    assert payload["stage_version"] == "S393"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
