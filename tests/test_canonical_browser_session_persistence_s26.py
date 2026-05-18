from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s26_browser_session_builds_and_preserves_authority():
    module = importlib.import_module("claire.api.canonical_browser_session_persistence")
    payload = {
        "continuous_browser_runtime_loop": {
            "loop_state": "continuous_observation",
            "summary": {"selected_route": "portfolio", "payload_freshness": "fresh"},
        },
        "runtime_continuity_visualization": {
            "continuity_state": "continuous",
            "summary": {"selected_route": "portfolio"},
        },
        "governed_operator_workflow": {
            "summary": {"workflow_total": 2, "manual_review_required": True},
        },
        "governed_evidence_basket": {
            "summary": {"evidence_total": 3},
        },
    }

    session = module.build_browser_session_persistence(payload)

    assert session["version"] == "v19.89.8-S26"
    assert session["status"] == "active"
    assert session["authority"]["runtime_authority"] == "blocked"
    assert session["authority"]["browser_execution_authority"] == "blocked"
    assert session["authority"]["runtime_mutation_enabled"] is False
    assert session["authority"]["autonomous_execution_expansion"] is False
    assert session["persistence_policy"]["contains_runtime_truth"] is False
    assert session["persistence_policy"]["write_back_to_runtime"] is False
    assert session["session_snapshot"]["selected_route"] == "portfolio"


def test_s26_attach_browser_session_preserves_payload():
    module = importlib.import_module("claire.api.canonical_browser_session_persistence")
    updated = module.attach_browser_session_persistence({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "canonical_browser_session_persistence" in updated
    assert updated["canonical_browser_session_persistence"]["authority"]["runtime_authority"] == "blocked"


def test_s26_frontend_assets_are_presentation_only_storage():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "canonical_browser_session_persistence.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "canonical_browser_session_persistence.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S26" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "localStorage" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
