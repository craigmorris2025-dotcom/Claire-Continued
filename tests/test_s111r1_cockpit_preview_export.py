from __future__ import annotations

from pathlib import Path

from claire.api.governed_cockpit_preview_export_s111r1 import (
    export_cockpit_preview_artifact,
    validate_cockpit_preview_artifact,
    build_cockpit_preview_export_report,
)

def test_s111r1_exports_cockpit_preview_artifact(tmp_path: Path):
    export = export_cockpit_preview_artifact(export_dir=tmp_path)
    assert export["export_version"] == "S111R1"
    assert export["ok"] is True
    assert export["derived_artifact_only"] is True
    assert export["live_dashboard_rewire_performed"] is False
    assert export["app_patch_performed"] is False
    assert export["route_registration_performed"] is False
    assert Path(export["path"]).exists()

def test_s111r1_validates_exported_artifact(tmp_path: Path):
    export = export_cockpit_preview_artifact(export_dir=tmp_path)
    validation = validate_cockpit_preview_artifact(Path(export["path"]))
    assert validation["validation_version"] == "S111R1"
    assert validation["ok"] is True
    assert validation["checks"]["derived_artifact_only"] is True
    assert validation["checks"]["runtime_truth_write_blocked"] is True

def test_s111r1_export_report_passes(tmp_path: Path):
    report = build_cockpit_preview_export_report(export_dir=tmp_path)
    assert report["export_report_version"] == "S111R1"
    assert report["ok"] is True
    assert report["export"]["ok"] is True
    assert report["validation"]["ok"] is True
    assert report["next_safe_step"] == "S112R1 cockpit artifact validation and stop gate"
