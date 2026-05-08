from pathlib import Path


PLACEHOLDER_PATTERNS = [
    "NotImplementedError",
    "Import target class",
]


def test_no_active_placeholder_import_target_class_tests():
    root = Path(__file__).resolve().parents[2]
    test_files = [p for p in (root / "tests").rglob("test_*.py") if "consistency" not in p.parts]

    offenders = []
    for path in test_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if all(pattern in text for pattern in PLACEHOLDER_PATTERNS):
            offenders.append(str(path.relative_to(root)))

    assert not offenders, "Active placeholder stage tests found: " + ", ".join(offenders)
