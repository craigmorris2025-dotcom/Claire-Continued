from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from claire.app import create_app
from claire.api.industry_standard_endpoint_package import (
    build_industry_standard_endpoint_package,
)


def test_industry_standard_endpoint_package_routes_are_mounted():
    client = TestClient(create_app())

    payload = client.get("/api/system/industry-standard-endpoint-package").json()
    settings = client.get("/api/system/endpoint-standard-settings").json()

    assert payload["schema_version"] == "claire.industry_standard_endpoint_package.v1"
    assert payload["package_name"] == "Endpoint Reconciliation + End-to-End Proof Lock"
    assert settings["package_endpoint"] == "/api/system/industry-standard-endpoint-package"
    assert settings["openapi_endpoint"] == "/openapi.json"
    assert settings["cad_intent_reviewable"] is True
    assert payload["mutation_policy"]["automatic_updates_enabled"] is False


def test_industry_standard_package_maps_required_standards_and_endpoints():
    client = TestClient(create_app())
    payload = client.get("/api/system/industry-standard-endpoint-package").json()

    standards = {item["standard"] for item in payload["standards"]}
    assert {"OpenAPI 3.1", "SLSA", "CycloneDX SBOM", "NIST AI RMF", "ISO/IEC 42001"}.issubset(standards)

    expected = {(item["method"], item["path"]) for item in payload["endpoint_expectations"]}
    assert ("POST", "/api/update-governance/open-web/install/stage") in expected
    assert ("POST", "/api/update-governance/open-web/install/apply") in expected
    assert ("GET", "/design-portal/status") in expected
    assert ("GET", "/design-portal/contract") in expected
    assert ("GET", "/cad/intent") in expected

    checks = {item["path"]: item for item in payload["acceptance_checks"]}
    assert checks["/api/update-governance/open-web/install/stage"]["review_required"] is True
    assert checks["/cad/intent"]["mounted"] is True


def test_standards_control_map_binds_frameworks_to_real_runtime_surfaces():
    client = TestClient(create_app())

    payload = client.get("/api/system/standards-control-map").json()
    package = client.get("/api/system/industry-standard-endpoint-package").json()

    assert payload["schema_version"] == "claire.standards_control_map.v1"
    assert payload["status"] == "ready"
    assert payload["framework_count"] == 8
    assert package["standards_control_map"]["framework_count"] == 8

    frameworks = {item["framework"]: item for item in payload["frameworks"]}
    for framework in [
        "NIST AI RMF",
        "ISO/IEC 42001",
        "OWASP LLM Top 10",
        "NIST CSF 2.0",
        "NIST SSDF",
        "SLSA",
        "CycloneDX",
        "OpenTelemetry",
    ]:
        row = frameworks[framework]
        assert row["mounted"] is True
        assert row["real_route"] is True
        assert row["real_control"] is True
        assert row["real_test"] is True
        assert row["real_governance_gate"] is True
        assert row["real_runtime_behavior"] is True


def test_design_portal_and_cad_contract_endpoints_are_review_only():
    client = TestClient(create_app())

    status = client.get("/design-portal/status").json()
    contract = client.get("/design-portal/contract").json()
    cad = client.get("/cad/intent").json()

    assert status["cad_export_enabled"] is False
    assert contract["cad_export_enabled"] is False
    assert cad["cad_export_enabled"] is False
    assert cad["operator_review_required"] is True
    assert cad["design_contract_endpoint"] == "/design-portal/contract"


def test_industry_standard_package_writes_attached_files(tmp_path: Path):
    payload = build_industry_standard_endpoint_package(project_root=tmp_path)

    package_file = tmp_path / "data" / "endpoint_contracts" / "industry_standard_endpoint_package.json"
    doc_file = tmp_path / "docs" / "engineering" / "industry_standard_endpoint_package.md"

    assert package_file.exists()
    assert doc_file.exists()
    assert payload["settings"]["package_file"] == "data/endpoint_contracts/industry_standard_endpoint_package.json"
    assert "OpenAPI 3.1" in doc_file.read_text(encoding="utf-8")
