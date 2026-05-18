from __future__ import annotations

from pathlib import Path


def test_s1209_s1236_risk_pattern_review_classifies_all_current_warning_files():
    from claire.audit.risk_pattern_governance_review import build_risk_pattern_review, reviewed_risk_files

    report = build_risk_pattern_review()
    files = reviewed_risk_files()

    assert report["status"] == "reviewed"
    assert report["blocker_count"] == 0
    assert report["forward_motion_allowed"] is True
    assert report["policy"]["no_autonomous_execution_added"] is True
    assert report["policy"]["no_body_read_added"] is True
    assert report["policy"]["no_runtime_mutation_added"] is True

    expected = {
        "claire/api/internet_controlled_live_probe_s394_s400.py",
        "claire/audit/system_plateau_audit.py",
        "claire/connectors/web_fetcher.py",
        "claire/desktop/startup_reliability.py",
        "claire/enterprise/dependency_governance_snapshot.py",
        "claire/governance/governed_web/controlled_head_transport_executor.py",
        "claire/install_safety/simple_manifest_installer.py",
        "claire/internet/governed_live_probe.py",
        "claire/package_update_governance/dependency_snapshot.py",
        "claire/package_update_governance/pip_audit_runner.py",
        "claire/platform/launch_hardening.py",
        "claire/platform/manifest.py",
        "claire/platform/resolver.py",
        "claire/real_governed_live_connectivity/http_client_adapter.py",
    }
    assert expected.issubset(files)


def test_s1209_s1236_risk_review_matches_plateau_warning_scope_without_blockers():
    from claire.audit.risk_pattern_governance_review import reviewed_risk_files
    from claire.audit.system_plateau_audit import run_audit

    audit = run_audit(Path.cwd(), write_report=True)
    blockers = [issue for issue in audit.get("issues", []) if issue.get("severity") == "blocker"]
    risk_warnings = [
        issue
        for issue in audit.get("issues", [])
        if issue.get("severity") == "warning" and issue.get("code") == "active_source_risk_patterns"
    ]

    assert blockers == []
    assert audit["summary"]["forward_motion_allowed"] is True

    if risk_warnings:
        warning_files = {entry["file"] for entry in risk_warnings[0].get("detail", [])}
        assert warning_files.issubset(reviewed_risk_files())


def test_s1209_s1236_risk_review_routes_mount_through_create_app():
    from claire.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    api = client.get("/api/audit/risk-pattern-review")
    dashboard = client.get("/dashboard/audit/risk-pattern-review")

    assert api.status_code == 200
    assert dashboard.status_code == 200
    payload = api.json()
    assert payload["status"] == "reviewed"
    assert payload["blocker_count"] == 0
    assert payload["blocked_authority"]["body_reads"] == "blocked"
