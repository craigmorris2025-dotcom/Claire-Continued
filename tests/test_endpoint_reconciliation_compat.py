from __future__ import annotations

from fastapi.testclient import TestClient

from claire.app import create_app


def test_valuable_stale_frontend_routes_resolve_as_compatibility_aliases():
    client = TestClient(create_app())

    for path in [
        "/system/runtime-state/summary",
        "/system/runtime-execution/summary",
        "/system/runtime-propagation/summary",
        "/api/dashboard/search/provider/status",
        "/api/evidence/governed/status",
        "/api/evidence/governed/cards",
        "/api/evidence/governed/actions",
        "/api/search/readiness/preflight",
        "/api/search/metadata/payload",
        "/api/search/governed/plans",
        "/api/search/governed/actions",
        "/api/cockpit/search-results/payload",
        "/api/sources/gaps/payload",
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        payload = response.json()
        assert payload["status"] == "alias_resolved", path
        assert payload["compatibility_only"] is True
        assert payload["computed_new_truth"] is False


def test_old_internet_workflow_routes_are_operator_gated_aliases():
    client = TestClient(create_app())

    post_paths = [
        "/api/internet/live-toggle/preflight",
        "/api/internet/provider/probe",
        "/api/internet/fetch/controlled",
        "/api/internet/live-metadata/run",
        "/api/internet/proposals/review",
        "/api/internet/proposals/export",
    ]
    for path in post_paths:
        response = client.post(path, json={"operator_confirmed": True, "source_url": "https://example.com"})
        assert response.status_code == 200, path
        payload = response.json()
        assert payload["status"] == "alias_resolved", path
        assert payload["compatibility_only"] is True
        assert payload["computed_new_truth"] is False

    assert client.get("/api/internet/fetch/controlled/status").status_code == 200
    assert client.get("/api/internet/live-metadata/run/status").status_code == 200
    assert client.get("/api/internet/proposals/status").status_code == 200


def test_endpoint_reconciliation_report_is_dashboard_accessible():
    client = TestClient(create_app())

    payload = client.get("/api/system/endpoint-reconciliation").json()

    assert payload["schema_version"] == "claire.endpoint_reconciliation_report.v1"
    assert payload["compatibility_alias_count"] >= 19
    assert payload["mounted_route_count"] > 0
    assert "/system/runtime-state/summary" in payload["aliases"]
    assert payload["next_rule"].startswith("Replace compatibility aliases")

