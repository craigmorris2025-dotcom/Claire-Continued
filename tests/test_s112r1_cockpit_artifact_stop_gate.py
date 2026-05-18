from __future__ import annotations

from pathlib import Path

from claire.api.governed_cockpit_stop_gate_s112r1 import (
    build_cockpit_artifact_stop_gate,
    write_cockpit_artifact_stop_gate_report,
)

def test_s112r1_cockpit_artifact_stop_gate_passes(tmp_path: Path):
    gate = build_cockpit_artifact_stop_gate(export_dir=tmp_path / "exports")
    assert gate["stop_gate_version"] == "S112R1"
    assert gate["ok"] is True
    assert gate["status"] == "cockpit_artifact_stop_gate_passed"
    assert gate["forward_motion_allowed"] is True
    assert gate["no_live_dashboard_rewire"] is True
    assert gate["no_app_patch"] is True
    assert gate["no_route_registration"] is True
    for value in gate["checks"].values():
        assert value is True

def test_s112r1_writes_stop_gate_report(tmp_path: Path):
    result = write_cockpit_artifact_stop_gate_report(
        report_dir=tmp_path / "reports",
        export_dir=tmp_path / "exports",
    )
    assert result["writer_version"] == "S112R1"
    assert result["ok"] is True
    assert result["forward_motion_allowed"] is True
    assert result["next_allowed_phase"] == "S113R1 controlled live cockpit integration plan"
    assert Path(result["path"]).exists()
