from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.governed_controlled_metadata_search_routes import router
from runtime_core.governance.governed_cockpit_search_consolidation import build_cockpit_source_search_consolidation
from runtime_core.governance.governed_manual_provider_probe import build_manual_probe_preflight
from runtime_core.governance.governed_search_evidence_bridge import build_search_to_evidence_bridge
from runtime_core.governance.governed_evidence_lifecycle_preview import build_evidence_lifecycle_routing_preview


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_s653_manual_probe_preflight_is_metadata_only_and_blocked():
    payload = build_manual_probe_preflight("latest AI chip official docs")
    assert payload["status"] == "manual_metadata_probe_preflight_ready_but_execution_blocked"
    assert payload["execution_allowed"] is False
    assert payload["provider_execution_allowed"] is False
    assert payload["network_request_performed"] is False
    assert payload["blocked_authority"]["body_read_allowed"] is False
    assert payload["blocked_authority"]["runtime_mutation_enabled"] is False
    assert payload["providers"]


def test_s660_search_to_evidence_bridge_preserves_quarantine_first_contract():
    payload = build_search_to_evidence_bridge()
    assert payload["status"] == "bridge_ready_with_sample_metadata_only_inputs"
    assert payload["metadata_result_count"] >= 1
    assert payload["evidence_item_count"] == payload["metadata_result_count"]
    assert payload["runtime_truth_mutated"] is False
    assert payload["network_request_performed"] is False
    assert all(item["review_state"] == "quarantined_pending_operator_review" for item in payload["evidence_items"])
    assert all(item["body_read"] is False for item in payload["evidence_items"])


def test_s667_evidence_lifecycle_preview_has_routes_without_mutation():
    payload = build_evidence_lifecycle_routing_preview()
    route_ids = {item["route_id"] for item in payload["route_previews"]}
    assert "trend_discovery_preview" in route_ids
    assert "portfolio_preview" in route_ids
    assert "breakthrough_preview" in route_ids
    assert "design_preview" in route_ids
    assert "update_readiness_preview" in route_ids
    assert payload["selected_route"] is None
    assert payload["lifecycle_mutated"] is False
    assert payload["runtime_truth_mutated"] is False


def test_s680_consolidated_cockpit_payload_contains_panels_cards_actions_and_blocks():
    payload = build_cockpit_source_search_consolidation("search command bar test")
    panel_ids = {panel["panel_id"] for panel in payload["panels"]}
    assert "manual_provider_probe" in panel_ids
    assert "search_to_evidence_bridge" in panel_ids
    assert "evidence_lifecycle_preview" in panel_ids
    assert "source_search_stop_gate" in panel_ids
    assert payload["cards"]
    assert payload["actions"]
    assert payload["proof"]["manual_probe_gate_present"] is True
    assert payload["proof"]["search_to_evidence_bridge_present"] is True
    assert payload["proof"]["evidence_to_lifecycle_preview_present"] is True
    assert payload["blocked_authority"]["live_web_execution_enabled"] is False
    assert payload["blocked_authority"]["network_request_performed"] is False


def test_routes_return_expected_manual_probe_and_consolidated_payloads():
    client = _client()
    preflight = client.get("/api/search/provider/manual-probe/preflight", params={"query": "AI official docs"})
    assert preflight.status_code == 200
    assert preflight.json()["network_request_performed"] is False

    bridge = client.get("/api/search/evidence/bridge/preview")
    assert bridge.status_code == 200
    assert bridge.json()["runtime_truth_mutated"] is False

    lifecycle = client.get("/api/evidence/lifecycle/routing-preview")
    assert lifecycle.status_code == 200
    assert lifecycle.json()["route_preview_count"] >= 5

    consolidated = client.get("/api/cockpit/search/consolidated-payload", params={"query": "command bar query"})
    assert consolidated.status_code == 200
    data = consolidated.json()
    assert data["stage_range"] == "S653-S680"
    assert data["proof"]["body_read_allowed"] is False


def test_s680_stop_gate_route_reports_next_phase_without_unlocking_web():
    client = _client()
    response = client.get("/api/cockpit/search/stop-gate")
    assert response.status_code == 200
    data = response.json()
    assert data["stop_gate_id"] == "s680_cockpit_source_search_consolidation"
    assert data["current_state"]["next_phase"] == "S681-S694 search/web readiness audit and provider configuration inspector"
    assert data["current_state"]["live_web_execution_enabled"] is False
    assert data["current_state"]["search_provider_execution_enabled"] is False
    assert data["current_state"]["network_request_performed"] is False


def test_create_app_registers_s653_s680_router_when_app_module_exists():
    from runtime_core.app import create_app

    app = create_app()
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/api/cockpit/search/consolidated-payload" in paths
    assert "/api/search/provider/manual-probe/preflight" in paths
