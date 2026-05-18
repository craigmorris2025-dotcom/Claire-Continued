from pathlib import Path

from claire.continuous_runtime.cycle import ensure_continuous_runtime_files, run_once


def test_v19_87_4_5_legacy_files_are_broadly_seeded(tmp_path):
    files = ensure_continuous_runtime_files(tmp_path)
    assert files["completed"] == "success"
    assert files["loop_running"] is False
    for key in [
        "state_file",
        "cycle_file",
        "manifest_file",
        "review_candidates_file",
        "data_state_file",
        "data_cycle_file",
        "root_runtime_state_file",
        "root_runtime_cycle_file",
        "legacy_state_file",
        "legacy_cycle_file",
        "legacy_review_candidates_file",
    ]:
        assert Path(files[key]).exists()


def test_v19_87_4_5_run_once_returns_legacy_success_shape(tmp_path):
    result = run_once("legacy governed cycle", tmp_path)
    assert result["completed"] == "success"
    assert result["review_candidate_created"] is True
    assert result["loop_running"] is False
    assert result["runtime_truth_mutated"] is False
