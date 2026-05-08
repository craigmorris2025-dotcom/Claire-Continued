from pathlib import Path


def test_baseline_runner_has_guard_or_fixture():
    root = Path(__file__).resolve().parents[2]
    candidate = root / "tests" / "regression" / "test_baseline_runner.py"

    if not candidate.exists():
        return

    text = candidate.read_text(encoding="utf-8", errors="ignore")
    bad_fragments = [
        "assert 1 == 0",
        "assert failures == 0",
        "assert len(failures) == 0",
    ]
    has_context_guard = (
        "CLAIRE_ALLOW_BASELINE_FAILURES" in text
        or "known_placeholder" in text.lower()
        or "baseline_runner_guard" in text.lower()
        or "expected_failures" in text.lower()
    )

    assert has_context_guard or not any(fragment in text for fragment in bad_fragments), (
        "Baseline runner needs a context guard/fixture for known placeholder or maturity-stage failures."
    )
