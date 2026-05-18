from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s37r5_queue_script_exists_and_does_not_execute_web():
    path = ROOT / "tools" / "s37_build_governed_research_queue.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8").lower()
    forbidden = ["http.client", "requests.", "urllib.request", "selenium", "playwright", "webdriver"]
    for token in forbidden:
        assert token not in source


def test_s37r6_queue_builder_runs_after_classifier():
    subprocess.run([sys.executable, "tools/s37_system_self_inventory.py"], cwd=ROOT, check=True, text=True, capture_output=True, timeout=60)
    subprocess.run([sys.executable, "tools/s37_web_need_classifier.py"], cwd=ROOT, check=True, text=True, capture_output=True, timeout=60)

    result = subprocess.run([sys.executable, "tools/s37_build_governed_research_queue.py"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    report = ROOT / "runtime" / "governed_system_inventory" / "s37_governed_research_queue.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_system_inventory" / "s37_governed_research_queue_quarantine.json"
    assert report.exists()
    assert quarantine.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_search_executed"] is False
    assert data["live_web_execution"] is False
    assert data["runtime_truth_mutation_allowed"] is False
    assert data["manual_promotion_required"] is True
    assert data["queue_count"] >= 1


def test_s37r7_source_policy_gate_runs_without_web_search():
    result = subprocess.run([sys.executable, "tools/s37_source_policy_gate.py"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    report = ROOT / "runtime" / "governed_system_inventory" / "s37_source_policy_gate.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_system_inventory" / "s37_source_policy_gate_quarantine.json"
    assert report.exists()
    assert quarantine.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_search_executed"] is False
    assert data["live_web_execution"] is False
    assert data["automatic_updates_allowed"] is False
    assert data["manual_promotion_required"] is True


def test_s37r8_queue_entries_have_manual_promotion_and_no_auto_action():
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_governed_research_queue.json"
    data = json.loads(report.read_text(encoding="utf-8"))
    for item in data["queue"]:
        assert item["web_search_executed"] is False
        assert item["automatic_action_allowed"] is False
        assert item["runtime_truth_mutation_allowed"] is False
        assert item["manual_promotion_required"] is True
        assert item["quarantine_required"] is True
