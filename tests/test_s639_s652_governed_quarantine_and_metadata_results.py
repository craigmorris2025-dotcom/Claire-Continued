from __future__ import annotations

import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_s639_quarantine_store_payload_preserves_blocks():
    module = importlib.import_module("runtime_core.governance.governed_quarantine_evidence_store")
    payload = module.build_quarantine_payload()
    assert payload["status"]["quarantine_store_ready"] is True
    assert payload["status"]["review_queue_ready"] is True
    assert payload["review_queue"]["item_count"] >= 3
    blocked = payload["status"]["blocked_capabilities"]
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["network_request_performed"] is False


def test_s646_metadata_contract_disallows_body_and_runtime_mutation():
    module = importlib.import_module("runtime_core.governance.governed_metadata_result_contract")
    contract = module.get_metadata_result_contract()
    assert contract["status"] == "defined_non_executing"
    assert "body" in contract["disallowed_fields"]
    assert "html" in contract["disallowed_fields"]
    assert contract["blocked_capabilities"]["body_read_allowed"] is False
    assert contract["blocked_capabilities"]["runtime_mutation_enabled"] is False
    assert contract["blocked_capabilities"]["search_provider_execution_enabled"] is False


def test_metadata_result_validator_rejects_body_fields():
    module = importlib.import_module("runtime_core.governance.governed_metadata_result_contract")
    valid = module.validate_metadata_result({"result_id": "r1", "title": "Result", "url": "https://example.invalid", "source_family": "official_docs", "trust_tier": "tier_1_official", "lineage": ["test"]})
    invalid = module.validate_metadata_result({"result_id": "r2", "title": "Result", "url": "https://example.invalid", "source_family": "open_web", "trust_tier": "tier_4_unverified", "lineage": ["test"], "body": "not allowed"})
    assert valid["valid"] is True
    assert invalid["valid"] is False
    assert "body" in invalid["present_disallowed_fields"]


def test_quarantine_and_metadata_routers_serve_payloads():
    q_routes = importlib.import_module("runtime_core.api.governed_quarantine_evidence_routes")
    m_routes = importlib.import_module("runtime_core.api.governed_metadata_result_routes")
    app = FastAPI()
    app.include_router(q_routes.router)
    app.include_router(m_routes.router)
    client = TestClient(app)
    q_resp = client.get("/api/evidence/quarantine/payload")
    m_resp = client.get("/api/search/metadata/payload")
    assert q_resp.status_code == 200
    assert m_resp.status_code == 200
    assert q_resp.json()["status"]["cockpit_cards_ready"] is True
    assert m_resp.json()["status"]["contract_ready"] is True


def test_create_app_registers_s639_s652_routes_when_available():
    app_module = importlib.import_module("runtime_core.app")
    app = app_module.create_app()
    client = TestClient(app)
    q_resp = client.get("/api/evidence/quarantine/status")
    m_resp = client.get("/api/search/metadata/status")
    assert q_resp.status_code == 200
    assert m_resp.status_code == 200
    assert q_resp.json()["quarantine_store_ready"] is True
    assert m_resp.json()["metadata_contract_ready"] is True


def test_s645_and_s652_stop_gates_pass_without_unlocking_web():
    q_module = importlib.import_module("runtime_core.governance.governed_quarantine_evidence_store")
    m_module = importlib.import_module("runtime_core.governance.governed_metadata_result_contract")
    q_gate = q_module.build_quarantine_stop_gate()
    m_gate = m_module.build_metadata_stop_gate()
    assert q_gate["passed"] is True
    assert m_gate["passed"] is True
    assert q_gate["blocked_capabilities"]["network_request_performed"] is False
    assert m_gate["blocked_capabilities"]["body_read_allowed"] is False


def test_frontend_assets_exist_and_reference_new_endpoints():
    js_path = Path("frontend/cockpit/assets/claire_governed_quarantine_and_metadata_results.js")
    css_path = Path("frontend/cockpit/assets/claire_governed_quarantine_and_metadata_results.css")
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    assert "/api/evidence/quarantine/payload" in js
    assert "/api/search/metadata/payload" in js
