from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s22_evidence_basket_builds_and_preserves_authority():
    module = importlib.import_module("claire.api.governed_evidence_basket")
    payload = {
        "event_stream": {"events": [{"id": "e1", "type": "runtime_state_transition"}]},
        "governed_runtime_timeline": {
            "events": [{"id": "t1", "type": "heartbeat", "classification": "heartbeat", "severity": "info"}]
        },
    }

    basket = module.build_evidence_basket(payload)

    assert basket["version"] == "v19.89.8-S22"
    assert basket["status"] == "active"
    assert basket["authority"]["runtime_authority"] == "blocked"
    assert basket["authority"]["cockpit_presentation_only"] is True
    assert basket["authority"]["evidence_promotion"] == "manual_review_required"
    assert basket["authority"]["autonomous_execution_expansion"] is False
    assert basket["summary"]["manual_review_required"] is True
    assert basket["summary"]["automatic_truth_mutation"] is False
    assert basket["summary"]["evidence_total"] == 2


def test_s22_attach_evidence_basket_preserves_payload():
    module = importlib.import_module("claire.api.governed_evidence_basket")
    updated = module.attach_evidence_basket({"existing": "preserved"})

    assert updated["existing"] == "preserved"
    assert "governed_evidence_basket" in updated
    assert updated["governed_evidence_basket"]["authority"]["runtime_authority"] == "blocked"


def test_s22_frontend_assets_are_review_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_evidence_basket.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_evidence_basket.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S22" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "manual review required" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js
