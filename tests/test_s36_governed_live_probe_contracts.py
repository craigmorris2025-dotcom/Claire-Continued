from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36_router_module_imports_and_exposes_contract():
    module = importlib.import_module("runtime_core.api.routes.governed_live_probe")
    status = module.governed_live_probe_status()
    assert status["registered"] is True
    assert status["method_allowed"] == "HEAD"
    assert status["body_reads_allowed"] is False
    assert status["browser_execution_allowed"] is False
    assert status["runtime_truth_mutation_allowed"] is False
    assert status["autonomous_execution_allowed"] is False


def test_s36_router_does_not_read_response_body():
    source = (ROOT / "runtime_core" / "api" / "routes" / "governed_live_probe.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "read":
                forbidden.append(fn.attr)
    assert forbidden == []


def test_s36_app_py_was_not_touched_by_this_installer():
    # app.py may contain historical governed_live_probe references from earlier Claire builds.
    # The S36 invariant is not "string absent"; it is "this installer did not touch app.py".
    report_path = ROOT / "runtime" / "governed_live_probe" / "s36_r1d_router_only_exclude_bridge_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["safety"]["app_py_patched"] is False
    assert report["app_py_touched"] is False
    changed_files = "\n".join(report.get("changed_files", []))
    assert "claire\\app.py" not in changed_files
    assert "claire/app.py" not in changed_files


def test_s36_payload_bridge_was_not_touched_by_router_only_installer():
    report_path = ROOT / "runtime" / "governed_live_probe" / "s36_r1d_router_only_exclude_bridge_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["payload_bridge_touched"] is False
    assert report["safety"]["payload_bridge_patched"] is False


def test_s36_registration_report_exists_and_is_router_only():
    report_path = ROOT / "runtime" / "governed_live_probe" / "s36_r1d_router_only_exclude_bridge_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["registration_strategy"] == "router_only_excluding_dashboard_payload_bridge"
    assert report["safety"]["body_reads_allowed"] is False
    assert report["safety"]["browser_execution_allowed"] is False
    assert report["safety"]["runtime_truth_mutation_allowed"] is False
    assert report["safety"]["autonomous_execution_allowed"] is False
    assert report["safety"]["manual_promotion_required"] is True
    assert report["safety"]["quarantine_required"] is True
