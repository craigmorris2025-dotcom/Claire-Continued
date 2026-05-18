from __future__ import annotations

from pathlib import Path

import importlib


ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "frontend" / "cockpit" / "s45_bridge" / "cockpit_shell_bridge.html"
JS = ROOT / "frontend" / "cockpit" / "s45_bridge" / "s45_shell_mount.js"
CSS = ROOT / "frontend" / "cockpit" / "s45_bridge" / "s45_shell_mount.css"


def test_s46r1_modern_cockpit_layout_contract_is_safe():
    module = importlib.import_module("claire.api.s46_modern_cockpit_layout_contract")
    contract = module.build_modern_cockpit_layout_contract()

    assert contract["version"] == "v19.89.8-S46R1-R4"
    assert contract["status"] == "modern_cockpit_layout_contract_ready"
    assert contract["zone_count"] == 4
    assert contract["backend_owns_truth"] is True
    assert contract["cockpit_presentation_only"] is True
    assert contract["runtime_truth_mutation_allowed"] is False

    for zone in contract["zones"]:
        assert zone["visible"] is True
        assert zone["presentation_only"] is True
        assert zone["runtime_truth_mutation_allowed"] is False
        assert zone["operator_mutation_enabled"] is False


def test_s46r2_modern_cockpit_layout_contract_verifies_cleanly():
    module = importlib.import_module("claire.api.s46_modern_cockpit_layout_contract")
    verification = module.verify_modern_cockpit_layout_contract()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["zone_count"] == 4


def test_s46r3_shell_bridge_assets_exist_and_are_presentation_only():
    assert SHELL.exists()
    assert JS.exists()
    assert CSS.exists()

    html = SHELL.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8").lower()

    assert "Claire S45 Cockpit Shell Bridge" in html
    assert "data-runtime-truth-mutation-allowed=\"false\"" in html
    assert "runtimeTruthMutationAllowed: false" in js
    assert "operatorMutationEnabled: false" in js
    assert 'method: "GET"' in js
    assert "read_only_artifact" in js
    assert "presentation-only" in css
