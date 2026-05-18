from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def _client() -> TestClient:
    app_module = importlib.import_module("claire.app")
    return TestClient(app_module.create_app())


def test_s779_s792_authorization_model_never_grants_body_read():
    module = importlib.import_module("claire.governance.governed_body_read_authorization")
    payload = module.build_authorization_payload()
    assert payload["stage_range"] == "S779-S792"
    assert payload["terminal_state"] == "body_read_authorization_model_ready_body_reads_blocked"
    assert payload["summary"]["authorizations_granted"] == 0
    assert payload["summary"]["body_reads_allowed"] == 0
    assert payload["summary"]["body_reads_performed"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert all(item["body_read_allowed"] is False for item in payload["requests"])


def test_s793_s806_extraction_contract_blocks_body_required_fields():
    module = importlib.import_module("claire.governance.governed_extraction_scope_contract")
    payload = module.build_extraction_scope_contract()
    assert payload["stage_range"] == "S793-S806"
    assert payload["terminal_state"] == "extraction_scope_contract_ready_body_fields_blocked"
    assert payload["summary"]["body_fields_blocked"] >= 1
    assert payload["summary"]["body_reads_performed"] == 0
    assert payload["contract_rules"]["no_crawling"] is True
    assert payload["contract_rules"]["no_runtime_truth_mutation"] is True


def test_s807_s820_sanitizer_plan_is_not_execution():
    module = importlib.import_module("claire.governance.governed_content_safety_sanitizer")
    payload = module.build_sanitizer_payload("text/html", "official_docs")
    assert payload["stage_range"] == "S807-S820"
    assert payload["terminal_state"] == "content_sanitizer_plan_ready_execution_blocked"
    assert payload["summary"]["sanitizer_rules_executed"] == 0
    assert payload["summary"]["body_reads"] == 0
    assert payload["guards"]["no_script_execution"] is True
    risk = module.classify_content_risk("application/octet-stream", "open_web_unknown")
    assert risk["risk_level"] == "high"
    assert risk["body_read_allowed"] is False
    assert risk["network_request_performed"] is False


def test_s821_s834_manual_gate_payload_stops_before_execution():
    module = importlib.import_module("claire.governance.governed_manual_body_read_gate")
    payload = module.build_manual_body_read_gate_payload()
    assert payload["stage_range"] == "S779-S834"
    assert payload["terminal_state"] == "manual_body_read_gate_ready_execution_blocked"
    assert payload["summary"]["executable_actions"] == 0
    assert payload["summary"]["body_reads_allowed"] == 0
    assert payload["summary"]["body_reads_performed"] == 0
    assert payload["summary"]["network_requests"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert payload["stop_gate"]["gate_id"] == "S834_MANUAL_BODY_READ_GATE_STOP"
    assert payload["stop_gate"]["ready_for_next_phase"] is True


def test_s779_s834_routes_return_payload_cards_actions_and_status():
    client = _client()
    payload_response = client.get("/api/cockpit/body-read-gate/payload")
    assert payload_response.status_code == 200
    payload = payload_response.json()
    assert payload["stage_range"] == "S779-S834"
    assert payload["summary"]["executable_actions"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False

    cards_response = client.get("/api/cockpit/body-read-gate/cards")
    assert cards_response.status_code == 200
    cards = cards_response.json()
    assert len(cards) >= 6
    assert all(card["execution_enabled"] is False for card in cards)

    actions_response = client.get("/api/cockpit/body-read-gate/actions")
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert len(actions) >= 3
    assert all(action["execution_enabled"] is False for action in actions)

    status_response = client.get("/api/cockpit/body-read-gate/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "ready"


def test_s779_s834_posted_authorization_and_sanitizer_stay_blocked():
    client = _client()
    auth_response = client.post(
        "/api/web/body-read/authorization/payload",
        json={
            "requests": [
                {
                    "request_id": "test-denied-001",
                    "title": "Unknown web page",
                    "source_family": "open_web_unknown",
                    "trust_tier": "tier_4_unknown",
                }
            ]
        },
    )
    assert auth_response.status_code == 200
    request = auth_response.json()["requests"][0]
    assert request["risk_level"] == "high"
    assert request["body_read_allowed"] is False
    assert request["network_request_performed"] is False

    risk_response = client.post(
        "/api/web/body-read/sanitizer/classify",
        json={"content_type": "application/octet-stream", "source_family": "open_web_unknown"},
    )
    assert risk_response.status_code == 200
    risk = risk_response.json()
    assert risk["risk_level"] == "high"
    assert risk["body_read_performed"] is False


def test_s779_s834_router_exposes_expected_paths():
    routes = importlib.import_module("claire.api.governed_body_read_gate_routes")
    paths = {route.path for route in routes.router.routes}
    expected = {
        "/api/web/body-read/authorization/payload",
        "/api/web/body-read/authorization/cards",
        "/api/web/body-read/extraction-scope/contract",
        "/api/web/body-read/sanitizer/payload",
        "/api/web/body-read/manual-gate/preflight",
        "/api/web/body-read/manual-gate/stop-gate",
        "/api/cockpit/body-read-gate/payload",
        "/api/cockpit/body-read-gate/cards",
        "/api/cockpit/body-read-gate/actions",
        "/api/cockpit/body-read-gate/stop-gate",
        "/api/internet/body-read-gate/payload",
    }
    assert expected.issubset(paths)
