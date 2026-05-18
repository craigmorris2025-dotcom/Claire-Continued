from __future__ import annotations

from pathlib import Path


def test_s1153_s1180_plateau_audit_runs_and_writes_report():
    from claire.audit.system_plateau_audit import run_audit

    report = run_audit(Path.cwd(), write_report=True)

    assert report["audit_version"].startswith("v19.89.8-S1153-S1180")
    assert "summary" in report
    assert "blocker_count" in report["summary"]
    assert "warning_count" in report["summary"]
    assert "forward_motion_allowed" in report["summary"]
    assert "report_paths" in report

    json_path = Path(report["report_paths"]["json"])
    md_path = Path(report["report_paths"]["markdown"])

    assert json_path.exists()
    assert md_path.exists()


def test_s1153_s1180_plateau_audit_checks_core_dashboard_routes():
    from claire.audit.system_plateau_audit import EXPECTED_GET_ROUTES, run_audit

    report = run_audit(Path.cwd(), write_report=False)
    expected = set(EXPECTED_GET_ROUTES)

    assert "/dashboard/actions/registry" in expected
    assert "/dashboard/operator-console/contract" in expected
    assert "/dashboard/operator-action/result/plan_search" in expected
    assert "/dashboard/visibility/summary" in expected
    assert "/dashboard/status/harmonized" in expected

    routes = report.get("routes", {}).get("expected_get", {})
    for path in expected:
        assert path in routes
