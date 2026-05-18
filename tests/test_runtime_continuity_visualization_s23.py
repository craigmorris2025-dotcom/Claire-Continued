from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s23_runtime_continuity_builds_and_preserves_authority():
    module = importlib.import_module("claire.api.runtime_continuity_visualization")
    payload = {
        "governed_runtime_timeline": {
            "summary": {"last_terminal_state": "portfolio_action_ready", "last_payload_freshness": "fresh"},
            "events": [{"id": "t1"}],
        },
        "governed_route_activity_overlay": {
            "summary": {"selected_route": "portfolio", "state_counts": {"active": 1}},
        },
        "continuous_runtime_presence": {
            "presence_state": "active",
            "summary": {"last_payload_freshness": "fresh"},
        },
        "governed_evidence_basket": {
            "summary": {"evidence_total": 2},
            "items": [{"id": "e1"}, {"id": "e2"}],
        },
    }

    continuity = module.build_runtime_continuity(payload)

    assert continuity["version"] == "v19.89.8-S23"
    assert continuity["status"] == "active"
    assert continuity["continuity_state"] == "continuous"
    assert continuity["authority"]["runtime_authority"] == "blocked"
    assert continuity["authority"]["cockpit_presentation_only"] is True
    assert continuity["authority"]["autonomous_execution_expansion"] is False
    assert len(continuity["continuity_chain"]) == 4


def test_s23_runtime_continuity_detects_degraded_route():
    module = importlib.import_module("claire.api.runtime_continuity_visualization")
    payload = {
        "governed_route_activity_overlay": {
            "summary": {"state_counts": {"degraded": 1}},
        }
    }

    continuity = module.build_runtime_continuity(payload)
    assert continuity["continuity_state"] == "degraded"


def test_s23_attach_runtime_continuity_preserves_payload():
    module = importlib.import_module("claire.api.runtime_continuity_visualization")
    updated = module.attach_runtime_continuity({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "runtime_continuity_visualization" in updated
    assert updated["runtime_continuity_visualization"]["authority"]["runtime_authority"] == "blocked"


def test_s23_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "runtime_continuity_visualization.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "runtime_continuity_visualization.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S23" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
