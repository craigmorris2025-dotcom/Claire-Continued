from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_dashboard_primary_buttons_call_work_producing_endpoints():
    html = Path("frontend/command_center/modern/platform_dashboard.html").read_text(encoding="utf-8")
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")

    assert 'data-action="/runtime/continuous/start"' in html
    assert 'data-action="/evaluate"' in html
    assert "local_source_pack" in js
    assert "Signal -> Trend -> Thesis -> Portfolio" in js
    assert "Breakthrough -> PCO -> PI" not in js
    assert 'data-action="/operator/loop/step"' not in html
    assert 'data-action="/operator/gate/trigger"' not in html


def test_runtime_start_and_evaluate_create_visible_dashboard_state():
    client = TestClient(app)

    cycle = client.post("/runtime/continuous/start", json={"trigger": "test"}).json()
    assert cycle["cycle"]["status"] == "completed_allowlisted_input_cycle"
    assert cycle["cycle"]["candidate_counts"]["discoveries"] >= 0
    assert cycle["cycle"]["candidate_counts"]["breakthroughs"] >= 0
    assert cycle["cycle"]["input_boundary"]["status"] == "enforced"

    run = client.post(
        "/evaluate",
        json={
            "raw_input": "Run the 30-stage Claire lifecycle against the local autonomous invention technology database and return one concrete source-backed candidate.",
            "mode": "deterministic",
            "source_mode": "local_source_pack",
        },
    ).json()
    assert run["status"] == "success"
    assert run["core_lifecycle"]["route"] == "portfolio_creation_optimization"
    assert run["route_selected"] == "portfolio_creation_optimization"
    assert run["core_lifecycle"]["stage_count"] == 30

    state = client.get("/api/dashboard/state").json()
    assert state["metrics"]["discovery_candidates"]["value"] > 0
    assert state["metrics"]["breakthroughs"]["value"] >= 0
    assert state["records"]["discovery"]
    assert state["lifecycle"]["route_selected"] == "portfolio_creation_optimization"
    assert state["system_wiring"]["status"] == "bound"
    assert state["system_wiring"]["selected_route"] == "portfolio_creation_optimization"
    assert state["metrics"]["system_wiring_routes"]["value"] >= 5
    assert state["metrics"]["system_wiring_missing"]["value"] == 0
    route_map = {item["route"]: item for item in state["system_wiring"]["routes"]}
    assert "breakthrough_design" in route_map
    assert "records.design" in route_map["breakthrough_design"]["dashboard_fields"]
    assert "portfolio_creation_optimization" in route_map
    assert not any(
        item.get("name") == "portfolio-first route policy"
        for item in state["platform_completion"].get("gaps", [])
    )


def test_dashboard_frontend_renders_system_wiring_map():
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")

    assert "renderSystemWiring" in js
    assert "renderSystemOwners" in js
    assert "Canonical Runtime Routes to Dashboard Fields" in js
    assert "Project Owners for Runtime Wiring" in js
