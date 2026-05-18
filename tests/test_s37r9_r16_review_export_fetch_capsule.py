from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_base_queue():
    subprocess.run([sys.executable, "tools/s37_system_self_inventory.py"], cwd=ROOT, check=True, text=True, capture_output=True, timeout=60)
    subprocess.run([sys.executable, "tools/s37_web_need_classifier.py"], cwd=ROOT, check=True, text=True, capture_output=True, timeout=60)
    subprocess.run([sys.executable, "tools/s37_build_governed_research_queue.py"], cwd=ROOT, check=True, text=True, capture_output=True, timeout=60)


def _seed_manual_approval():
    subprocess.run(
        [
            sys.executable,
            "tools/s37_create_manual_research_approval.py",
            "--queue-id",
            "S37-WEB-NEED-001",
            "--candidate-url",
            "https://docs.python.org",
            "--operator-ack",
            "YES",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        timeout=60,
    )


def test_s37r9_review_export_runs_without_web():
    _run_base_queue()
    result = subprocess.run([sys.executable, "tools/s37_export_research_queue_review.py"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_research_queue_operator_review.json"
    md = ROOT / "runtime" / "governed_system_inventory" / "S37_RESEARCH_QUEUE_OPERATOR_REVIEW.md"
    assert report.exists()
    assert md.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_search_executed"] is False
    assert data["automatic_action_allowed"] is False
    assert data["manual_promotion_required"] is True


def test_s37r10_manual_approval_creates_quarantined_record():
    _run_base_queue()
    result = subprocess.run(
        [
            sys.executable,
            "tools/s37_create_manual_research_approval.py",
            "--queue-id",
            "S37-WEB-NEED-001",
            "--candidate-url",
            "https://docs.python.org",
            "--operator-ack",
            "YES",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    report = ROOT / "runtime" / "governed_system_inventory" / "s37_manual_research_approvals.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_system_inventory" / "s37_manual_research_approvals_quarantine.json"
    assert report.exists()
    assert quarantine.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["web_fetch_executed"] is False
    assert data["runtime_truth_mutation_allowed"] is False


def test_s37r11_fetch_capsule_prepares_plan_without_fetching():
    _run_base_queue()
    _seed_manual_approval()

    result = subprocess.run(
        [
            sys.executable,
            "tools/s37_approved_source_fetch_capsule.py",
            "--approval-id",
            "S37-WEB-NEED-001-APPROVED",
            "--operator-ack",
            "YES",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    plan = ROOT / "runtime" / "governed_system_inventory" / "s37_approved_source_fetch_plan.json"
    quarantine = ROOT / "data" / "quarantine" / "governed_web_evidence" / "s37_approved_source_fetch_plan_quarantine.json"
    assert plan.exists()
    assert quarantine.exists()
    data = json.loads(plan.read_text(encoding="utf-8"))
    assert data["ready_for_s38_single_fetch"] is True
    assert data["web_fetch_executed"] is False
    assert data["response_body_read"] is False
    assert data["runtime_truth_mutation_allowed"] is False


def test_s37r12_r16_scripts_do_not_contain_fetch_execution():
    for rel in [
        "tools/s37_export_research_queue_review.py",
        "tools/s37_create_manual_research_approval.py",
        "tools/s37_approved_source_fetch_capsule.py",
    ]:
        source = (ROOT / rel).read_text(encoding="utf-8").lower()
        forbidden = ["http.client", "requests.get", "requests.post", "urllib.request.urlopen", "selenium", "playwright", "webdriver"]
        for token in forbidden:
            assert token not in source
