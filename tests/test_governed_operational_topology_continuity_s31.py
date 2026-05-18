from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s31_topology_continuity_builds_review_state_and_preserves_authority():
    module = importlib.import_module("claire.api.governed_operational_topology_continuity")
    payload = {
        "governed_multi_workspace_orchestration": {
            "topology_state": "review_required",
            "summary": {"workspace_total": 2, "selected_route": "portfolio", "manual_review_required": True},
        },
        "governed_runtime_workspace_continuity": {
            "workspace_state": "review_required",
            "summary": {"selected_route": "portfolio"},
        },
        "governed_operational_session_orchestration": {
            "session_state": "review_required",
            "summary": {"selected_route": "portfolio"},
        },
        "multi_panel_runtime_cohesion": {
            "cohesion_state": "cohesive",
            "summary": {"missing_total": 0, "drift_total": 0, "payload_propagation": "complete"},
        },
        "continuous_browser_runtime_loop": {
            "loop_state": "continuous_observation",
            "summary": {"payload_freshness": "fresh"},
        },
    }

    continuity = module.build_operational_topology_continuity(payload)

    assert continuity["version"] == "v19.89.8-S31"
    assert continuity["status"] == "active"
    assert continuity["continuity_state"] == "review_required"
    assert continuity["authority"]["runtime_authority"] == "blocked"
    assert continuity["authority"]["browser_execution_authority"] == "blocked"
    assert continuity["authority"]["topology_mutation_enabled"] is False
    assert continuity["authority"]["autonomous_execution_expansion"] is False
    assert len(continuity["continuity_chain"]) == 5


def test_s31_topology_continuity_blocks_on_drift():
    module = importlib.import_module("claire.api.governed_operational_topology_continuity")
    continuity = module.build_operational_topology_continuity({
        "governed_multi_workspace_orchestration": {"topology_state": "coordinated", "summary": {"authority_drift_total": 1}}
    })
    assert continuity["continuity_state"] == "blocked"


def test_s31_topology_continuity_partial_on_missing_panels():
    module = importlib.import_module("claire.api.governed_operational_topology_continuity")
    continuity = module.build_operational_topology_continuity({
        "governed_multi_workspace_orchestration": {"topology_state": "coordinated", "summary": {"missing_panel_total": 2}}
    })
    assert continuity["continuity_state"] == "partial"


def test_s31_attach_topology_continuity_preserves_payload():
    module = importlib.import_module("claire.api.governed_operational_topology_continuity")
    updated = module.attach_operational_topology_continuity({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_operational_topology_continuity" in updated
    assert updated["governed_operational_topology_continuity"]["authority"]["runtime_authority"] == "blocked"


def test_s31_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_operational_topology_continuity.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_operational_topology_continuity.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S31" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
