from __future__ import annotations

from pathlib import Path


def test_s1237_s1264_plateau_audit_integrates_reviewed_risk_patterns():
    from claire.audit.system_plateau_audit import run_audit

    report = run_audit(Path.cwd(), write_report=True)
    blockers = [issue for issue in report.get("issues", []) if issue.get("severity") == "blocker"]
    active_risk_warnings = [
        issue
        for issue in report.get("issues", [])
        if issue.get("code") == "active_source_risk_patterns"
    ]

    assert blockers == []
    assert active_risk_warnings == []
    assert report["summary"]["blocker_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["forward_motion_allowed"] is True
    assert report["static_risk_scan"]["finding_count"] >= 1
    assert report["static_risk_scan"]["unreviewed_finding_count"] == 0
    assert report["static_risk_scan"]["all_findings_reviewed"] is True


def test_s1237_s1264_risk_review_includes_self_and_routes_still_work():
    from claire.audit.risk_pattern_governance_review import reviewed_risk_files
    from claire.app import create_app
    from fastapi.testclient import TestClient

    files = reviewed_risk_files()
    assert "claire/audit/risk_pattern_governance_review.py" in files
    assert "claire/audit/system_plateau_audit.py" in files

    client = TestClient(create_app())
    response = client.get("/api/audit/risk-pattern-review")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "reviewed"
    assert payload["policy"]["audit_can_suppress_reviewed_static_warnings"] is True
    assert payload["blocked_authority"]["command_execution"] == "blocked"
