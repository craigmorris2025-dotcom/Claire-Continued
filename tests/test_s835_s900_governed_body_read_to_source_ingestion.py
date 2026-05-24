from __future__ import annotations

import importlib
from fastapi.testclient import TestClient


def _client() -> TestClient:
    app_module = importlib.import_module("runtime_core.app")
    return TestClient(app_module.create_app())


def test_s835_s848_execution_envelope_models_but_blocks_body_reads():
    module = importlib.import_module("runtime_core.governance.governed_manual_body_read_execution_envelope")
    payload = module.build_execution_envelope_payload()
    assert payload["stage_range"] == "S835-S848"
    assert payload["terminal_state"] == "manual_body_read_execution_envelope_ready_execution_blocked"
    assert payload["summary"]["body_reads_allowed"] == 0
    assert payload["summary"]["network_requests"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert all(item["body_read_allowed"] is False for item in payload["envelopes"])


def test_s849_s855_sanitized_extraction_preview_blocks_body_fields():
    module = importlib.import_module("runtime_core.governance.governed_sanitized_extraction_preview")
    payload = module.build_sanitized_extraction_preview_payload()
    assert payload["stage_range"] == "S849-S855"
    assert payload["terminal_state"] == "sanitized_extraction_preview_ready_body_read_blocked"
    assert payload["summary"]["body_reads_performed"] == 0
    assert payload["summary"]["network_requests"] == 0
    assert payload["policy"]["scripts_never_execute"] is True


def test_s856_s883_source_update_ingestion_drafts_do_not_execute():
    module = importlib.import_module("runtime_core.governance.governed_source_update_ingestion")
    payload = module.build_source_ingestion_payload()
    assert payload["stage_range"] == "S856-S883"
    assert payload["terminal_state"] == "source_update_ingestion_drafts_ready_execution_blocked"
    assert payload["summary"]["ingestions_allowed"] == 0
    assert payload["summary"]["automatic_updates_allowed"] == 0
    assert payload["summary"]["runtime_truth_mutations"] == 0
    assert payload["validation_rules"]["no_runtime_mutation"] is True


def test_s884_s900_promotion_preview_and_stop_gate_preserve_blocks():
    module = importlib.import_module("runtime_core.governance.governed_runtime_truth_promotion_preview")
    promotion = module.build_runtime_truth_promotion_preview()
    assert promotion["stage_range"] == "S884-S890"
    assert promotion["summary"]["promotions_allowed"] == 0
    assert promotion["summary"]["runtime_truth_mutations"] == 0
    gate = module.build_s900_stop_gate()
    assert gate["gate_id"] == "S900_BODY_READ_TO_SOURCE_UPDATE_INGESTION_STOP"
    assert gate["ready_for_next_phase"] is True
    assert gate["proof"]["network_request_performed"] is False
    assert gate["proof"]["body_read_performed"] is False
    assert gate["proof"]["runtime_truth_mutation_allowed"] is False


def test_s835_s900_cockpit_payload_is_visible_but_non_executable():
    module = importlib.import_module("runtime_core.governance.governed_runtime_truth_promotion_preview")
    payload = module.build_cockpit_source_ingestion_payload()
    assert payload["stage_range"] == "S835-S900"
    assert payload["terminal_state"] == "s900_source_update_ingestion_ready_execution_blocked"
    assert payload["summary"]["cards"] >= 6
    assert payload["summary"]["executable_actions"] == 0
    assert payload["command_bar_search_state"]["can_search_open_web"] is False
    assert payload["command_bar_search_state"]["can_display_review_cards"] is True


def test_s835_s900_routes_return_payload_cards_actions_and_status():
    client = _client()
    payload_response = client.get("/api/cockpit/source-ingestion/payload")
    assert payload_response.status_code == 200
    payload = payload_response.json()
    assert payload["stage_range"] == "S835-S900"
    assert payload["summary"]["executable_actions"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    cards_response = client.get("/api/cockpit/source-ingestion/cards")
    assert cards_response.status_code == 200
    assert all(card["execution_enabled"] is False for card in cards_response.json())
    actions_response = client.get("/api/cockpit/source-ingestion/actions")
    assert actions_response.status_code == 200
    assert all(action["execution_enabled"] is False for action in actions_response.json())
    status_response = client.get("/api/cockpit/source-ingestion/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "ready"
    stop_response = client.get("/api/cockpit/source-ingestion/stop-gate")
    assert stop_response.status_code == 200
    assert stop_response.json()["gate_id"] == "S900_BODY_READ_TO_SOURCE_UPDATE_INGESTION_STOP"


def test_s835_s900_posted_unknown_envelope_stays_blocked_high_risk():
    client = _client()
    response = client.post("/api/web/body-read/execution-envelope/payload", json={"envelopes": [{"envelope_id": "unknown-open-web-001", "source_family": "open_web_unknown", "trust_tier": "tier_4_unknown", "target_kind": "single_url"}]})
    assert response.status_code == 200
    envelope = response.json()["envelopes"][0]
    assert envelope["risk_level"] == "high"
    assert envelope["body_read_allowed"] is False
    assert envelope["network_request_performed"] is False


def test_s835_s900_router_exposes_expected_paths():
    routes = importlib.import_module("runtime_core.api.governed_body_read_source_ingestion_routes")
    paths = {route.path for route in routes.router.routes}
    expected = {"/api/web/body-read/execution-envelope/payload", "/api/web/body-read/extraction-preview/payload", "/api/web/source-ingestion/draft", "/api/web/source-ingestion/lineage", "/api/web/update-proposal/payload", "/api/web/runtime-truth/promotion-preview", "/api/cockpit/source-ingestion/payload", "/api/cockpit/source-ingestion/cards", "/api/cockpit/source-ingestion/actions", "/api/cockpit/source-ingestion/status", "/api/cockpit/source-ingestion/stop-gate", "/api/internet/source-ingestion/payload"}
    assert expected.issubset(paths)
