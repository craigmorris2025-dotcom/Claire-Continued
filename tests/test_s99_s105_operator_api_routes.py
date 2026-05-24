from __future__ import annotations

import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.governed_s99_s105_routes import include_governed_s99_s105_routes


def build_client() -> TestClient:
    app = FastAPI()
    include_governed_s99_s105_routes(app)
    return TestClient(app)


def test_s99_read_contract_endpoints_are_exposed():
    client = build_client()
    panel = client.get("/api/governed/operator/proof-panel")
    queue = client.get("/api/governed/operator/review-queue")
    assert panel.status_code == 200
    assert queue.status_code == 200
    assert panel.json()["endpoint_contract_version"] == "S99"
    assert queue.json()["read_only"] is True


def test_s100_review_action_endpoint_exports_approved_item():
    client = build_client()
    demo = client.post("/api/governed/operator/route-demo", json={"route": "portfolio", "approve": False})
    assert demo.status_code == 200
    review_item_id = demo.json()["demo"]["review_item"]["review_item_id"]

    action = client.post(
        "/api/governed/operator/review-action",
        json={
            "review_item_id": review_item_id,
            "action": "approve",
            "operator": "pytest",
            "note": "S100 approval endpoint proof",
        },
    )
    assert action.status_code == 200
    payload = action.json()
    assert payload["endpoint_contract_version"] == "S100"
    assert payload["decision"]["decision"] == "approved"
    assert payload["export"]["status"] == "exported"
    assert payload["locks"]["runtime_truth_write_blocked"] is True


def test_s101_route_demo_endpoint_supports_routes():
    client = build_client()
    for route in ("portfolio", "breakthrough", "design"):
        response = client.post("/api/governed/operator/route-demo", json={"route": route, "approve": False})
        assert response.status_code == 200
        payload = response.json()
        assert payload["endpoint_contract_version"] == "S101"
        assert payload["selected_route"] == route
        assert payload["demo"]["status"] == "review_required"


def test_s102_export_manifest_endpoint_is_read_only():
    client = build_client()
    client.get("/api/governed/operator/api-demo-proof")
    response = client.get("/api/governed/operator/export-manifest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["endpoint_contract_version"] == "S102"
    assert payload["read_only"] is True
    assert payload["locks"]["runtime_truth_mutation_blocked"] is True


def test_s103_fetch_map_and_cockpit_card_endpoints():
    client = build_client()
    fetch_map = client.get("/api/governed/operator/fetch-map")
    card = client.get("/api/governed/operator/cockpit-card")
    assert fetch_map.status_code == 200
    assert card.status_code == 200
    assert fetch_map.json()["endpoint_contract_version"] == "S103"
    assert "/api/governed/operator/cockpit-card" in fetch_map.json()["cockpit_fetch_map"].values()
    assert card.json()["endpoint_contract_version"] == "S103"
    assert card.json()["presentation_only"] is True


def test_s104_swagger_visibility_proof_and_openapi_contains_routes():
    client = build_client()
    proof = client.get("/api/governed/operator/swagger-proof")
    openapi = client.get("/openapi.json")
    assert proof.status_code == 200
    assert proof.json()["endpoint_contract_version"] == "S104"
    paths = openapi.json()["paths"]
    assert "/api/governed/operator/proof-panel" in paths
    assert "/api/governed/operator/review-action" in paths
    assert "/api/governed/operator/route-demo" in paths
    assert "/api/governed/operator/api-demo-proof" in paths


def test_s105_end_to_end_operator_api_demo_proof():
    client = build_client()
    proof = client.get("/api/governed/operator/api-demo-proof")
    assert proof.status_code == 200
    payload = proof.json()
    assert payload["endpoint_contract_version"] == "S105"
    assert payload["status"] == "ready"
    assert payload["selected_demo"]["demo"]["export"]["status"] == "exported"
    assert payload["locks"]["autonomous_execution_blocked"] is True


def test_route_module_imports_cleanly():
    module = importlib.import_module("runtime_core.api.governed_s99_s105_routes")
    assert hasattr(module, "router")
    assert hasattr(module, "include_governed_s99_s105_routes")
