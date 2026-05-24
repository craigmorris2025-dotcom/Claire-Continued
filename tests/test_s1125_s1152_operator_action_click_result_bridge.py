from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_s1125_s1152_operator_action_result_routes_are_review_only():
    from runtime_core.app import create_app

    client = TestClient(create_app())

    result = client.get("/dashboard/operator-action/result/plan_search")
    alias = client.get("/dashboard/actions/result/plan_search")
    api_result = client.get("/api/dashboard/operator-action/result/plan_search")

    assert result.status_code == 200
    assert alias.status_code == 200
    assert api_result.status_code == 200

    payload = result.json()
    assert payload["ok"] is True
    assert payload["status"] == "review_preview_ready"
    assert payload["review_only"] is True
    assert payload["unlock_allowed"] is False
    assert payload["execution_enabled"] is False
    assert payload["network_request_performed"] is False
    assert payload["body_read_allowed"] is False
    assert payload["blocked_authority"]["runtime_mutation"] == "blocked"


def test_s1125_s1152_click_bridge_assets_bind_clicks_to_get_results():
    legacy_js = Path("frontend/command_center/modern/operator_action_click_bridge.js")
    legacy_css = Path("frontend/command_center/modern/operator_action_click_bridge.css")
    canonical_js = Path("frontend/command_center/modern/dashboard_operator_console_contract.js")

    assert not legacy_js.exists()
    assert not legacy_css.exists()
    assert canonical_js.exists()

    text = canonical_js.read_text(encoding="utf-8")
    assert "/dashboard/operator-console/contract" in text
    assert "method: \"GET\"" in text
    assert ".post(" not in text
    assert "method: \"POST\"" not in text


def test_s1125_s1152_active_index_mounts_click_bridge_when_present():
    index = Path("frontend/command_center/modern/index.html")
    assert index.exists()

    text = index.read_text(encoding="utf-8")
    assert "/dashboard" in text
    assert "dashboard_operator_console_contract.js" in text
    assert "dashboard_operator_console_contract.css" in text
    assert "operator_action_click_bridge.js" not in text
    assert "operator_action_click_bridge.css" not in text
