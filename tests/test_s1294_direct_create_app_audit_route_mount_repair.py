from __future__ import annotations

from fastapi.testclient import TestClient


def test_s1294_exact_failing_audit_routes_return_200_from_create_app():
    from claire.app import create_app

    client = TestClient(create_app())

    endpoints = [
        "/api/audit/risk-pattern-review",
        "/dashboard/audit/risk-pattern-review",
        "/api/audit/plateau-lock",
        "/dashboard/audit/plateau-lock",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint

    risk = client.get("/api/audit/risk-pattern-review").json()
    plateau = client.get("/api/audit/plateau-lock").json()

    assert risk["status"] == "reviewed"
    assert risk["blocked_authority"]["command_execution"] == "blocked"
    assert risk["blocked_authority"]["body_reads"] == "blocked"

    assert plateau["status"] == "locked"
    assert plateau["forward_motion_allowed"] is True
    assert plateau["blocker_count"] == 0
    assert plateau["warning_count"] == 0
    assert plateau["blocked_authority"]["runtime_mutation"] == "blocked"
    assert plateau["blocked_authority"]["body_reads"] == "blocked"


def test_s1294_routes_are_in_route_table_not_only_module_functions():
    from claire.app import create_app

    app = create_app()
    paths = {getattr(route, "path", "") for route in app.routes}

    assert "/api/audit/risk-pattern-review" in paths
    assert "/dashboard/audit/risk-pattern-review" in paths
    assert "/api/audit/plateau-lock" in paths
    assert "/dashboard/audit/plateau-lock" in paths
