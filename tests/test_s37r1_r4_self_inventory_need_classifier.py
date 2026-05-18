from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s37r1_inventory_script_exists_and_has_no_web_execution():
    path = ROOT / "tools" / "s37_system_self_inventory.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8").lower()
    forbidden = ["http.client", "requests.", "urllib.request", "selenium", "playwright", "webdriver"]
    for token in forbidden:
        assert token not in source


def test_s37r2_inventory_runs_and_writes_quarantine():
    result = subprocess.run([sys.executable, "tools/s37_system_self_inventory.py"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_system_self_inventory.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_system_inventory" / "s37_system_self_inventory_quarantine.json"
    assert report.exists()
    assert quarantine.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["live_web_execution"] is False
    assert data["runtime_truth_mutation_allowed"] is False
    assert data["autonomous_execution_allowed"] is False
    assert data["manual_promotion_required"] is True


def test_s37r3_need_classifier_runs_without_searching_web():
    result = subprocess.run([sys.executable, "tools/s37_web_need_classifier.py"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_web_need_classifier.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_system_inventory" / "s37_web_need_classifier_quarantine.json"
    assert report.exists()
    assert quarantine.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_search_executed"] is False
    assert data["live_web_execution"] is False
    assert data["automatic_updates_allowed"] is False
    assert data["runtime_truth_mutation_allowed"] is False
    assert data["manual_promotion_required"] is True


def test_s37r4_classifier_allows_research_only_as_quarantined_needs():
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_web_need_classifier.json"
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_need_count"] >= 1
    for need in data["needs"]:
        assert need.get("automatic_action_allowed") is not True
        assert need.get("manual_promotion_required") is True
