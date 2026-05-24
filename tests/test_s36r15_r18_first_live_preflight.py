from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _calls_and_imports(source: str) -> tuple[set[str], set[str]]:
    tree = ast.parse(source)
    imports = set()
    calls = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                parts = [fn.attr]
                value = fn.value
                while isinstance(value, ast.Attribute):
                    parts.append(value.attr)
                    value = value.value
                if isinstance(value, ast.Name):
                    parts.append(value.id)
                calls.add(".".join(reversed(parts)))

    return calls, imports


def test_s36r15_preflight_script_exists_and_is_static_safe():
    path = ROOT / "tools" / "s36_first_live_preflight.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    calls, imports = _calls_and_imports(source)

    forbidden_imports = {"http.client", "requests", "urllib.request", "selenium", "playwright", "webdriver"}
    assert imports.isdisjoint(forbidden_imports)

    forbidden_calls = {
        "requests.get",
        "requests.post",
        "run_governed_head_probe",
        "webdriver",
    }
    assert calls.isdisjoint(forbidden_calls)


def test_s36r16_command_file_exists_and_contains_only_manual_commands():
    path = ROOT / "runtime" / "governed_live_probe" / "S36_FIRST_LIVE_OPERATOR_COMMANDS.txt"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "python tools/run_s36_single_head_probe.py --url https://example.com --operator-ack YES" in text
    assert "python tools/verify_s36_probe_quarantine.py" in text
    assert "python tools/compile_s36_first_probe_report.py" in text
    assert "NO automatic execution" in text
    assert "HEAD-only" in text


def test_s36r17_router_no_body_read_static_proof():
    router = ROOT / "runtime_core" / "api" / "routes" / "governed_live_probe.py"
    source = router.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            assert not (isinstance(fn, ast.Attribute) and fn.attr == "read")


def test_s36r18_first_live_preflight_runs_without_live_probe():
    result = subprocess.run(
        [sys.executable, "tools/s36_first_live_preflight.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    report_path = ROOT / "runtime" / "governed_live_probe" / "s36_first_live_preflight_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["live_probe_executed_by_preflight"] is False
    assert report["ready_for_one_operator_head_probe"] is True
    assert report["invariants"]["body_reads_allowed"] is False
    assert report["invariants"]["runtime_truth_mutation_allowed"] is False
    assert report["invariants"]["autonomous_execution_allowed"] is False
