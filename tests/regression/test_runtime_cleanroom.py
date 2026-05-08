from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_placeholder_tests_are_quarantined():
    offenders = []
    marker = "raise " + "NotImplementedError" + '("Import target class")'

    for path in (ROOT / "tests").rglob("test_*.py"):
        rel = str(path.relative_to(ROOT))

        if "placeholder_disabled" in rel:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        if marker in text:
            offenders.append(rel)

    assert offenders == []


def test_pytest_runtime_ini_exists():
    assert (ROOT / "pytest_runtime.ini").exists()


def test_runtime_compile_tool_exists():
    assert (ROOT / "tools" / "runtime_compile_check.py").exists()
