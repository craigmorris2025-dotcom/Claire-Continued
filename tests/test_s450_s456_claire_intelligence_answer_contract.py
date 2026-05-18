from __future__ import annotations

import importlib
from pathlib import Path


def test_s450_question_classifier_routes_core_domains():
    module = importlib.import_module("claire.api.claire_intelligence_answer_contract_s450_s456")

    market = module.classify_claire_question("Can Claire analyze this market trend and demand signal?")
    assert market["domain"] == "market"
    assert market["evidence_requirement"] == "moderate_to_high"

    engineering = module.classify_claire_question("Is this system architecture buildable and feasible?")
    assert engineering["domain"] == "engineering"
    assert engineering["innovation_potential"] is True

    portfolio = module.classify_claire_question("Optimize this portfolio weighting and exposure.")
    assert portfolio["domain"] == "portfolio"

    governance = module.classify_claire_question("What safety authority is blocked?")
    assert governance["domain"] == "governance"


def test_s451_s454_contracts_define_claire_intelligence_scope():
    module = importlib.import_module("claire.api.claire_intelligence_answer_contract_s450_s456")

    profiles = module.build_s451_domain_intelligence_profiles()
    assert profiles["ready"] is True
    assert profiles["claire_identity"] == "Cognitive Learning Artificial Intelligence Research Engineering"
    for domain in ["market", "research", "engineering", "portfolio", "breakthrough", "acquisition"]:
        assert domain in profiles["domain_profiles"]

    shape = module.build_s452_answer_shape_contract()
    assert "direct_answer" in shape["answer_sections"]
    assert "innovation_potential" in shape["required_output_fields"]

    evidence = module.build_s453_evidence_requirement_contract()
    assert "high" in evidence["evidence_levels"]
    assert evidence["network_request_performed"] is False

    route = module.build_s454_innovation_route_potential_contract()
    assert route["route_logic"]["breakthrough"] == "breakthrough_escalation_gate"


def test_s450_s456_answer_contract_is_read_only_and_governed():
    module = importlib.import_module("claire.api.claire_intelligence_answer_contract_s450_s456")

    answer = module.build_claire_intelligence_answer(
        "Can Claire research this engineering gap and identify a breakthrough design route?",
        context={"payload": "available"},
    )

    assert answer["classification"]["domain"] in {"research", "engineering", "breakthrough"}
    assert answer["direct_answer"]
    assert answer["innovation_potential"] is True
    assert answer["governance_state"]["backend_owns_truth"] is True

    for flag in module.BLOCKED_AUTHORITY:
        assert answer[flag] is False
        assert answer["governance_state"][flag] is False


def test_s455_assets_exist_and_preserve_blocked_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.js"
    css = root / "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireIntelligenceAnswerContractVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "autonomousExecutionEnabled: false" in text
    assert "networkRequestPerformed: false" in text


def test_s456_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_intelligence_answer_contract_s450_s456")

    gate = module.build_s456_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["s455_assets_exist"] is True
    assert (tmp_path / "s456_claire_intelligence_answer_contract_stop_gate.json").exists()


def test_s450_s456_rollup_ready():
    module = importlib.import_module("claire.api.claire_intelligence_answer_contract_s450_s456")

    rollup = module.build_claire_intelligence_answer_contract_s450_s456(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s450"]["ready"] is True
    assert rollup["contracts"]["s455"]["assets"]["js_exists"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
