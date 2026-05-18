
from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient


BOM_TARGETS = [
    "claire/api/live_intelligence_status_routes.py",
    "claire/api/live_source_catalog_routes.py",
    "claire/feeds/source_catalogs/live_source_catalog.py",
    "claire/feeds/source_catalogs/source_health.py",
    "tools/active_module_registry.py",
    "tools/core_runtime_lock.py",
    "tools/live_runtime_dashboard.py",
    "tools/live_runtime_dashboard_state.py",
    "tools/runtime_manifest_system.py",
    "tools/runtime_state_engine.py",
    "tools/run_claire_baseline.py",
    "tools/unified_runtime_dashboard_builder.py",
]


def test_s1181_s1208_bom_targets_compile_without_nonprintable_header():
    for rel in BOM_TARGETS:
        path = Path(rel)
        assert path.exists(), rel
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), rel

        text = path.read_text(encoding="utf-8")
        assert not text.startswith("\ufeff"), rel
        compile(text, str(path), "exec")
        ast.parse(text)


def test_s1181_s1208_live_probe_status_unlock_allowed_false():
    from claire.app import create_app

    client = TestClient(create_app())
    response = client.get("/api/governed/live-probe/status")

    assert response.status_code == 200
    data = response.json()

    assert data["registered"] is True
    assert data["operator_triggered_only"] is True
    assert data["one_shot_only"] is True
    assert data["method_allowed"] == "HEAD"
    assert data["unlock_allowed"] is False
    assert data["execution_enabled"] is False
    assert data["network_request_performed"] is False
    assert data["body_read_allowed"] is False
    assert data["runtime_truth_mutation_allowed"] is False


def test_s1181_s1208_plateau_audit_blockers_cleared():
    from claire.audit.system_plateau_audit import run_audit

    report = run_audit(Path.cwd(), write_report=True)
    blocker_codes = {issue["code"] for issue in report.get("issues", []) if issue.get("severity") == "blocker"}

    assert "python_syntax_failures" not in blocker_codes
    assert "unlock_allowed_not_false" not in blocker_codes
    assert report["summary"]["blocker_count"] == 0
    assert report["summary"]["forward_motion_allowed"] is True
