from __future__ import annotations

from fastapi.testclient import TestClient


def test_dashboard_v5_payload_maps_all_30_stages_and_design_route():
    from claire.dashboard.final_dashboard_payload import build_final_dashboard_payload

    payload = build_final_dashboard_payload()

    assert payload["schema_version"] == "claire_final_dashboard_v5"
    assert payload["completion_percent"] == 100
    assert payload["stage_count"] == 30
    assert [stage["number"] for stage in payload["stages"]] == list(range(1, 31))

    design = payload["design_route"]
    assert design["required"] is True
    assert design["stage_range"] == [16, 22]
    assert design["stage_count"] == 7
    assert [stage["number"] for stage in design["stages"]] == list(range(16, 23))
    assert payload["scores"]["all_30_stages_mapped"] == 100
    assert payload["scores"]["design_route_16_22_mapped"] == 100
    assert payload["dashboard_identity"]["surface"] == "final_operator_web_dashboard"


def test_dashboard_v5_payload_contains_operator_workflows_and_processes():
    from claire.dashboard.final_dashboard_payload import build_final_dashboard_payload

    payload = build_final_dashboard_payload()

    panel_ids = {panel["id"] for panel in payload["operator_panels"]}
    workflow_ids = {workflow["id"] for workflow in payload["operator_workflows"]}
    process_ids = {process["id"] for process in payload["system_processes"]}

    assert {"lifecycle", "evidence", "design_autodesign", "portfolio", "acquisition", "governance", "exports", "diagnostics"} <= panel_ids
    assert {"review_current_stage", "run_design_readiness_review", "prepare_acquisition_package", "export_proof_package"} <= workflow_ids
    assert {"payload_normalization", "lifecycle_registry", "design_route", "governance_locks", "completion_gate"} <= process_ids
    assert payload["command_surface"]["default_mode"] == "operate"
    assert "runtime_mutation" in payload["command_surface"]["blocked_authorities"]
    assert all(workflow["safe_to_preview"] is True for workflow in payload["operator_workflows"])
    assert all(workflow["execution_enabled"] is False for workflow in payload["operator_workflows"])
    assert payload["scores"]["operator_functionality"] == 100
    assert payload["scores"]["system_processes_mapped"] == 100


def test_dashboard_v5_routes_assets_and_html_are_user_facing():
    from claire.app import create_app

    client = TestClient(create_app())

    assert client.get("/api/dashboard/v5/payload").status_code == 200
    html = client.get("/dashboard/v5")
    assert html.status_code == 200
    assert client.get("/dashboard/final-user").status_code == 200
    assert client.get("/dashboard/v5/assets/dashboard_v5.css").status_code == 200
    assert client.get("/dashboard/v5/assets/dashboard_v5.js").status_code == 200
    assert client.get("/favicon.ico").status_code == 200

    text = html.text
    assert "Claire Command Center" in text
    assert "Operator Actions" in text
    assert "Operate Claire" in text
    assert "Platform control surface" in text
    assert "Evidence Review" in text
    assert "Design / AutoDesign" in text
    assert "Acquisition Package" in text
    assert "Export Package" in text
    assert "System Processes" in text
    assert "Stages 1-30" in text
    assert "Stages 16-22" in text
    assert "endpoint-list" not in text
    assert "Endpoint Browser" not in text


def test_complete_system_gate_requires_v5_stage_map_and_design_route():
    from tools.plateau.complete_system_gate import run_gate

    report = run_gate()

    assert report["status"] == "complete"
    assert report["scores"]["all_30_stages_mapped"] == 100
    assert report["scores"]["design_route_16_22_mapped"] == 100
    assert report["scores"]["operator_functionality"] == 100
    assert report["scores"]["system_processes_mapped"] == 100
    assert report["scores"]["favicon_clean"] == 100
    assert report["dashboard_v5_payload"]["stage_count"] == 30
    assert report["dashboard_v5_payload"]["design_route_stage_count"] == 7
    assert report["dashboard_v5_payload"]["operator_workflow_count"] >= 6
