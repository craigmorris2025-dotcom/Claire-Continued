from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s25_operator_workflow_builds_review_queue_and_preserves_authority():
    module = importlib.import_module("runtime_core.api.governed_operator_workflow")
    payload = {
        "governed_evidence_basket": {"summary": {"evidence_total": 3}},
        "governed_search_session": {"session_controls": {"manual_review_required": True}},
    }

    workflow = module.build_governed_operator_workflow(payload)

    assert workflow["version"] == "v19.89.8-S25"
    assert workflow["status"] == "active"
    assert workflow["authority"]["runtime_authority"] == "blocked"
    assert workflow["authority"]["browser_execution_authority"] == "blocked"
    assert workflow["authority"]["autonomous_execution_expansion"] is False
    assert workflow["summary"]["operator_mutation_enabled"] is False
    assert workflow["summary"]["manual_review_required"] is True
    assert workflow["summary"]["workflow_total"] >= 2


def test_s25_operator_workflow_default_search_review_state():
    module = importlib.import_module("runtime_core.api.governed_operator_workflow")
    workflow = module.build_governed_operator_workflow({})

    assert workflow["items"][0]["workflow_id"] == "search_review"
    assert workflow["items"][0]["operator_action"] == "acknowledge_only"
    assert workflow["items"][0]["state"] == "manual_review_required"


def test_s25_attach_operator_workflow_preserves_payload():
    module = importlib.import_module("runtime_core.api.governed_operator_workflow")
    updated = module.attach_governed_operator_workflow({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_operator_workflow" in updated
    assert updated["governed_operator_workflow"]["authority"]["runtime_authority"] == "blocked"


def test_s25_frontend_assets_are_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_operator_workflow.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_operator_workflow.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S25" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js