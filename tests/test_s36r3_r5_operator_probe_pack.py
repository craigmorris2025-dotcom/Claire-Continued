from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36r3_operator_script_exists_and_is_one_shot_only():
    path = ROOT / "tools" / "run_s36_single_head_probe.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "operator_ack=True" in source
    assert "one_shot=True" in source
    assert "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE" in source
    assert "PLATFORM_ALLOW_HEAD_ONLY_PROBE" in source
    assert "PLATFORM_ALLOW_RESPONSE_BODY_READ" in source
    assert "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION" in source
    assert "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION" in source


def test_s36r3_operator_script_does_not_use_http_body_or_browser():
    path = ROOT / "tools" / "run_s36_single_head_probe.py"
    source = path.read_text(encoding="utf-8").lower()
    forbidden = ["selenium", "playwright", "webdriver", ".read()", "requests.get", "requests.post"]
    for token in forbidden:
        assert token not in source


def test_s36r4_quarantine_verifier_exists():
    path = ROOT / "tools" / "verify_s36_probe_quarantine.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "last_single_head_probe_manifest.json" in source
    assert "HEAD_METADATA_ONLY" in source
    assert "manual_promotion_required" in source
    assert "body_read" in source


def test_s36r5_no_runtime_authority_expansion_in_operator_pack():
    op = (ROOT / "tools" / "run_s36_single_head_probe.py").read_text(encoding="utf-8")
    verify = (ROOT / "tools" / "verify_s36_probe_quarantine.py").read_text(encoding="utf-8")
    combined = (op + "\n" + verify).lower()
    forbidden = [
        "while true",
        "schedule",
        "scheduler",
        "cron",
        "backgroundtask",
        "autonomous_execution = true",
        "runtime_truth_mutation = true",
        "body_read = true",
    ]
    for token in forbidden:
        assert token not in combined


def test_s36r5_operator_pack_python_syntax():
    for rel in [
        "tools/run_s36_single_head_probe.py",
        "tools/verify_s36_probe_quarantine.py",
    ]:
        source = (ROOT / rel).read_text(encoding="utf-8")
        ast.parse(source)
