from __future__ import annotations

import importlib


def test_s597_provider_registry_is_visible_and_blocked():
    module = importlib.import_module("runtime_core.governance.governed_provider_readiness")
    registry = module.provider_registry()
    assert registry["version"].endswith("S597-S603")
    assert registry["summary"]["provider_count"] >= 4
    assert registry["summary"]["execution_allowed_count"] == 0
    assert registry["summary"]["network_allowed_count"] == 0
    assert registry["summary"]["body_read_allowed_count"] == 0
    assert registry["blocked_flags"]["live_web_execution_enabled"] is False
    assert registry["blocked_flags"]["automatic_updates_enabled"] is False
    assert registry["blocked_flags"]["runtime_mutation_enabled"] is False


def test_s598_trust_tiers_and_policy_are_present():
    module = importlib.import_module("runtime_core.governance.governed_provider_readiness")
    policy = module.provider_policy()
    tiers = policy["trust_tiers"]
    assert "tier_1_official" in tiers
    assert "tier_3_open_web" in tiers
    assert "tier_4_blocked" in tiers
    assert any("Provider execution remains disabled" in rule for rule in policy["rules"])
    assert any("Body reads remain disabled" in rule for rule in policy["rules"])


def test_s599_provider_cards_are_cockpit_ready():
    module = importlib.import_module("runtime_core.governance.governed_provider_readiness")
    cards = module.provider_cards()
    assert cards["card_count"] >= 4
    for card in cards["cards"]:
        assert card["card_id"].startswith("provider_card::")
        assert card["ui_region"] == "Governed Web / Sources"
        assert card["execution_allowed"] is False
        assert card["network_allowed"] is False
        assert card["body_read_allowed"] is False
        assert card["blocked_reason"]


def test_s600_actions_are_visible_but_non_executable():
    module = importlib.import_module("runtime_core.governance.governed_provider_readiness")
    actions = module.provider_actions()
    assert actions["action_count"] >= 3
    for action in actions["actions"]:
        assert action["enabled"] is False
        assert action["blocked"] is True
        assert action["blocked_reason"]
        assert action["would_require"]


def test_s601_payload_and_stop_gate_preserve_blocks():
    module = importlib.import_module("runtime_core.governance.governed_provider_readiness")
    payload = module.provider_payload()
    stop_gate = module.build_stop_gate()
    assert payload["status"]["execution_allowed"] is False
    assert payload["status"]["network_allowed"] is False
    assert payload["status"]["body_read_allowed"] is False
    assert stop_gate["stop_gate"] == "S603"
    assert stop_gate["passed"] is True
    assert "runtime_mutation_enabled" in stop_gate["must_remain_blocked"]


def test_s602_routes_export_provider_readiness_contract():
    routes = importlib.import_module("runtime_core.api.governed_provider_readiness_routes")
    route_paths = {route.path for route in routes.router.routes}
    assert "/api/search/providers/readiness" in route_paths
    assert "/api/search/providers/cards" in route_paths
    assert "/api/search/providers/actions" in route_paths
    assert "/api/search/providers/payload" in route_paths
    assert "/api/sources/providers/cards" in route_paths


def test_s603_optional_app_registration_does_not_break_create_app():
    app_module = importlib.import_module("runtime_core.app")
    if hasattr(app_module, "create_app"):
        app = app_module.create_app()
        assert app is not None
