from __future__ import annotations

from fastapi.testclient import TestClient


def _client() -> TestClient:
    from runtime_core.app import create_app
    return TestClient(create_app())


def test_readiness_audit_preserves_execution_blocks():
    from runtime_core.governance.governed_web_readiness_audit import build_readiness_audit
    audit = build_readiness_audit()
    assert audit["audit_id"] == "s681_s687_search_web_readiness_audit"
    assert audit["execution_allowed"] is False
    assert audit["network_request_performed"] is False
    assert audit["blocked_authority"]["live_web_execution_enabled"] is False
    assert audit["blocked_authority"]["body_read_allowed"] is False
    assert len(audit["components"]) >= 6


def test_provider_configuration_inspection_hides_secrets_and_does_not_execute():
    from runtime_core.governance.governed_provider_config_inspector import inspect_provider_configurations
    providers = inspect_provider_configurations()
    assert providers
    assert all(provider["secrets_exposed"] is False for provider in providers)
    assert all(provider["execution_allowed"] is False for provider in providers)
    assert all(provider["network_request_performed"] is False for provider in providers)
    assert {provider["provider_id"] for provider in providers} >= {"google_custom_search_metadata", "official_docs_seed_metadata"}


def test_metadata_adapter_boundary_rejects_body_fields():
    from runtime_core.governance.governed_metadata_adapter_boundary import build_metadata_adapter_boundary, normalize_metadata_preview, validate_metadata_result
    boundary = build_metadata_adapter_boundary()
    assert boundary["status"] == "adapter_boundary_ready_execution_blocked"
    assert boundary["body_read_allowed"] is False
    assert "body" in boundary["denied_fields"]
    preview = normalize_metadata_preview("AI market update")
    assert preview
    assert all("body" not in result for result in preview)
    validation = validate_metadata_result({"title": "x", "url": "https://example.invalid", "provider_id": "p", "query": "q", "rank": 1, "body": "not allowed"})
    assert validation["accepted"] is False
    assert validation["body_read_detected"] is True


def test_manual_metadata_probe_is_preview_only_no_network():
    from runtime_core.governance.governed_manual_metadata_probe_gate import build_manual_metadata_probe_payload, build_s708_stop_gate
    payload = build_manual_metadata_probe_payload("Claire source search")
    assert payload["preflight"]["execution_allowed"] is False
    assert payload["preflight"]["provider_execution_allowed"] is False
    assert payload["preflight"]["network_request_performed"] is False
    assert payload["preview"]["status"] == "local_preview_only_no_network"
    assert payload["preview"]["preview_results"]
    stop_gate = build_s708_stop_gate()
    assert stop_gate["status"] == "complete_execution_still_blocked"
    assert stop_gate["current_state"]["next_phase"] == "S709-S736 result quarantine and cockpit evidence/result visibility"


def test_routes_expose_s681_s708_payloads():
    client = _client()
    readiness = client.get("/api/search/readiness/audit")
    assert readiness.status_code == 200
    assert readiness.json()["execution_allowed"] is False
    providers = client.get("/api/search/providers/configuration/payload")
    assert providers.status_code == 200
    assert providers.json()["status"]["secrets_exposed"] is False
    adapter = client.get("/api/search/metadata/adapter/payload?query=portfolio")
    assert adapter.status_code == 200
    assert adapter.json()["status"]["network_request_performed"] is False
    probe = client.get("/api/search/metadata/probe/manual/payload?query=portfolio")
    assert probe.status_code == 200
    data = probe.json()
    assert data["status"]["real_results_available"] is False
    assert data["status"]["preview_results_available"] is True
    cockpit = client.get("/api/cockpit/metadata-search/payload?query=portfolio")
    assert cockpit.status_code == 200
    assert cockpit.json()["stop_gate"]["stop_gate_id"] == "s708_manual_metadata_probe_gate"


def test_route_registration_exists_in_create_app():
    from runtime_core.app import create_app
    app = create_app()
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/api/cockpit/metadata-search/payload" in paths
    assert "/api/search/metadata/probe/manual/preflight" in paths
