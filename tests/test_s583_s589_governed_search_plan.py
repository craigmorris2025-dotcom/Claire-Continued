from __future__ import annotations

from pathlib import Path


def test_s583_s589_search_plan_payload_preserves_all_blocks():
    from runtime_core.governance.governed_search_plan import get_governed_search_plan_payload

    payload = get_governed_search_plan_payload()
    assert payload["version"] == "v19.89.8-S583-S589"
    assert payload["readiness"] == "governed_search_plan_ready_execution_blocked"
    assert payload["summary"]["total_plans"] >= 5
    assert payload["stop_gate"]["build"] == "S589"

    blocked = payload["blocked_capabilities"]
    assert blocked["live_web_execution_enabled"] is False
    assert blocked["browser_execution_enabled"] is False
    assert blocked["search_provider_execution_enabled"] is False
    assert blocked["network_request_performed"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["autonomous_crawling_enabled"] is False
    assert blocked["automatic_updates_enabled"] is False
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["package_download_performed"] is False
    assert blocked["package_install_performed"] is False
    assert blocked["command_execution_enabled"] is False


def test_s583_s589_query_intent_risk_and_scope_are_visible():
    from runtime_core.governance.governed_search_plan import build_search_plan

    technical = build_search_plan("Check FastAPI docs for Pydantic compatibility")
    assert technical["intent"] == "technical_research"
    assert technical["execution_allowed"] is False
    assert technical["provider_probe_allowed"] is False
    assert technical["network_request_performed"] is False
    assert technical["body_read_allowed"] is False
    assert technical["source_scope"]["operator_review_required"] is True
    assert "tier_1_authoritative" in technical["source_scope"]["preferred_trust_tiers"]

    risky = build_search_plan("download and install package then execute powershell automatic update")
    assert risky["risk_flags"]
    assert risky["execution_allowed"] is False
    assert any(flag["term"] == "install" for flag in risky["risk_flags"])
    assert any(flag["term"] == "download" for flag in risky["risk_flags"])


def test_s583_s589_cards_actions_and_evidence_are_cockpit_ready_but_blocked():
    from runtime_core.governance.governed_search_plan import get_governed_search_plan_payload

    payload = get_governed_search_plan_payload()
    assert payload["search_plan_cards"]
    assert payload["governed_actions"]
    assert payload["evidence_cards"]
    assert all(card["policy"]["execution_allowed"] is False for card in payload["search_plan_cards"])
    assert all(card["policy"]["body_read_allowed"] is False for card in payload["search_plan_cards"])
    assert all(action["enabled"] is False for action in payload["governed_actions"])
    assert all(action["execution_blocked"] is True for action in payload["governed_actions"])
    assert all(card["network_request_performed"] is False for card in payload["evidence_cards"])


def test_s583_s589_api_route_functions_return_governed_search_payloads():
    from runtime_core.api.governed_search_plan_routes import (
        read_governed_search_actions,
        read_governed_search_cards,
        read_governed_search_plans,
        read_governed_search_policy,
        read_governed_search_sample,
        read_governed_search_status,
    )

    plans = read_governed_search_plans()
    cards = read_governed_search_cards()
    actions = read_governed_search_actions()
    policy = read_governed_search_policy()
    sample = read_governed_search_sample("source trust tier discovery plan")
    status = read_governed_search_status()

    assert plans["cockpit_panels"]["governed_web"]["cards"]
    assert cards["search_plan_cards"]
    assert actions["governed_actions"]
    assert policy["search_intents"]
    assert sample["plan"]["intent"] == "source_discovery"
    assert sample["network_request_performed"] is False
    assert status["stop_gate"]["next_phase"] == "S590-S596 Evidence Card Normalization + Review Surface"


def test_s583_s589_cockpit_assets_exist_and_point_to_governed_search_endpoints():
    js_path = Path("frontend/cockpit/assets/claire_governed_search_plan.js")
    css_path = Path("frontend/cockpit/assets/claire_governed_search_plan.css")
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "/api/search/governed/plans" in js
    assert "/api/search/governed/actions" in js
    assert "Governed Search Plan" in js
    assert ".claire-search-plan-panel" in css

