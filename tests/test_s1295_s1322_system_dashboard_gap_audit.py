from __future__ import annotations

from pathlib import Path


def test_s1295_s1322_system_dashboard_gap_audit_runs_and_writes_reports():
    from claire.audit.system_dashboard_gap_audit import build_system_dashboard_gap_audit

    report = build_system_dashboard_gap_audit(Path.cwd(), write_report=True)

    assert report["audit_version"].startswith("v19.89.8-S1295-S1322")
    assert report["summary"]["backend_route_count"] > 0
    assert report["summary"]["required_capability_count"] >= 10
    assert "report_paths" in report
    assert Path(report["report_paths"]["json"]).exists()
    assert Path(report["report_paths"]["markdown"]).exists()


def test_s1295_s1322_gap_audit_uses_actual_create_app_routes_and_frontend_files():
    from claire.audit.system_dashboard_gap_audit import build_system_dashboard_gap_audit

    report = build_system_dashboard_gap_audit(Path.cwd(), write_report=False)
    paths = {route["path"] for route in report["backend"]["routes"]}

    assert "/dashboard/actions/registry" in paths
    assert "/dashboard/payload" in paths
    assert "/api/governed/live-probe/status" in paths

    frontend_files = {entry["file"] for entry in report["frontend"]["files"]}
    assert "frontend/command_center/modern/index.html" in frontend_files


def test_s1295_s1322_gap_audit_identifies_operation_capabilities():
    from claire.audit.system_dashboard_gap_audit import build_system_dashboard_gap_audit

    report = build_system_dashboard_gap_audit(Path.cwd(), write_report=False)
    keys = {capability["key"] for capability in report["capabilities"]}

    assert "operator_console" in keys
    assert "cockpit_operations" in keys
    assert "governed_search" in keys
    assert "evidence_review" in keys
    assert "runtime_spine_lifecycle" in keys
    assert "body_read_gates" in keys
