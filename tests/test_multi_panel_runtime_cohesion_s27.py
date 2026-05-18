from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s27_cohesion_builds_and_preserves_authority():
    module = importlib.import_module("claire.api.multi_panel_runtime_cohesion")
    payload = {
        "governed_runtime_timeline": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "governed_route_activity_overlay": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "continuous_runtime_presence": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "governed_search_session": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "governed_evidence_basket": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "runtime_continuity_visualization": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "continuous_browser_runtime_loop": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "governed_operator_workflow": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
        "canonical_browser_session_persistence": {"authority": {"runtime_authority": "blocked", "autonomous_execution_expansion": False}},
    }

    cohesion = module.build_multi_panel_runtime_cohesion(payload)

    assert cohesion["version"] == "v19.89.8-S27"
    assert cohesion["status"] == "active"
    assert cohesion["cohesion_state"] == "cohesive"
    assert cohesion["authority"]["runtime_authority"] == "blocked"
    assert cohesion["authority"]["browser_execution_authority"] == "blocked"
    assert cohesion["authority"]["runtime_mutation_enabled"] is False
    assert cohesion["authority"]["autonomous_execution_expansion"] is False
    assert cohesion["summary"]["missing_total"] == 0
    assert cohesion["summary"]["drift_total"] == 0


def test_s27_cohesion_detects_missing_panels():
    module = importlib.import_module("claire.api.multi_panel_runtime_cohesion")
    cohesion = module.build_multi_panel_runtime_cohesion({})

    assert cohesion["cohesion_state"] == "partial"
    assert cohesion["summary"]["missing_total"] >= 1


def test_s27_cohesion_detects_authority_drift():
    module = importlib.import_module("claire.api.multi_panel_runtime_cohesion")
    payload = {
        "governed_runtime_timeline": {"authority": {"runtime_authority": "enabled", "autonomous_execution_expansion": False}},
    }

    cohesion = module.build_multi_panel_runtime_cohesion(payload)

    assert cohesion["cohesion_state"] == "blocked"
    assert cohesion["summary"]["drift_total"] == 1


def test_s27_attach_cohesion_preserves_payload():
    module = importlib.import_module("claire.api.multi_panel_runtime_cohesion")
    updated = module.attach_multi_panel_runtime_cohesion({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "multi_panel_runtime_cohesion" in updated
    assert updated["multi_panel_runtime_cohesion"]["authority"]["runtime_authority"] == "blocked"


def test_s27_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "multi_panel_runtime_cohesion.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "multi_panel_runtime_cohesion.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S27" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
