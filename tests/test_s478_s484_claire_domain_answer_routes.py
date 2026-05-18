from __future__ import annotations

import importlib
from pathlib import Path


def test_s478_s480_route_contracts_exist_and_are_safe():
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    market = module.build_s478_market_answer_route_contract()
    research = module.build_s479_research_answer_route_contract()
    engineering = module.build_s480_engineering_answer_route_contract()

    assert market["route"]["route_id"] == "market_intelligence_route"
    assert research["route"]["route_id"] == "research_intelligence_route"
    assert engineering["route"]["route_id"] == "engineering_intelligence_route"

    for payload in [market, research, engineering]:
        for flag in module.BLOCKED_AUTHORITY:
            assert payload[flag] is False


def test_domain_route_inference_handles_market_research_engineering_and_cross_domain():
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    assert module.infer_domain_route("Can Claire analyze this market trend and pricing opportunity?")["selected_domain_route"] == "market"
    assert module.infer_domain_route("Can Claire review research evidence and source quality?")["selected_domain_route"] == "research"
    assert module.infer_domain_route("Can Claire assess whether this system architecture is buildable?")["selected_domain_route"] == "engineering"
    assert module.infer_domain_route("Compare market demand, research evidence, and engineering feasibility.")["selected_domain_route"] == "cross_domain"


def test_domain_answer_route_outputs_use_evidence_and_knowledge_registry():
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    market = module.build_domain_answer_route("Can Claire analyze this market trend and demand signal?", preferred_domain="market")
    assert market["route_selection"]["selected_domain_route"] == "market"
    assert market["evidence_answer"]["evidence_basket"]["source_count"] >= 1
    assert market["knowledge_results"]["results"]
    assert "portfolio_implication" in market["route_sections"]

    research = module.build_domain_answer_route("Can Claire review the research evidence and source quality?", preferred_domain="research")
    assert research["route_selection"]["selected_domain_route"] == "research"
    assert "claim_support" in research["route_sections"]

    engineering = module.build_domain_answer_route("Can Claire assess if this system architecture is buildable?", preferred_domain="engineering")
    assert engineering["route_selection"]["selected_domain_route"] == "engineering"
    assert "buildability_read" in engineering["route_sections"]
    assert "design_route_potential" in engineering["route_sections"]

    for output in [market, research, engineering]:
        for flag in module.BLOCKED_AUTHORITY:
            assert output[flag] is False


def test_s481_cross_domain_synthesis_and_s482_builder():
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    cross_contract = module.build_s481_cross_domain_synthesis_contract()
    assert cross_contract["sample_route"]["selected_domain_route"] == "cross_domain"

    builder = module.build_s482_domain_route_response_builder_contract()
    assert "market" in builder["supported_routes"]
    assert "research" in builder["supported_routes"]
    assert "engineering" in builder["supported_routes"]
    assert "cross_domain" in builder["supported_routes"]


def test_s483_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_domain_answer_routes.js"
    css = root / "frontend/cockpit/shell/assets/claire_domain_answer_routes.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireDomainAnswerRoutesVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "networkRequestPerformed: false" in text


def test_s484_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    gate = module.build_s484_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["market_output_safe"] is True
    assert gate["checks"]["cross_domain_output_safe"] is True
    assert (tmp_path / "s484_claire_domain_answer_routes_stop_gate.json").exists()


def test_s478_s484_rollup_ready():
    module = importlib.import_module("claire.api.claire_domain_answer_routes_s478_s484")

    rollup = module.build_claire_domain_answer_routes_s478_s484(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s478"]["route"]["route_id"] == "market_intelligence_route"
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
