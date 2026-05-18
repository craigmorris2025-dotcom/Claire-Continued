from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36r12_operator_script_still_requires_explicit_ack():
    path = ROOT / "tools" / "run_s36_single_head_probe.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "--operator-ack" in source
    assert 'choices=["YES"]' in source
    assert "operator_ack=True" in source
    assert "one_shot=True" in source


def test_s36r13_quarantine_verifier_schema_lock():
    path = ROOT / "tools" / "verify_s36_probe_quarantine.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    for token in [
        "HEAD_METADATA_ONLY",
        "body_read",
        "browser_execution",
        "runtime_truth_mutation",
        "autonomous_execution",
        "manual_promotion_required",
        "quarantined",
        "metadata",
        "headers",
        "status",
    ]:
        assert token in source


def test_s36r14_first_probe_report_compiler_exists_and_is_safe():
    path = ROOT / "tools" / "compile_s36_first_probe_report.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    lower = source.lower()
    forbidden = [
        "http.client",
        "requests.",
        "urllib.request",
        "selenium",
        "playwright",
        "webdriver",
        "run_governed_head_probe",
        "runtime_truth_mutated = true",
        "automatic_update_applied = true",
    ]
    for token in forbidden:
        assert token not in lower


def test_s36r14_report_compiler_enforces_quarantine_only():
    source = (ROOT / "tools" / "compile_s36_first_probe_report.py").read_text(encoding="utf-8")
    assert "last_single_head_probe_manifest.json" in source
    assert "s36_first_probe_operator_report.json" in source
    assert "manual_promotion_required" in source
    assert "runtime_truth_mutated" in source
    assert "automatic_update_applied" in source
    assert "continuous_crawl_started" in source
