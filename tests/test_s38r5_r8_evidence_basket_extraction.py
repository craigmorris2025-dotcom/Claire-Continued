from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s38r5_basket_script_exists_and_is_quarantine_only():
    path = ROOT / "tools" / "s38_build_quarantined_evidence_basket.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "s38_last_single_fetch_manifest.json" in source
    assert "s38_quarantined_evidence_basket.json" in source
    assert "manual_promotion_required" in source
    assert "runtime_truth_mutation" in source
    assert "automatic_update_applied" in source


def test_s38r6_extraction_script_exists_and_is_bounded_preview_only():
    path = ROOT / "tools" / "s38_extract_structured_knowledge.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "bounded_preview_only" in source
    assert "s38_structured_knowledge_extraction.json" in source
    assert "manual_promotion_required" in source


def test_s38r7_scripts_do_not_fetch_or_mutate():
    for rel in [
        "tools/s38_build_quarantined_evidence_basket.py",
        "tools/s38_extract_structured_knowledge.py",
    ]:
        source = (ROOT / rel).read_text(encoding="utf-8").lower()
        forbidden = [
            "urlopen",
            "http.client",
            "requests.get",
            "requests.post",
            "selenium",
            "playwright",
            "webdriver",
            "automatic_update_applied\": true",
            "runtime_truth_mutation\": true",
        ]
        for token in forbidden:
            assert token not in source


def test_s38r8_install_report_locks_no_auto_update():
    report = ROOT / "runtime" / "governed_web_fetch" / "s38r5_r8_install_report.json"
    assert report.exists()
    text = report.read_text(encoding="utf-8").lower()
    assert "automatic_updates_allowed" in text
    assert "false" in text
