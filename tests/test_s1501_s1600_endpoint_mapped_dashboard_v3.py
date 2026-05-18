from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from claire.app import create_app


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_MARKER = 'data-dashboard-v3="endpoint-mapped-final-operator-dashboard"'
MAP = ROOT / "output" / "dashboard_endpoint_map" / "dashboard_endpoint_map_latest.json"
HTML = ROOT / "frontend" / "command_center" / "modern" / "dashboard_endpoint_mapped_v3.html"
INDEX = ROOT / "frontend" / "command_center" / "modern" / "index.html"
JS = ROOT / "frontend" / "command_center" / "modern" / "dashboard_endpoint_mapped_v3.js"
CSS = ROOT / "frontend" / "command_center" / "modern" / "dashboard_endpoint_mapped_v3.css"


def test_s1501_endpoint_map_exists_and_covers_system():
    data = json.loads(MAP.read_text(encoding="utf-8"))
    assert data["build_id"] == "v19.89.8-s1501-s1600-endpoint-mapped-final-operator-dashboard-v3"
    assert data["summary"]["endpoint_count"] >= 595
    assert len(data["endpoints"]) == data["summary"]["endpoint_count"]
    assert data["summary"]["method_counts"].get("GET", 0) >= 1


def test_s1501_dashboard_v3_files_exist_and_have_required_surfaces():
    html = HTML.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    assert DASHBOARD_MARKER in html
    assert DASHBOARD_MARKER in index
    for token in [
        "Permanent Claire command / search bar",
        "Endpoint Browser",
        "Result Pane",
        "Lifecycle Portal",
        "Evidence & Search Portal",
        "Portfolio Portal",
        "Breakthrough / Design Portal",
        "Acquisition / Package Portal",
        "Update Governance Portal",
        "Q&A / Cognitive Portal",
        "Memory / Replay Portal",
        "Existing-System Portal",
        "System Diagnostics",
    ]:
        assert token in html
    assert "window.ClaireDashboardV3" in js
    assert ".dashboard-v3" in css


def test_s1501_dashboard_route_serves_v3():
    client = TestClient(create_app())
    for path in ["/dashboard", "/dashboard/final", "/dashboard/v3", "/operator-dashboard", "/operator-cockpit", "/command-center"]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert DASHBOARD_MARKER in response.text, path


def test_s1501_dashboard_v3_assets_and_map_served():
    client = TestClient(create_app())
    for path, needle in [
        ("/dashboard/v3/assets/dashboard_endpoint_mapped_v3.css", ".dashboard-v3"),
        ("/dashboard/v3/assets/dashboard_endpoint_mapped_v3.js", "window.ClaireDashboardV3"),
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert needle in response.text, path
    response = client.get("/dashboard/endpoint-map")
    assert response.status_code == 200
    assert response.json()["build_id"] == "v19.89.8-s1501-s1600-endpoint-mapped-final-operator-dashboard-v3"


def test_s1501_existing_backend_contracts_still_work():
    client = TestClient(create_app())
    for path in ["/dashboard/payload", "/dashboard/payload/status", "/api/dashboard/active-control-map", "/dashboard/active-control-map"]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_s1501_no_unsafe_post_execution_added_to_dashboard_v3_js():
    js = JS.read_text(encoding="utf-8")
    forbidden = [
        r"method\s*:\s*['\"]POST['\"]",
        "unlockAuthority(",
        "enableRuntimeMutation(",
        "installPackage(",
        "executeCommand(",
        "startAutonomousCrawl(",
        "enableAutomaticUpdates(",
    ]
    for token in forbidden:
        if token.startswith("method"):
            assert not re.search(token, js, re.I), token
        else:
            assert token not in js, token
