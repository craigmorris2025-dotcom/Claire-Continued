from __future__ import annotations


def test_strategic_world_layer_is_recommendation_only():
    from runtime_core.strategic_world import build_strategic_world_layer

    payload = build_strategic_world_layer(
        {
            "run_id": "cycle-test",
            "route_selected": "existing_system_replacement",
            "signals": [{"title": "AI platform governance market signal", "summary": "buyer pressure"}],
            "trend": {"title": "Platform governance trend", "confidence": 0.8},
            "thesis": {"statement": "Governed platform replacement is review-ready."},
            "portfolio_candidate": {"title": "Governed platform replacement"},
            "emergence_engine": {
                "detected_patterns": [
                    {"pattern_id": "platformization", "name": "Platformization", "score": 0.9}
                ],
            },
            "quality_gate": {"design_proof_complete": True},
        },
        memory_records=[],
    )

    assert payload["status"] == "strategic_world_ready"
    assert payload["ranked_recommendations"]
    assert payload["governance"]["proposal_allowed"] is True
    assert payload["governance"]["external_execution_allowed"] is False
    assert payload["authority"]["external_action_performed"] is False
    assert payload["authority"]["runtime_truth_mutated"] is False
    assert "technology" in payload["domains"]


def test_continuous_runtime_attaches_strategic_world_to_first_run(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    import runtime_core.api.routes_continuous_runtime as runtime_routes
    from runtime_core.app import create_app

    monkeypatch.setattr(runtime_routes, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runtime_routes, "CONTINUOUS_DIR", tmp_path / "data" / "continuous_runtime")

    client = TestClient(create_app())
    result = client.post("/runtime/continuous/start", json={"trigger": "strategic_world_test"})

    assert result.status_code == 200
    payload = result.json()
    run = payload["cycle"]
    assert run["strategic_world"]["status"] == "strategic_world_ready"
    assert run["quality_gate"]["strategic_world_complete"] is True
    assert run["strategic_world"]["governance"]["external_execution_allowed"] is False


def test_strategic_world_route_and_dashboard_state_surface():
    from fastapi.testclient import TestClient

    from runtime_core.app import create_app

    client = TestClient(create_app())

    route_payload = client.get("/api/strategic-world/status")
    dashboard = client.get("/api/dashboard/state")

    assert route_payload.status_code == 200
    assert route_payload.json()["schema_version"] == "claire.strategic_world.layer.v1"
    assert dashboard.status_code == 200
    assert "strategic_world" in dashboard.json()
