from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s30_multi_workspace_builds_review_state_and_preserves_authority():
    module = importlib.import_module("runtime_core.api.governed_multi_workspace_orchestration")
    payload = {
        "governed_runtime_workspace_continuity": {
            "workspace_state": "review_required",
            "summary": {"selected_route": "portfolio", "workflow_total": 2, "evidence_total": 3},
        },
        "governed_operational_session_orchestration": {
            "session_state": "review_required",
            "summary": {"selected_route": "portfolio"},
        },
        "multi_panel_runtime_cohesion": {
            "cohesion_state": "cohesive",
            "summary": {"missing_total": 0, "drift_total": 0, "payload_propagation": "complete"},
        },
        "governed_route_activity_overlay": {
            "routes": [{"route": "portfolio", "state": "active", "selected": True, "owned_surface_count": 1}]
        },
        "governed_evidence_basket": {"summary": {"evidence_total": 3}},
        "governed_operator_workflow": {"summary": {"workflow_total": 2, "manual_review_required": True}},
    }

    topology = module.build_multi_workspace_orchestration(payload)

    assert topology["version"] == "v19.89.8-S30"
    assert topology["status"] == "active"
    assert topology["topology_state"] == "review_required"
    assert topology["authority"]["runtime_authority"] == "blocked"
    assert topology["authority"]["browser_execution_authority"] == "blocked"
    assert topology["authority"]["multi_workspace_mutation_enabled"] is False
    assert topology["authority"]["autonomous_execution_expansion"] is False
    assert topology["summary"]["workspace_total"] == 1


def test_s30_multi_workspace_blocks_on_drift():
    module = importlib.import_module("runtime_core.api.governed_multi_workspace_orchestration")
    topology = module.build_multi_workspace_orchestration({
        "multi_panel_runtime_cohesion": {"summary": {"missing_total": 0, "drift_total": 1}}
    })
    assert topology["topology_state"] == "blocked"


def test_s30_multi_workspace_partial_on_missing_panels():
    module = importlib.import_module("runtime_core.api.governed_multi_workspace_orchestration")
    topology = module.build_multi_workspace_orchestration({
        "multi_panel_runtime_cohesion": {"summary": {"missing_total": 2, "drift_total": 0}}
    })
    assert topology["topology_state"] == "partial"


def test_s30_attach_multi_workspace_preserves_payload():
    module = importlib.import_module("runtime_core.api.governed_multi_workspace_orchestration")
    updated = module.attach_multi_workspace_orchestration({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_multi_workspace_orchestration" in updated
    assert updated["governed_multi_workspace_orchestration"]["authority"]["runtime_authority"] == "blocked"


def test_s30_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_multi_workspace_orchestration.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_multi_workspace_orchestration.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S30" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
