from __future__ import annotations

import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_s44r5_dashboard_consumption_manifest_is_read_only():
    module = importlib.import_module("claire.api.s44_dashboard_consumption_manifest")
    manifest = module.build_dashboard_consumption_manifest()

    assert manifest["status"] == "dashboard_consumption_manifest_ready"
    assert manifest["backend_owns_truth"] is True
    assert manifest["cockpit_presentation_only"] is True
    assert manifest["runtime_truth_mutation_allowed"] is False
    assert manifest["surface_count"] == 7

    for surface in manifest["dashboard_surfaces"]:
        assert surface["method"] == "GET"
        assert surface["presentation_only"] is True
        assert surface["backend_owns_truth"] is True
        assert surface["response_mode"] == "read_only_artifact"


def test_s44r6_manifest_verifies_cleanly():
    module = importlib.import_module("claire.api.s44_dashboard_consumption_manifest")
    verification = module.verify_dashboard_consumption_manifest()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["surface_count"] == 7


def test_s44r7_fetch_contract_paths_are_available_on_isolated_app():
    contracts_module = importlib.import_module("claire.api.s44_cockpit_fetch_contracts")
    include_module = importlib.import_module("claire.api.operator_router_include_adapter")

    app = FastAPI()
    include_module.include_operator_router_non_invasive(app)
    client = TestClient(app)

    for path in contracts_module.list_contract_paths():
        response = client.get(path)
        assert response.status_code == 200


def test_s44r8_plateau_report_points_to_next_verification_phase():
    module = importlib.import_module("claire.api.s44_dashboard_consumption_manifest")
    report = module.build_s44_plateau_report()

    assert report["status"] == "s44r1_r8_ready"
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S44R9-R16 cockpit fetch verification and status aggregation"
