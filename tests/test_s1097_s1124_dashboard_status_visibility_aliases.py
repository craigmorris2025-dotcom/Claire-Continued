from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_s1097_s1124_status_visibility_alias_module_is_read_only_and_ready():
    module = importlib.import_module("runtime_core.api.dashboard_status_visibility_aliases")

    visibility = module.build_dashboard_visibility_summary()
    status = module.build_dashboard_status_harmonized()

    assert visibility["ok"] is True
    assert visibility["status"] == "ready"
    assert visibility["action_count"] >= 1
    assert visibility["panels"]["actions"]["visible"] is True
    assert visibility["unlock_allowed"] is False
    assert visibility["execution_enabled"] is False
    assert visibility["body_read_allowed"] is False
    assert visibility["network_request_performed"] is False

    assert status["ok"] is True
    assert status["status"] == "ready"
    assert status["harmonized_status"] == "ready"
    assert status["action_count"] >= 1
    assert status["unlock_allowed"] is False
    assert status["blocked_authority"]["body_reads"] == "blocked"


def test_s1097_s1124_create_app_serves_status_visibility_aliases():
    from runtime_core.app import create_app

    client = TestClient(create_app())

    visibility = client.get("/dashboard/visibility/summary")
    harmonized = client.get("/dashboard/status/harmonized")
    api_visibility = client.get("/api/dashboard/visibility/summary")
    api_harmonized = client.get("/api/dashboard/status/harmonized")

    assert visibility.status_code == 200
    assert harmonized.status_code == 200
    assert api_visibility.status_code == 200
    assert api_harmonized.status_code == 200

    visibility_payload = visibility.json()
    harmonized_payload = harmonized.json()

    assert visibility_payload["action_count"] >= 1
    assert visibility_payload["panels"]["actions"]["actions_chip_should_be_greater_than_zero"] is True
    assert harmonized_payload["action_count"] >= 1
    assert harmonized_payload["chips"][2]["label"] == "Actions"
    assert harmonized_payload["chips"][2]["value"] >= 1

    assert visibility_payload["unlock_allowed"] is False
    assert harmonized_payload["unlock_allowed"] is False
    assert visibility_payload["body_read_allowed"] is False
    assert harmonized_payload["network_request_performed"] is False
