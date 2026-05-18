from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def test_s1069_s1096_operator_console_contract_module_is_ready_and_blocked():
    module = importlib.import_module("claire.api.dashboard_operator_console_contract")
    contract = module.build_operator_console_contract()

    assert contract["status"] == "ready"
    assert contract["phase"] == "S1069-S1096"
    assert contract["action_count"] > 0
    assert contract["unlock_allowed"] is False
    assert contract["execution_enabled"] is False
    assert contract["body_read_allowed"] is False
    assert contract["network_request_performed"] is False
    assert contract["ui_contract"]["actions_tab_should_show_controls"] is True
    assert contract["ui_contract"]["actions_chip_should_be_greater_than_zero"] is True
    assert contract["ui_contract"]["dev_stage_grid"] is False

    labels = [action["label"] for action in contract["operator_controls"]]
    assert any(label in labels for label in ["Plan a governed search", "Compile search plan"])
    assert not any(label.startswith("S1069") or label.startswith("S1096") for label in labels)


def test_s1069_s1096_operator_console_routes_mount_through_create_app():
    from claire.app import create_app

    client = TestClient(create_app())

    contract = client.get("/dashboard/operator-console/contract")
    summary = client.get("/dashboard/operator-console/summary")
    actions = client.get("/dashboard/operator-console/actions")
    preview = client.get("/dashboard/operator-console/preview/plan_search")

    assert contract.status_code == 200
    assert summary.status_code == 200
    assert actions.status_code == 200
    assert preview.status_code == 200

    contract_payload = contract.json()
    assert contract_payload["action_count"] > 0
    assert contract_payload["unlock_allowed"] is False
    assert contract_payload["fetch_contract"]["method"] == "GET"
    assert "POST" in contract_payload["fetch_contract"]["forbidden_methods"]
    assert preview.json()["execution_enabled"] is False


def test_s1069_s1096_frontend_assets_are_review_only_when_mounted():
    js = Path("frontend/command_center/modern/dashboard_operator_console_contract.js")
    css = Path("frontend/command_center/modern/dashboard_operator_console_contract.css")

    assert js.exists()
    assert css.exists()

    js_text = js.read_text(encoding="utf-8")
    assert "/dashboard/operator-console/contract" in js_text
    assert "method: \"GET\"" in js_text
    assert "No web execution" in js_text
    assert ".post(" not in js_text
    assert "runtime mutation" in js_text.lower()
    assert "command execution" in js_text.lower()
