from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s20_presence_builds_from_payload_and_preserves_authority():
    module = importlib.import_module("claire.api.continuous_runtime_presence")

    payload = {
        "governed_runtime_timeline": {
            "summary": {
                "last_payload_freshness": "fresh",
                "last_connection_state": "connected",
            }
        },
        "governed_route_activity_overlay": {
            "summary": {
                "selected_route": "portfolio",
                "state_counts": {"active": 2, "degraded": 0, "recovering": 0},
            }
        },
        "canonical_cockpit_surface_health": {
            "summary": {"issue_total": 0}
        },
    }

    presence = module.build_continuous_runtime_presence(payload)

    assert presence["version"] == "v19.89.8-S20"
    assert presence["status"] == "active"
    assert presence["presence_state"] == "active"
    assert presence["authority"]["runtime_authority"] == "blocked"
    assert presence["authority"]["cockpit_presentation_only"] is True
    assert presence["authority"]["autonomous_execution_expansion"] is False
    assert presence["summary"]["selected_route"] == "portfolio"


def test_s20_presence_detects_degraded_state():
    module = importlib.import_module("claire.api.continuous_runtime_presence")
    payload = {
        "governed_route_activity_overlay": {
            "summary": {"state_counts": {"degraded": 1}}
        },
        "canonical_cockpit_surface_health": {
            "summary": {"issue_total": 0}
        },
    }

    presence = module.build_continuous_runtime_presence(payload)
    assert presence["presence_state"] == "degraded"


def test_s20_attach_presence_preserves_payload():
    module = importlib.import_module("claire.api.continuous_runtime_presence")
    updated = module.attach_continuous_runtime_presence({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "continuous_runtime_presence" in updated
    assert updated["continuous_runtime_presence"]["authority"]["runtime_authority"] == "blocked"


def test_s20_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "continuous_runtime_presence.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "continuous_runtime_presence.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S20" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
