from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s36r22_1_operator_script_has_project_root_bootstrap():
    path = ROOT / "tools" / "run_s36_single_head_probe.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "sys.path.insert(0, str(ROOT))" in source
    assert "Path(__file__).resolve().parents[1]" in source


def test_s36r22_1_operator_script_still_requires_ack_and_one_shot():
    source = (ROOT / "tools" / "run_s36_single_head_probe.py").read_text(encoding="utf-8")
    assert "--operator-ack" in source
    assert 'choices=["YES"]' in source
    assert "operator_ack=True" in source
    assert "one_shot=True" in source


def test_s36r22_1_operator_script_preserves_safety_gates():
    source = (ROOT / "tools" / "run_s36_single_head_probe.py").read_text(encoding="utf-8")
    assert 'PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE"] = "1"' in source
    assert 'PLATFORM_ALLOW_HEAD_ONLY_PROBE"] = "1"' in source
    assert "PLATFORM_ALLOW_RESPONSE_BODY_READ" in source
    assert "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION" in source
    assert "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION" in source


def test_s36r22_1_operator_script_no_browser_or_body_read():
    source = (ROOT / "tools" / "run_s36_single_head_probe.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "selenium",
        "playwright",
        "webdriver",
        "requests.get",
        "requests.post",
        ".read()",
        "while true",
        "scheduler",
        "cron",
    ]
    for token in forbidden:
        assert token not in source
