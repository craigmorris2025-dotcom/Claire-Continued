from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from runtime_core.app import create_app


ROOT = Path(__file__).resolve().parents[1]
MODERN = ROOT / "frontend" / "command_center" / "modern"


def test_local_dashboard_is_platform_primary_and_local_alias_exists():
    index = (MODERN / "index.html").read_text(encoding="utf-8")
    html = (MODERN / "platform_dashboard.html").read_text(encoding="utf-8")
    js = (MODERN / "platform_dashboard.js").read_text(encoding="utf-8")
    css = (MODERN / "platform_dashboard.css").read_text(encoding="utf-8")

    assert "/dashboard" in index
    assert 'data-platform-dashboard="canonical-cockpit"' in html
    assert 'href="/dashboard/assets/platform_dashboard.css"' in html
    assert 'src="/dashboard/assets/platform_dashboard.js"' in html
    assert "/operator/status" in js
    assert "/api/system/route-integrity" in js
    assert ".metric-grid" in css


def test_dashboard_route_serves_local_primary_and_local_alias_matches():
    client = TestClient(create_app())

    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 200
    assert 'data-platform-dashboard="canonical-cockpit"' in response.text

    local = client.get("/dashboard/local")
    assert local.status_code == 200
    assert 'data-platform-dashboard="canonical-cockpit"' in local.text

    for path, needle in [
        ("/dashboard/assets/platform_dashboard.css", ".metric-grid"),
        ("/dashboard/assets/platform_dashboard.js", "/operator/status"),
        ("/platform_dashboard.css", ".metric-grid"),
        ("/platform_dashboard.js", "/operator/status"),
    ]:
        asset = client.get(path)
        assert asset.status_code == 200
        assert needle in asset.text

    for path in ["/dashboard/assets/claire_dashboard.css", "/dashboard/assets/claire_dashboard.js", "/claire_dashboard.css", "/claire_dashboard.js"]:
        assert client.get(path).status_code == 404


def test_platform_dashboard_config_exposes_local_primary_backend_contract():
    client = TestClient(create_app())
    response = client.get("/api/platform/dashboard-config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["dashboard_mode"] == "local_canonical_primary"
    assert payload["uploaded_dashboard_url"] is None
    assert payload["primary_dashboard_url"] == "/dashboard"
    assert payload["local_dashboard_url"] == "/dashboard/local"
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["launcher_opens_uploaded_dashboard"] is False
    assert payload["launcher_opens_canonical_dashboard"] is True


def test_old_dashboard_aliases_are_not_active_dashboard_routes():
    client = TestClient(create_app())

    for path in ["/dashboard/v3", "/dashboard/final", "/operator-dashboard", "/operator-cockpit", "/command-center"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 404, path
