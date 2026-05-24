from __future__ import annotations

from fastapi.testclient import TestClient


def test_ask_claire_routes_portfolio_question_to_evidence_backed_answer():
    from runtime_core.app import create_app

    client = TestClient(create_app())
    response = client.post(
        "/api/ask-claire",
        json={"query": "Should Claire turn this market trend into a portfolio thesis and weighting?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "answer_ready"
    assert payload["answer_mode"] == "intelligence_routed_evidence_backed"
    assert payload["question_type"]["question_type"] in {"portfolio", "strategic", "investment"}
    assert payload["classification"]["domain"] in {"portfolio", "market"}
    assert payload["evidence_requirement"] == "high"
    assert payload["citation_count"] >= 1
    assert payload["confidence"] > 0
    assert payload["governance"]["answer_is_read_only"] is True
    assert payload["network_request_performed"] is False
    assert payload["body_read_performed"] is False
    assert payload["runtime_truth_mutation"] is False


def test_command_plan_includes_intelligence_answer_contract():
    from runtime_core.dashboard.cockpit_command_plan import build_cockpit_command_plan

    payload = build_cockpit_command_plan(
        "Can Claire assess whether this architecture is buildable?",
    )

    answer = payload["intelligence_answer"]
    assert answer["status"] == "answer_ready"
    assert answer["question_type"]["question_type"] in {"architecture", "engineering"}
    assert answer["domain_route"]["selected_domain_route"] == "engineering"
    assert answer["citation_count"] >= 1
    assert answer["governance"]["live_search_must_use_governed_provider_route"] is True
    assert answer["network_request_performed"] is False
