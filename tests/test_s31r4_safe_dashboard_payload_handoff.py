from __future__ import annotations

from pathlib import Path
import py_compile


ROOT = Path(__file__).resolve().parents[1]


def test_s31r4_app_compiles():
    py_compile.compile(str(ROOT / "claire" / "app.py"), doraise=True)


def test_s31r4_app_contains_single_payload_handoff():
    text = (ROOT / "claire" / "app.py").read_text(encoding="utf-8")
    assert text.count("Claire v19.89.8-S31R4 governed dashboard payload handoff") == 1
    assert text.count("compose_governed_payload(payload)") == 1


def test_s31r4_reconciliation_module_exists():
    module_file = ROOT / "claire" / "api" / "governed_payload_reconciliation.py"
    assert module_file.exists()
    text = module_file.read_text(encoding="utf-8")
    assert "compose_governed_payload" in text
    assert "governed_operational_topology_continuity" in text


def test_s31r4_no_runtime_authority_expansion_strings():
    text = (ROOT / "claire" / "app.py").read_text(encoding="utf-8")
    forbidden = [
        "runtime_authority = 'enabled'",
        'runtime_authority = "enabled"',
        "autonomous_execution_expansion = True",
        "runtime_mutation_enabled = True",
    ]
    for token in forbidden:
        assert token not in text
