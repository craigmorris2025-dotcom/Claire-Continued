from pathlib import Path

from claire.continuous_runtime.cycle import (
    ensure_continuous_runtime_files,
    run_once,
)


def test_v19_87_4_4_legacy_files_seed_expected_surface(tmp_path):
    files = ensure_continuous_runtime_files(tmp_path)
    assert files["ok"] is True
    assert files["seeded"] is True
    for key in [
        "state_file",
        "cycle_file",
        "manifest_file",
        "review_candidates_file",
        "legacy_state_file",
        "legacy_cycle_file",
        "legacy_review_candidates_file",
    ]:
        assert Path(files[key]).exists()


def test_v19_87_4_4_run_once_accepts_legacy_positional_patterns(tmp_path):
    payload = run_once("governed discovery test", tmp_path)
    assert payload["runtime_truth_mutated"] is False
    assert payload["promotion_required"] is True
    assert payload["review_candidate_created"] is False
    assert payload["files_seeded"] is True
