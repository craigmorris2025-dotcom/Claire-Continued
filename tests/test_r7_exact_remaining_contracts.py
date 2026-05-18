
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_r7_exact_remaining_contracts():
    from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry
    from claire.app import create_app

    labels = {action["label"] for action in build_dashboard_actions_registry()["actions"]}
    assert "Plan a governed search" in labels or "Compile search plan" in labels

    app_text = Path("claire/app.py").read_text(encoding="utf-8")
    assert app_text.count("Claire v19.89.8-S31R4 governed dashboard payload handoff") == 1
    assert app_text.count("compose_governed_payload(payload)") == 1

    client = TestClient(create_app())
    status = client.get("/api/governed/live-probe/status")
    assert status.status_code == 200
    data = status.json()
    assert data["registered"] is True
    assert data["operator_triggered_only"] is True
    assert data["network_request_performed"] is False
    assert data["body_read_allowed"] is False
    assert data["runtime_truth_mutation_allowed"] is False
