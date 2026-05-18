from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s38r1_fetch_script_exists_and_requires_approval():
    path = ROOT / "tools" / "s38_single_approved_source_fetch.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "--operator-ack" in source
    assert "--approval-id" in source
    assert "choices=[\"YES\"]" in source
    assert "s37_approved_source_fetch_plan.json" in source


def test_s38r2_fetch_script_is_bounded_and_quarantined():
    source = (ROOT / "tools" / "s38_single_approved_source_fetch.py").read_text(encoding="utf-8")
    assert "MAX_BYTES = 65536" in source
    assert "quarantine_path" in source
    assert "manual_promotion_required" in source
    assert "automatic_update_applied" in source
    assert "runtime_truth_mutation" in source


def test_s38r3_fetch_script_no_browser_or_autonomy():
    source = (ROOT / "tools" / "s38_single_approved_source_fetch.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "selenium",
        "playwright",
        "webdriver",
        "while true",
        "scheduler",
        "cron",
        "backgroundtask",
        "automatic_update_applied\": true",
        "runtime_truth_mutation\": true",
        "autonomous_execution\": true",
    ]
    for token in forbidden:
        assert token not in source


def test_s38r4_verify_script_exists_and_enforces_no_mutation():
    path = ROOT / "tools" / "s38_verify_quarantined_fetch_evidence.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "runtime_truth_mutation" in source
    assert "automatic_update_applied" in source
    assert "manual_promotion_required" in source
    assert "quarantined" in source
