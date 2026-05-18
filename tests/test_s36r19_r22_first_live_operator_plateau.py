from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36r19_plateau_runner_exists_and_requires_operator_ack():
    path = ROOT / "tools" / "run_s36_first_live_operator_plateau.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "--operator-ack" in source
    assert 'choices=["YES"]' in source
    assert "tools/run_s36_single_head_probe.py" in source


def test_s36r20_plateau_runner_has_exact_required_sequence():
    source = (ROOT / "tools" / "run_s36_first_live_operator_plateau.py").read_text(encoding="utf-8")
    assert "tools/s36_first_live_preflight.py" in source
    assert "tools/run_s36_single_head_probe.py" in source
    assert "tools/verify_s36_probe_quarantine.py" in source
    assert "tools/compile_s36_first_probe_report.py" in source


def test_s36r21_plateau_runner_no_loop_or_autonomy():
    source = (ROOT / "tools" / "run_s36_first_live_operator_plateau.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "while true",
        "schedule",
        "scheduler",
        "cron",
        "backgroundtask",
        "autonomous_execution_allowed\": true",
        "runtime_truth_mutation_allowed\": true",
        "body_reads_allowed\": true",
        "automatic_update_applied\": true",
    ]
    for token in forbidden:
        assert token not in source


def test_s36r22_plateau_install_report_exists():
    report = ROOT / "runtime" / "governed_live_probe" / "s36r19_r22_first_live_operator_plateau_install.json"
    assert report.exists()
    text = report.read_text(encoding="utf-8").lower()
    assert "live_network_execution_during_install" in text
    assert "false" in text
