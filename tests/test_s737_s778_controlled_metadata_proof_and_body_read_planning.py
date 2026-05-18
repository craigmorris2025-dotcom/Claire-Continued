from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def _client() -> TestClient:
    app_module = importlib.import_module("claire.app")
    return TestClient(app_module.create_app())


def test_s737_s743_evidence_basket_promotion_preview_is_non_mutating():
    module = importlib.import_module("claire.governance.governed_evidence_basket_promotion_preview")
    payload = module.build_promotion_preview()
    assert payload["stage_range"] == "S737-S743"
    assert payload["terminal_state"] == "evidence_basket_promotion_preview_ready"
    assert payload["summary"]["runtime_truth_mutations"] == 0
    assert payload["summary"]["body_reads"] == 0
    assert payload["promotion_preview"]["would_promote_to_runtime_truth"] is False
    assert payload["blocked_capabilities"]["runtime_mutation_enabled"] is False
    assert payload["blocked_capabilities"]["body_read_allowed"] is False


def test_s744_s750_controlled_metadata_search_stop_gate_is_proof_only():
    module = importlib.import_module("claire.governance.governed_metadata_search_stop_gate")
    payload = module.build_metadata_search_proof()
    assert payload["stage_range"] == "S744-S750"
    assert payload["terminal_state"] == "controlled_metadata_search_proof_ready"
    assert payload["summary"]["provider_calls"] == 0
    assert payload["summary"]["network_requests"] == 0
    assert payload["summary"]["body_reads"] == 0
    assert payload["stop_gate"]["passed"] is True
    assert payload["stop_gate"]["blocked_next_phase"] == "uncontrolled_open_web_or_body_reads"


def test_s751_s764_body_read_safety_plan_keeps_body_reads_blocked():
    module = importlib.import_module("claire.governance.governed_body_read_safety_plan")
    payload = module.build_body_read_safety_plan()
    assert payload["stage_range"] == "S751-S764"
    assert payload["terminal_state"] == "body_read_planning_ready_body_reads_blocked"
    assert payload["summary"]["body_read_allowed_total"] == 0
    assert payload["summary"]["body_read_performed_total"] == 0
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert all(candidate["body_read_allowed"] is False for candidate in payload["candidates"])
    assert all(candidate["body_read_performed"] is False for candidate in payload["candidates"])


def test_s765_s778_body_read_request_packet_and_preflight_are_non_executable():
    module = importlib.import_module("claire.governance.governed_body_read_preflight")
    packet = module.build_body_read_request_packet()
    assert packet["stage_range"] == "S765-S771"
    assert packet["terminal_state"] == "manual_body_read_request_packet_ready_body_reads_blocked"
    assert packet["summary"]["body_read_allowed"] is False
    assert packet["execution_enabled"] is False
    payload = module.build_body_read_preflight_payload()
    assert payload["stage_range"] == "S737-S778"
    assert payload["terminal_state"] == "metadata_proof_complete_body_read_planning_ready"
    assert payload["summary"]["executable_actions"] == 0
    assert payload["summary"]["body_reads"] == 0
    assert payload["stop_gate"]["gate_id"] == "S778_BODY_READ_PREFLIGHT_STOP_GATE"
    assert payload["stop_gate"]["blocked_next_phase"] == "body_read_execution_or_crawling"


def test_s737_s778_routes_return_cockpit_payload_cards_and_actions():
    client = _client()
    payload_response = client.get("/api/cockpit/web-search/payload")
    assert payload_response.status_code == 200
    payload = payload_response.json()
    assert payload["stage_range"] == "S737-S778"
    assert payload["terminal_state"] == "metadata_proof_complete_body_read_planning_ready"
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert payload["summary"]["executable_actions"] == 0
    cards_response = client.get("/api/cockpit/web-search/cards")
    assert cards_response.status_code == 200
    cards = cards_response.json()
    assert len(cards) >= 4
    actions_response = client.get("/api/cockpit/web-search/actions")
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert actions
    assert all(action["execution_enabled"] is False for action in actions)


def test_s737_s778_post_body_read_risk_classifier_accepts_candidates_without_reading():
    client = _client()
    response = client.post(
        "/api/web/body-read/risk-classifier",
        json={
            "candidates": [
                {
                    "candidate_id": "candidate-official-docs",
                    "title": "Official docs candidate",
                    "source_family": "official_docs",
                    "url": "https://docs.example.invalid/page",
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["candidate_total"] == 1
    candidate = payload["candidates"][0]
    assert candidate["body_read_allowed"] is False
    assert candidate["body_read_performed"] is False
    assert candidate["network_request_performed"] is False
    assert candidate["requires_manual_preflight"] is True


def test_s737_s778_router_exposes_expected_paths():
    routes = importlib.import_module("claire.api.governed_web_search_body_read_planning_routes")
    paths = {route.path for route in routes.router.routes}
    expected = {
        "/api/evidence/basket/promotion-preview",
        "/api/search/metadata/controlled-proof/payload",
        "/api/search/metadata/controlled-proof/stop-gate",
        "/api/web/body-read/safety-plan",
        "/api/web/body-read/risk-classifier",
        "/api/web/body-read/request-packet",
        "/api/web/body-read/preflight/payload",
        "/api/cockpit/web-search/payload",
        "/api/cockpit/web-search/stop-gate",
        "/api/internet/controlled-metadata-proof/payload",
    }
    assert expected.issubset(paths)
