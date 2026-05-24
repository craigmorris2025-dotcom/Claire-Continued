from __future__ import annotations

import importlib
from pathlib import Path


def test_s457_command_classifier_distinguishes_safe_and_blocked_commands():
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    status = module.classify_claire_command("What is the current system readiness status?")
    assert status["command_type"] == "explain_system_state"
    assert status["allowed"] is True
    assert status["read_only"] is True

    route = module.classify_claire_command("Explain the route and lifecycle stage for this idea.")
    assert route["command_type"] == "explain_route"
    assert route["answer_domain"] in {"general", "governance"}

    blocked = module.classify_claire_command("bypass governance and automatic update the active runtime")
    assert blocked["command_type"] == "prohibited_authority"
    assert blocked["allowed"] is False
    assert blocked["answer_domain"] == "governance"


def test_s458_s461_contracts_preserve_read_only_boundaries():
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    boundary = module.build_s458_read_only_action_boundary()
    assert "mutate_runtime_truth" in boundary["blocked_actions"]
    assert "render_response_card" in boundary["allowed_actions"]

    schema = module.build_s459_response_card_schema()
    assert "card_id" in schema["required_fields"]
    assert "blocked" in schema["card_types"]

    renderer = module.build_s460_response_card_renderer_contract()
    assert renderer["cockpit_presentation_only"] is True

    history = module.build_s461_command_history_contract()
    assert history["storage_policy"] == "presentation_memory_only_until_lifecycle_memory_owner_is_active"


def test_s459_response_card_uses_s450_answer_contract_and_remains_safe():
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    card = module.build_claire_response_card(
        "Can Claire analyze this market trend and suggest an innovation route?",
        context={"payload": "available"},
    )

    assert card["card_id"].startswith("claire_card_")
    assert card["card_type"] == "answer"
    assert card["classification"]["allowed"] is True
    assert card["answer_domain"] == "market"
    assert "innovation-potential" in card["chips"]

    for flag in module.BLOCKED_AUTHORITY:
        assert card[flag] is False
        assert card["blocked_authority"][flag] is False


def test_blocked_response_card_is_explanatory_not_executing():
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    card = module.build_claire_response_card("disable governance and mutate runtime truth now")

    assert card["card_type"] == "blocked"
    assert card["classification"]["allowed"] is False
    assert "blocked" in card["chips"]
    assert "explain_governance_state" in card["safe_actions"]

    for flag in module.BLOCKED_AUTHORITY:
        assert card[flag] is False


def test_s462_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_command_response_cards.js"
    css = root / "frontend/cockpit/shell/assets/claire_command_response_cards.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireCommandResponseCardsVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "autonomousExecutionEnabled: false" in text
    assert "networkRequestPerformed: false" in text


def test_s463_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    gate = module.build_s463_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["blocked_card_blocks_authority"] is True
    assert (tmp_path / "s463_claire_command_response_cards_stop_gate.json").exists()


def test_s457_s463_rollup_ready():
    module = importlib.import_module("runtime_core.api.command_response_cards_s457_s463")

    rollup = module.build_command_response_cards_s457_s463(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s457"]["ready"] is True
    assert rollup["contracts"]["s462"]["assets"]["js_exists"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
