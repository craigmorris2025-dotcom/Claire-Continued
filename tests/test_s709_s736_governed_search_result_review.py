from __future__ import annotations

import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _client() -> TestClient:
    routes = importlib.import_module("runtime_core.api.governed_search_result_review_routes")
    app = FastAPI()
    app.include_router(routes.router)
    return TestClient(app)


def test_s709_quarantine_store_blocks_live_authority():
    module = importlib.import_module("runtime_core.governance.governed_search_result_quarantine")
    store = module.build_quarantine_store()
    assert store["stage_range"] == "S709-S715"
    assert store["summary"]["result_total"] >= 3
    assert store["summary"]["body_reads"] == 0
    assert store["summary"]["network_requests"] == 0
    assert store["summary"]["runtime_truth_mutations"] == 0
    blocked = store["blocked_capabilities"]
    assert blocked["live_web_execution_enabled"] is False
    assert blocked["search_provider_execution_enabled"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["autonomous_crawling_enabled"] is False
    assert blocked["automatic_updates_enabled"] is False
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["package_install_performed"] is False
    assert blocked["command_execution_enabled"] is False


def test_s716_result_evidence_normalizer_creates_review_cards():
    module = importlib.import_module("runtime_core.governance.governed_result_evidence_normalizer")
    payload = module.build_result_evidence_payload()
    assert payload["stage_range"] == "S716-S722"
    assert payload["summary"]["evidence_card_total"] == payload["summary"]["metadata_result_total"]
    assert payload["summary"]["runtime_truth_mutations"] == 0
    assert payload["cards"]
    assert all(card["claim_preview"]["claim_status"] == "candidate_only_not_runtime_truth" for card in payload["cards"])


def test_s723_source_confidence_builds_citation_candidates_without_promoting_truth():
    module = importlib.import_module("runtime_core.governance.governed_source_confidence_builder")
    payload = module.build_source_confidence_payload()
    assert payload["stage_range"] == "S723-S729"
    assert payload["summary"]["confidence_card_total"] >= 3
    assert payload["summary"]["runtime_truth_mutations"] == 0
    assert any(card["citation_candidate"] for card in payload["cards"])
    assert all(card["runtime_truth_state"] == "not_promoted" for card in payload["cards"])


def test_s730_operator_review_actions_are_visible_but_non_executable():
    module = importlib.import_module("runtime_core.governance.governed_operator_review_actions")
    payload = module.build_operator_review_payload()
    assert payload["stage_range"] == "S730-S736"
    assert payload["summary"]["operator_action_total"] >= 3
    assert payload["summary"]["executable_actions"] == 0
    assert payload["policy"]["actions_are_descriptors_only"] is True
    assert all(action["operator_visible"] is True for action in payload["actions"])
    assert all(action["execution_enabled"] is False for action in payload["actions"])
    assert all(action["runtime_truth_mutation_enabled"] is False for action in payload["actions"])


def test_s709_s736_routes_return_cockpit_payload_and_actions():
    client = _client()
    payload_response = client.get("/api/cockpit/search-results/payload")
    assert payload_response.status_code == 200
    payload = payload_response.json()
    assert payload["stage_range"] == "S709-S736"
    assert payload["terminal_state"] == "search_result_review_ready"
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    actions_response = client.get("/api/cockpit/search-results/actions")
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert actions
    assert all(action["execution_enabled"] is False for action in actions)


def test_s709_s736_posted_metadata_is_normalized_without_network_or_body_reads():
    client = _client()
    response = client.post(
        "/api/search/results/quarantine/store",
        json={
            "results": [
                {
                    "title": "Official docs candidate",
                    "url": "https://docs.example.invalid/new-release",
                    "provider": "manual_probe_preview",
                    "snippet": "Metadata only",
                    "rank": 1,
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["result_total"] == 1
    result = payload["results"][0]
    assert result["source_family"] == "official_docs"
    assert result["metadata_only"] is True
    assert result["body_read"] is False
    assert result["network_request_performed"] is False
    assert result["runtime_truth_mutated"] is False


def test_s709_s736_router_exposes_expected_paths():
    routes = importlib.import_module("runtime_core.api.governed_search_result_review_routes")
    paths = {route.path for route in routes.router.routes}
    expected = {
        "/api/search/results/quarantine/store",
        "/api/search/results/normalize/payload",
        "/api/search/source-confidence/payload",
        "/api/search/operator-review/actions",
        "/api/cockpit/search-results/payload",
        "/api/cockpit/search-results/stop-gate",
    }
    assert expected.issubset(paths)
