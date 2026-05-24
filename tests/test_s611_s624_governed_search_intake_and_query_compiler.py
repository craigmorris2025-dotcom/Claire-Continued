from __future__ import annotations

import importlib


def test_s611_source_intake_payload_preserves_blocked_authority():
    module = importlib.import_module("runtime_core.governance.governed_source_evidence_intake")
    payload = module.build_source_evidence_intake_payload("Claire source updates")
    assert payload["phase"] == "S611-S617"
    assert payload["authority"]["network_request_performed"] is False
    assert payload["authority"]["body_read_allowed"] is False
    assert payload["authority"]["runtime_mutation_enabled"] is False
    assert payload["summary"]["cards_total"] >= 5


def test_s612_source_cards_are_metadata_only_review_descriptors():
    module = importlib.import_module("runtime_core.governance.governed_source_evidence_intake")
    cards = module.build_source_evidence_cards("official docs update")
    assert cards
    assert all(card["card_type"] == "source_evidence_intake" for card in cards)
    assert all(card["network_performed"] is False for card in cards)
    assert all(card["body_text"] is None for card in cards)
    assert any(card["source_family"] == "official_docs" for card in cards)


def test_s618_query_compiler_builds_plan_without_execution():
    module = importlib.import_module("runtime_core.governance.governed_query_compiler")
    plan = module.build_governed_query_plan("official docs release notes for Claire update")
    assert plan["phase"] == "S618-S624"
    assert plan["status"] == "compiled_not_executed"
    assert plan["authority"]["search_provider_execution_enabled"] is False
    assert plan["authority"]["network_request_performed"] is False
    assert plan["compiled_queries"]
    assert plan["source_scope"][0]["network_execution_allowed"] is False


def test_s619_query_intent_flags_execution_language_but_keeps_it_blocked():
    module = importlib.import_module("runtime_core.governance.governed_query_compiler")
    plan = module.build_governed_query_plan("install package update command release notes")
    assert "execution_or_install_language_detected_but_blocked" in plan["intent"]["risk_flags"]
    assert plan["trust_constraints"]["body_reads_blocked"] is True
    assert plan["stop_gate"]["search_execution_allowed"] is False


def test_s620_route_modules_expose_expected_paths():
    intake_routes = importlib.import_module("runtime_core.api.governed_source_evidence_intake_routes")
    compiler_routes = importlib.import_module("runtime_core.api.governed_query_compiler_routes")
    paths = {route.path for route in intake_routes.router.routes} | {route.path for route in compiler_routes.router.routes}
    assert "/api/evidence/source/intake" in paths
    assert "/api/evidence/source/intake/cards" in paths
    assert "/api/search/governed/query/compile" in paths
    assert "/api/search/governed/query/payload" in paths


def test_s621_optional_app_registration_does_not_break_create_app():
    app_module = importlib.import_module("runtime_core.app")
    app = app_module.create_app()
    route_paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/api/evidence/source/intake" in route_paths
    assert "/api/search/governed/query/compile" in route_paths


def test_s624_combined_payloads_are_cockpit_ready():
    intake = importlib.import_module("runtime_core.governance.governed_source_evidence_intake")
    compiler = importlib.import_module("runtime_core.governance.governed_query_compiler")
    intake_payload = intake.build_source_evidence_intake_payload("market signal source policy")
    compiler_payload = compiler.build_query_compiler_payload("market signal source policy")
    assert intake_payload["stop_gate"]["gate_id"] == "S617"
    assert compiler_payload["plan"]["stop_gate"]["gate_id"] == "S624"
    assert len(compiler_payload["cards"]) >= 4
    assert any(action["performs_network"] is False for action in compiler_payload["actions"])

