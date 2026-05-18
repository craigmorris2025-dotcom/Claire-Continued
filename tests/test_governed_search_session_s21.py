from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s21_search_session_builds_and_preserves_blocked_execution():
    module = importlib.import_module("claire.api.governed_search_session")
    payload = {
        "governed_route_activity_overlay": {
            "summary": {"selected_route": "governed_search"},
            "routes": [
                {"route": "governed_search", "state": "active", "owned_surface_count": 1}
            ],
        },
        "continuous_runtime_presence": {
            "presence_state": "active",
            "summary": {"active_routes": 2, "last_payload_freshness": "fresh"},
        },
    }

    session = module.build_governed_search_session(payload)

    assert session["version"] == "v19.89.8-S21"
    assert session["status"] == "active"
    assert session["session_state"] == "active"
    assert session["authority"]["runtime_authority"] == "blocked"
    assert session["authority"]["live_search_execution"] == "blocked_from_cockpit"
    assert session["session_controls"]["execution_authority"] == "blocked"
    assert session["session_controls"]["manual_review_required"] is True
    assert session["session_controls"]["automatic_runtime_mutation"] is False


def test_s21_search_session_detects_degraded_search_route():
    module = importlib.import_module("claire.api.governed_search_session")
    payload = {
        "governed_route_activity_overlay": {
            "routes": [{"route": "governed_search", "state": "degraded"}]
        }
    }

    session = module.build_governed_search_session(payload)
    assert session["session_state"] == "degraded"


def test_s21_attach_search_session_preserves_payload():
    module = importlib.import_module("claire.api.governed_search_session")
    updated = module.attach_governed_search_session({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_search_session" in updated
    assert updated["governed_search_session"]["authority"]["runtime_authority"] == "blocked"


def test_s21_frontend_assets_are_presentation_only_and_disabled():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_search_session.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_search_session.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S21" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "disabled" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
