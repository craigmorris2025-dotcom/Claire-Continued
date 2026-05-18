from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s28_orchestration_builds_review_state_and_preserves_authority():
    module = importlib.import_module("claire.api.governed_operational_session_orchestration")
    payload = {
        "multi_panel_runtime_cohesion": {
            "cohesion_state": "cohesive",
            "summary": {"missing_total": 0, "drift_total": 0, "payload_propagation": "complete"},
        },
        "canonical_browser_session_persistence": {
            "session_snapshot": {"selected_route": "portfolio", "evidence_total": 3},
        },
        "governed_operator_workflow": {
            "summary": {"workflow_total": 2, "manual_review_required": True},
        },
        "runtime_continuity_visualization": {
            "continuity_state": "continuous",
            "summary": {"selected_route": "portfolio"},
        },
        "governed_evidence_basket": {
            "summary": {"evidence_total": 3},
        },
        "continuous_browser_runtime_loop": {
            "loop_state": "continuous_observation",
            "summary": {"payload_freshness": "fresh"},
        },
    }

    orchestration = module.build_operational_session_orchestration(payload)

    assert orchestration["version"] == "v19.89.8-S28"
    assert orchestration["status"] == "active"
    assert orchestration["session_state"] == "review_required"
    assert orchestration["authority"]["runtime_authority"] == "blocked"
    assert orchestration["authority"]["browser_execution_authority"] == "blocked"
    assert orchestration["authority"]["operator_mutation_enabled"] is False
    assert orchestration["authority"]["runtime_mutation_enabled"] is False
    assert orchestration["authority"]["autonomous_execution_expansion"] is False
    assert orchestration["summary"]["selected_route"] == "portfolio"
    assert len(orchestration["session_bindings"]) == 5


def test_s28_orchestration_blocks_on_authority_drift():
    module = importlib.import_module("claire.api.governed_operational_session_orchestration")
    orchestration = module.build_operational_session_orchestration({
        "multi_panel_runtime_cohesion": {
            "summary": {"missing_total": 0, "drift_total": 1}
        }
    })

    assert orchestration["session_state"] == "blocked"


def test_s28_orchestration_partial_on_missing_panels():
    module = importlib.import_module("claire.api.governed_operational_session_orchestration")
    orchestration = module.build_operational_session_orchestration({
        "multi_panel_runtime_cohesion": {
            "summary": {"missing_total": 2, "drift_total": 0}
        }
    })

    assert orchestration["session_state"] == "partial"


def test_s28_attach_orchestration_preserves_payload():
    module = importlib.import_module("claire.api.governed_operational_session_orchestration")
    updated = module.attach_operational_session_orchestration({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_operational_session_orchestration" in updated
    assert updated["governed_operational_session_orchestration"]["authority"]["runtime_authority"] == "blocked"


def test_s28_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_operational_session_orchestration.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_operational_session_orchestration.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S28" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
