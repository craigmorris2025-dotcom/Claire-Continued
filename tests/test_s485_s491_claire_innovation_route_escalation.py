from __future__ import annotations

import importlib
from pathlib import Path


def test_s485_s487_contracts_define_innovation_signals_and_routes():
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    schema = module.build_s485_innovation_signal_schema()
    scoring = module.build_s486_innovation_scoring_contract()
    routes = module.build_s487_route_escalation_contract()

    assert "breakthrough" in schema["categories"]
    assert "market_gap" in schema["categories"]
    assert scoring["sample_score"]["innovation_potential_level"] in {"low", "watch", "qualified", "high"}
    assert "breakthrough_escalation" in routes["escalation_routes"]
    assert "update_governance" in routes["escalation_routes"]

    for payload in [schema, scoring, routes]:
        for flag in module.BLOCKED_AUTHORITY:
            assert payload[flag] is False


def test_detect_innovation_potential_finds_market_engineering_and_update_routes():
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    market = module.detect_innovation_potential(
        "Can Claire find a market gap and portfolio optimization route from this trend?",
        preferred_domain="market",
    )
    assert market["innovation_potential_level"] in {"watch", "qualified", "high"}
    assert any(candidate["candidate_key"] in {"portfolio_optimization", "breakthrough_escalation"} for candidate in market["route_candidates"])

    engineering = module.detect_innovation_potential(
        "Can Claire identify a buildable breakthrough system design with feasible architecture?",
        preferred_domain="engineering",
    )
    assert any(candidate["candidate_key"] in {"engineering_design", "breakthrough_escalation"} for candidate in engineering["route_candidates"])

    update = module.detect_innovation_potential(
        "Can Claire evaluate an online update package with rollback validation and approval?"
    )
    assert any(candidate["candidate_key"] == "update_governance" for candidate in update["route_candidates"])

    for output in [market, engineering, update]:
        assert output["escalation_execution_allowed"] is False
        for flag in module.BLOCKED_AUTHORITY:
            assert output[flag] is False


def test_breakthrough_candidate_is_review_only_not_execution():
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    candidate = module.build_breakthrough_candidate(
        "Can Claire find a non-obvious breakthrough and buildable system design from this market gap?"
    )

    assert candidate["candidate_id"].startswith("breakthrough_candidate_")
    assert candidate["classification"] in {"breakthrough_review_candidate", "not_yet_qualified"}
    assert candidate["execution_allowed"] is False
    assert candidate["route_review_required"] in {True, False}

    for flag in module.BLOCKED_AUTHORITY:
        assert candidate[flag] is False


def test_s489_guardrails_block_escalation_authority():
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    guardrails = module.build_s489_escalation_guardrail_contract()
    assert "write_runtime_truth" in guardrails["blocked_escalation_authority"]
    assert "apply_online_update" in guardrails["blocked_escalation_authority"]
    assert "candidate_route" in guardrails["allowed_escalation_outputs"]
    assert "operator_review_required" in guardrails["allowed_escalation_outputs"]


def test_s490_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_innovation_route_escalation.js"
    css = root / "frontend/cockpit/shell/assets/claire_innovation_route_escalation.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireInnovationRouteEscalationVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "automaticUpdatesEnabled: false" in text
    assert "automaticEscalationExecutionEnabled: false" in text
    assert "networkRequestPerformed: false" in text


def test_s491_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    gate = module.build_s491_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["update_detection_finds_update_route"] is True
    assert gate["checks"]["breakthrough_candidate_safe"] is True
    assert (tmp_path / "s491_claire_innovation_route_escalation_stop_gate.json").exists()


def test_s485_s491_rollup_ready():
    module = importlib.import_module("claire.api.claire_innovation_route_escalation_s485_s491")

    rollup = module.build_claire_innovation_route_escalation_s485_s491(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s487"]["escalation_routes"]["breakthrough_escalation"]["route_id"] == "breakthrough_identification_and_classification"
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
