from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36r6_audit_script_exists_and_has_no_live_network_execution():
    path = ROOT / "tools" / "audit_s36_route_visibility.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8").lower()
    forbidden = [
        "http.client",
        "requests.",
        "urllib.request",
        "selenium",
        "playwright",
        "webdriver",
        "run_governed_head_probe",
    ]
    for token in forbidden:
        assert token not in source


def test_s36r7_route_module_contract_still_safe():
    module = importlib.import_module("claire.api.routes.governed_live_probe")
    status = module.governed_live_probe_status()
    assert status["operator_triggered_only"] is True
    assert status["one_shot_only"] is True
    assert status["method_allowed"] == "HEAD"
    assert status["body_reads_allowed"] is False
    assert status["browser_execution_allowed"] is False
    assert status["runtime_truth_mutation_allowed"] is False
    assert status["autonomous_execution_allowed"] is False


def test_s36r8_route_visibility_audit_runs_with_project_bootstrap():
    result = subprocess.run(
        [sys.executable, "tools/audit_s36_route_visibility.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    report_path = ROOT / "runtime" / "governed_live_probe" / "s36_route_visibility_audit.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["found_status_route"] is True
    assert report["found_head_route"] is True
    assert report["body_reads_allowed"] is False
    assert report["browser_execution_allowed"] is False
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["autonomous_execution_allowed"] is False
    assert report["manual_promotion_required"] is True
    assert report["quarantine_required"] is True
