from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.governed_runtime_spine_s106_s112 import (
    build_canonical_runtime_spine,
    build_lifecycle_authority_map,
    build_evidence_to_lifecycle_bridge,
    build_cockpit_operations_fetch_map,
    build_operator_control_read_model,
    build_governed_search_control_read_model,
    build_dashboard_managed_demo,
)
from runtime_core.api.governed_runtime_spine_routes_s106_s112 import include_governed_runtime_spine_routes


def test_s106_canonical_runtime_spine_is_ready():
    spine = build_canonical_runtime_spine()
    assert spine["spine_version"] == "S106"
    assert spine["status"] == "runtime_spine_ready"
    assert spine["authority_model"]["single_runtime_state_authority"] is True
    assert spine["locks"]["runtime_truth_write_blocked"] is True
    assert len(spine["stage_state"]) == 12


def test_s107_authority_map_blocks_dangerous_authority():
    authority = build_lifecycle_authority_map(build_canonical_runtime_spine())
    assert authority["authority_map_version"] == "S107"
    assert authority["owners"]["cockpit"] == "presentation_only"
    assert authority["blocked_authorities"]["autonomous_execution"] is True
    assert authority["blocked_authorities"]["automatic_updates"] is True


def test_s108_evidence_to_lifecycle_bridge_exists():
    bridge = build_evidence_to_lifecycle_bridge(build_canonical_runtime_spine())
    assert bridge["bridge_version"] == "S108"
    assert bridge["status"] == "evidence_lifecycle_bridge_ready"
    assert bridge["runtime_truth_write"] == "blocked"
    assert len(bridge["mapping"]) >= 6


def test_s109_cockpit_operations_fetch_map_is_read_only():
    fetch_map = build_cockpit_operations_fetch_map(build_canonical_runtime_spine())
    assert fetch_map["fetch_map_version"] == "S109"
    assert fetch_map["read_only"] is True
    assert "/api/governed/runtime-spine" in fetch_map["fetch_map"].values()


def test_s110_operator_control_read_model():
    control = build_operator_control_read_model(build_canonical_runtime_spine())
    assert control["control_model_version"] == "S110"
    assert control["action_authority"] == "manual_operator_only"
    assert "approve" in control["available_operator_actions"]
    assert control["runtime_truth_write"] == "blocked"


def test_s111_governed_search_control_read_model():
    search = build_governed_search_control_read_model(build_canonical_runtime_spine())
    assert search["search_control_model_version"] == "S111"
    assert search["manual_probe_required"] is True
    assert search["continuous_crawling"] == "blocked"
    assert search["automatic_updates"] == "blocked"


def test_s112_dashboard_managed_demo_ready():
    demo = build_dashboard_managed_demo(build_canonical_runtime_spine())
    assert demo["dashboard_demo_version"] == "S112"
    assert demo["status"] == "dashboard_managed_demo_ready"
    assert demo["locks"]["autonomous_execution_blocked"] is True


def test_s106_s112_routes_mount_and_return_200():
    app = FastAPI()
    include_governed_runtime_spine_routes(app)
    client = TestClient(app)
    routes = [
        "/api/governed/runtime-spine",
        "/api/governed/runtime-spine/authority-map",
        "/api/governed/runtime-spine/evidence-bridge",
        "/api/governed/runtime-spine/fetch-map",
        "/api/governed/runtime-spine/operator-control",
        "/api/governed/runtime-spine/search-control",
        "/api/governed/runtime-spine/dashboard-demo",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route
    openapi = client.get("/openapi.json").json()
    assert "/api/governed/runtime-spine" in openapi["paths"]
    assert "/api/governed/runtime-spine/dashboard-demo" in openapi["paths"]
