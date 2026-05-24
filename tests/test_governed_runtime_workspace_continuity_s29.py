from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s29_workspace_builds_review_state_and_preserves_authority():
    module = importlib.import_module("runtime_core.api.governed_runtime_workspace_continuity")
    payload = {
        "governed_operational_session_orchestration": {
            "session_state": "review_required",
            "summary": {"selected_route": "portfolio", "workflow_total": 2, "evidence_total": 3},
            "session_bindings": [{"binding": "route_session"}],
        },
        "canonical_browser_session_persistence": {
            "session_snapshot": {"selected_route": "portfolio", "payload_freshness": "fresh"},
        },
        "governed_operator_workflow": {
            "summary": {"workflow_total": 2, "manual_review_required": True},
        },
        "governed_evidence_basket": {
            "summary": {"evidence_total": 3},
        },
        "multi_panel_runtime_cohesion": {
            "cohesion_state": "cohesive",
            "summary": {"missing_total": 0, "drift_total": 0, "payload_propagation": "complete"},
        },
        "runtime_continuity_visualization": {
            "continuity_state": "continuous",
            "summary": {"selected_route": "portfolio", "payload_freshness": "fresh"},
        },
    }

    workspace = module.build_runtime_workspace_continuity(payload)

    assert workspace["version"] == "v19.89.8-S29"
    assert workspace["status"] == "active"
    assert workspace["workspace_state"] == "review_required"
    assert workspace["workspace_id"] == "workspace:portfolio"
    assert workspace["authority"]["runtime_authority"] == "blocked"
    assert workspace["authority"]["browser_execution_authority"] == "blocked"
    assert workspace["authority"]["workspace_mutation_enabled"] is False
    assert workspace["authority"]["autonomous_execution_expansion"] is False
    assert len(workspace["workspace_dimensions"]) == 5


def test_s29_workspace_blocks_on_authority_drift():
    module = importlib.import_module("runtime_core.api.governed_runtime_workspace_continuity")
    workspace = module.build_runtime_workspace_continuity({
        "multi_panel_runtime_cohesion": {"summary": {"missing_total": 0, "drift_total": 1}}
    })
    assert workspace["workspace_state"] == "blocked"


def test_s29_workspace_partial_on_missing_panels():
    module = importlib.import_module("runtime_core.api.governed_runtime_workspace_continuity")
    workspace = module.build_runtime_workspace_continuity({
        "multi_panel_runtime_cohesion": {"summary": {"missing_total": 2, "drift_total": 0}}
    })
    assert workspace["workspace_state"] == "partial"


def test_s29_attach_workspace_preserves_payload():
    module = importlib.import_module("runtime_core.api.governed_runtime_workspace_continuity")
    updated = module.attach_runtime_workspace_continuity({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_runtime_workspace_continuity" in updated
    assert updated["governed_runtime_workspace_continuity"]["authority"]["runtime_authority"] == "blocked"


def test_s29_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_runtime_workspace_continuity.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_runtime_workspace_continuity.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S29" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
