from __future__ import annotations

import importlib


def test_s604_source_gap_matrix_schema_and_blocks():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    matrix = module.source_gap_matrix()
    assert matrix["version"] == "v19.89.8-S604-S610"
    assert matrix["source_family_count"] >= 5
    assert matrix["summary"]["execution_allowed"] is False
    assert matrix["summary"]["network_allowed"] is False
    assert matrix["summary"]["body_read_allowed"] is False
    assert matrix["blocked_flags"]["live_web_execution_enabled"] is False
    assert matrix["blocked_flags"]["automatic_updates_enabled"] is False
    ids = {item["source_family_id"] for item in matrix["source_gaps"]}
    assert "official_software_docs" in ids
    assert "open_web_discovery" in ids
    assert "denied_source_patterns" in ids


def test_s605_trust_tiers_and_gap_requirements_are_visible():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    matrix = module.source_gap_matrix()
    assert "tier_1_official" in matrix["trust_tiers"]
    assert "tier_4_blocked" in matrix["trust_tiers"]
    for gap in matrix["source_gaps"]:
        assert gap["missing_before_use"]
        assert gap["blocked_now"]
        assert gap["evidence_required"]
        assert gap["blocked_reason"]


def test_s606_search_scope_plans_are_planning_only():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    plans = module.search_scope_plans()
    assert plans["plan_count"] >= 4
    assert plans["policy"]["planning_only"] is True
    assert plans["policy"]["execution_allowed"] is False
    for plan in plans["plans"]:
        assert plan["execution_allowed"] is False
        assert plan["network_allowed"] is False
        assert plan["body_read_allowed"] is False
        assert plan["preferred_source_families"]
        assert plan["evidence_path"]
        assert plan["blocked_capabilities"]


def test_s607_cards_are_cockpit_ready_not_raw_json_first():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    source_cards = module.source_gap_cards()
    scope_cards = module.search_scope_cards()
    assert source_cards["presentation_mode"] == "cockpit_cards_not_raw_json"
    assert scope_cards["presentation_mode"] == "cockpit_cards_not_raw_json"
    assert source_cards["card_count"] >= 5
    assert scope_cards["card_count"] >= 4
    for card in source_cards["cards"]:
        assert card["card_id"].startswith("source_gap_card::")
        assert card["ui_region"] == "Governed Web / Source Gaps"
        assert card["execution_allowed"] is False
        assert card["network_allowed"] is False
        assert card["body_read_allowed"] is False
    for card in scope_cards["cards"]:
        assert card["card_id"].startswith("search_scope_card::")
        assert card["ui_region"] == "Governed Web / Search Scope"
        assert card["execution_allowed"] is False


def test_s608_actions_begin_populating_actions_tab_but_are_non_executable():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    actions = module.source_gap_actions()
    assert actions["action_count"] >= 4
    assert actions["all_actions_non_executable"] is True
    for action in actions["actions"]:
        assert action["target_region"]
        assert action["enabled"] is False
        assert action["blocked"] is True
        assert action["does_not_perform"]


def test_s609_payload_and_policy_preserve_no_web_update_authority():
    module = importlib.import_module("claire.governance.governed_source_gap_matrix")
    payload = module.governed_source_gap_payload()
    policy = payload["policy"]
    assert payload["status"]["readiness"] == "source_search_planning_visible_execution_blocked"
    assert payload["status"]["actions_executable"] is False
    assert any("Body reads remain disabled" in rule for rule in policy["rules"])
    assert any("Automatic updates" in rule for rule in policy["rules"])
    assert payload["blocked_flags"]["runtime_mutation_enabled"] is False
    assert payload["blocked_flags"]["package_install_performed"] is False


def test_s610_routes_and_optional_app_registration_do_not_break_create_app():
    routes = importlib.import_module("claire.api.governed_source_gap_routes")
    route_paths = {route.path for route in routes.router.routes}
    assert "/api/sources/gaps/matrix" in route_paths
    assert "/api/sources/gaps/cards" in route_paths
    assert "/api/sources/gaps/actions" in route_paths
    assert "/api/search/scope/plans" in route_paths
    assert "/api/search/scope/cards" in route_paths
    app_module = importlib.import_module("claire.app")
    if hasattr(app_module, "create_app"):
        app = app_module.create_app()
        assert app is not None
