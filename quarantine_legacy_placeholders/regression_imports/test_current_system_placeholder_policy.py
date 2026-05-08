from pathlib import Path


def _is_placeholder_stage_test(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "NotImplementedError" in text and "Import target class" in text


def test_no_active_import_target_class_placeholders():
    root = Path(__file__).resolve().parents[2]
    offenders = []

    for path in (root / "tests").rglob("test_*.py"):
        if "consistency" in path.parts:
            continue
        if _is_placeholder_stage_test(path):
            offenders.append(str(path.relative_to(root)))

    assert not offenders, (
        "Active unbound placeholder tests found. Run: "
        "python tools/pytest_current_system_guard.py --quarantine "
        "Offenders: " + ", ".join(offenders)
    )
