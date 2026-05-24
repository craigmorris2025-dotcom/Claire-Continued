from __future__ import annotations

import importlib


def test_s901_s928_payload_preserves_all_blocks_and_reports_current_stage():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_web_search_convergence")
    payload = module.build_convergence_payload()

    assert payload["phase"] == "S901-S928"
    assert payload["highest_stage"] == "S928"
    assert payload["status"] == "dashboard_convergence_ready"
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True

    blocked = payload["blocked_capabilities"]
    assert blocked["live_web_execution_enabled"] is False
    assert blocked["search_provider_execution_enabled"] is False
    assert blocked["browser_execution_enabled"] is False
    assert blocked["network_request_performed"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["autonomous_crawling_enabled"] is False
    assert blocked["automatic_updates_enabled"] is False
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["package_download_performed"] is False
    assert blocked["package_install_performed"] is False
    assert blocked["command_execution_enabled"] is False


def test_s901_s928_actions_are_registered_but_non_executable():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_web_search_convergence")
    actions = module.build_actions()

    assert len(actions) >= 7
    assert all(action["safe_to_show"] is True for action in actions)
    assert all(action["executable_now"] is False for action in actions)
    assert {action["source"] for action in actions} >= {
        "source_policy",
        "metadata_activation_preflight",
        "controlled_metadata_search",
        "search_result_review",
        "body_read_gate",
        "source_ingestion",
    }


def test_s901_s928_payload_owners_cover_s576_to_s900_runway():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_web_search_convergence")
    payload = module.build_convergence_payload()
    owners = payload["payload_owners"]
    stage_ranges = {owner["stage_range"] for owner in owners}

    assert "S576-S582" in stage_ranges
    assert "S681-S708" in stage_ranges
    assert "S779-S834" in stage_ranges
    assert "S835-S900" in stage_ranges
    assert payload["convergence_summary"]["payload_owner_count"] >= 16


def test_s901_s928_cards_are_normalized_for_cockpit_tabs():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_web_search_convergence")
    payload = module.build_convergence_payload()

    assert len(payload["governed_web_cards"]) >= 4
    assert len(payload["evidence_cards"]) >= 3
    assert all("summary" in card for card in payload["governed_web_cards"])
    assert all(card["raw_json_secondary"] is True for card in payload["evidence_cards"])


def test_s901_s928_route_module_exposes_router():
    routes = importlib.import_module("runtime_core.api.governed_cockpit_web_search_convergence_routes")
    assert hasattr(routes, "router")
    paths = {route.path for route in routes.router.routes}
    assert "/api/cockpit/convergence/payload" in paths
    assert "/api/cockpit/convergence/actions" in paths
    assert "/api/cockpit/dashboard-sync/payload" in paths
    assert "/api/internet/s928-stop-gate" in paths


def test_s901_s928_optional_app_registration_does_not_break_create_app():
    app_module = importlib.import_module("runtime_core.app")
    app = app_module.create_app()
    assert app is not None


def test_s901_s928_stop_gate_reports_safe_forward_motion():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_web_search_convergence")
    gate = module.build_stop_gate()

    assert gate["phase"] == "S901-S928"
    assert gate["passed"] is True
    assert gate["checks"]["actions_registered_for_cockpit"] is True
    assert gate["checks"]["live_web_still_blocked"] is True
    assert gate["checks"]["body_read_still_blocked"] is True
    assert gate["checks"]["runtime_mutation_still_blocked"] is True
