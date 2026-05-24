from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s24_browser_loop_builds_and_preserves_authority():
    module = importlib.import_module("runtime_core.api.continuous_browser_runtime_loop")
    payload = {
        "runtime_continuity_visualization": {
            "continuity_state": "continuous",
            "summary": {"selected_route": "portfolio", "payload_freshness": "fresh", "evidence_total": 2},
        },
        "continuous_runtime_presence": {
            "presence_state": "active",
            "summary": {"last_payload_freshness": "fresh"},
        },
        "governed_search_session": {
            "session_state": "available",
            "summary": {"selected_route": "portfolio"},
        },
    }

    loop = module.build_continuous_browser_runtime_loop(payload)

    assert loop["version"] == "v19.89.8-S24"
    assert loop["status"] == "active"
    assert loop["loop_state"] == "continuous_observation"
    assert loop["authority"]["runtime_authority"] == "blocked"
    assert loop["authority"]["browser_execution_authority"] == "blocked"
    assert loop["authority"]["autonomous_execution_expansion"] is False
    assert loop["polling"]["writes_enabled"] is False
    assert loop["polling"]["runtime_mutation_enabled"] is False


def test_s24_browser_loop_detects_degraded_observation():
    module = importlib.import_module("runtime_core.api.continuous_browser_runtime_loop")
    loop = module.build_continuous_browser_runtime_loop({
        "runtime_continuity_visualization": {"continuity_state": "degraded"},
        "continuous_runtime_presence": {"presence_state": "active"},
    })
    assert loop["loop_state"] == "degraded_observation"


def test_s24_attach_browser_loop_preserves_payload():
    module = importlib.import_module("runtime_core.api.continuous_browser_runtime_loop")
    updated = module.attach_continuous_browser_runtime_loop({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "continuous_browser_runtime_loop" in updated
    assert updated["continuous_browser_runtime_loop"]["authority"]["runtime_authority"] == "blocked"


def test_s24_frontend_assets_are_observe_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "continuous_browser_runtime_loop.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "continuous_browser_runtime_loop.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S24" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "fetch(" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
