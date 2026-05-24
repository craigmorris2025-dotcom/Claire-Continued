from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_dashboard_state_exposes_platform_first_mode_completion():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    modes = payload["intelligence_modes"]
    assert modes["platform_mode_completion_percent"] == 100
    assert modes["activation_mode_completion_percent"] == 100
    assert modes["live_execution_completion_percent"] == 100
    assert modes["operator_workflow_order"][0] == "finish_platform_and_dashboard_operator_surface"
    assert modes["operator_selectable_modes"]["connected"]["operator_surface_ready"] is True
    assert modes["operator_selectable_modes"]["hybrid"]["operator_surface_ready"] is True
    assert modes["operator_selectable_modes"]["connected"]["activation_ready"] is True
    assert modes["operator_selectable_modes"]["hybrid"]["activation_ready"] is True


def test_dashboard_mode_control_renders_three_operator_lanes():
    root = Path(__file__).resolve().parents[1]
    js = (root / "frontend" / "command_center" / "modern" / "platform_dashboard.js").read_text(encoding="utf-8")

    assert "renderModeCards" in js
    assert "Platform mode completion" in js
    assert "Activation mode completion" in js
    assert "Live execution readiness" in js
    assert "platform-first activation sequence" in js
