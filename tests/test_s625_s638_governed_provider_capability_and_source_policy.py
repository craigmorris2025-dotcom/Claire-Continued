from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def test_s625_provider_capability_map_preserves_execution_blocks():
    module = importlib.import_module("runtime_core.governance.governed_provider_capability_map")
    payload = module.get_provider_capability_map()

    assert payload["status"] == "provider_capability_map_ready"
    assert payload["summary"]["provider_family_count"] >= 5
    assert payload["summary"]["configured_for_execution_count"] == 0
    assert payload["blocked_execution"]["live_web_execution_enabled"] is False
    assert payload["blocked_execution"]["search_provider_execution_enabled"] is False
    assert payload["blocked_execution"]["network_request_performed"] is False
    assert payload["blocked_execution"]["body_read_allowed"] is False
    assert payload["blocked_execution"]["automatic_updates_enabled"] is False
    assert payload["blocked_execution"]["runtime_mutation_enabled"] is False


def test_s631_provider_cards_and_actions_are_cockpit_ready_not_executable():
    module = importlib.import_module("runtime_core.governance.governed_provider_capability_map")
    cards = module.build_provider_capability_cards()
    actions = module.build_provider_capability_actions()

    assert cards
    assert actions
    assert any(card["trust_tier"] == "T1_authoritative" for card in cards)
    assert any(card["trust_tier"] == "D_denied" for card in cards)
    assert all(card["execution_enabled"] is False for card in cards)
    assert all(action["executable"] is False for action in actions)


def test_s632_source_policy_controls_are_visible_but_do_not_unlock_authority():
    module = importlib.import_module("runtime_core.governance.governed_source_policy_controls")
    payload = module.get_source_policy_controls()

    assert payload["status"] == "source_policy_controls_ready"
    assert payload["summary"]["control_count"] >= 6
    assert payload["summary"]["execution_enabling_control_count"] == 0
    assert payload["authority_state"]["policy_controls_can_unlock_authority"] is False
    assert payload["blocked_execution"]["live_web_execution_enabled"] is False
    assert payload["blocked_execution"]["network_request_performed"] is False
    assert payload["blocked_execution"]["body_read_allowed"] is False
    assert payload["blocked_execution"]["package_install_performed"] is False


def test_s638_source_policy_cards_actions_and_stop_gate():
    module = importlib.import_module("runtime_core.governance.governed_source_policy_controls")
    cards = module.build_source_policy_cards()
    actions = module.build_source_policy_actions()
    stop_gate = module.get_source_policy_stop_gate()

    assert len(cards) >= 6
    assert len(actions) >= 3
    assert any(card["card_id"] == "source-policy-quarantine-policy" for card in cards)
    assert all(card["execution_enabled"] is False for card in cards)
    assert all(action["executable"] is False for action in actions)
    assert stop_gate["forward_motion_allowed"] is True
    assert stop_gate["authority_unlock_allowed"] is False


def test_s625_s638_routes_are_registered_on_create_app():
    app_module = importlib.import_module("runtime_core.app")
    client = TestClient(app_module.create_app())

    routes = [
        "/api/search/providers/capability-map",
        "/api/search/providers/capability/cards",
        "/api/search/providers/capability/actions",
        "/api/search/providers/capability/status",
        "/api/search/providers/capability/payload",
        "/api/search/providers/capability/stop-gate",
        "/api/sources/policy/controls",
        "/api/sources/policy/cards",
        "/api/sources/policy/actions",
        "/api/sources/policy/status",
        "/api/sources/policy/payload",
        "/api/sources/policy/stop-gate",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route

    provider_payload = client.get("/api/search/providers/capability/payload").json()
    policy_payload = client.get("/api/sources/policy/payload").json()
    assert provider_payload["status"] == "ready"
    assert policy_payload["status"] == "ready"
    assert provider_payload["stop_gate"]["authority_unlock_allowed"] is False
    assert policy_payload["stop_gate"]["authority_unlock_allowed"] is False


def test_s625_s638_cockpit_assets_exist_and_reference_endpoints():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "claire_governed_provider_capability_and_source_policy.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "claire_governed_provider_capability_and_source_policy.css"

    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "/api/search/providers/capability/payload" in js
    assert "/api/sources/policy/payload" in js
    assert "claire-source-policy-panel" in css


def test_s625_s638_report_written():
    report_path = ROOT / "reports" / "s625_s638_governed_provider_capability_and_source_policy_report.json"
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "S625-S638" in report
    assert "live_web_execution_enabled" in report
