from claire.continuous_runtime.cycle import ensure_continuous_runtime_files, run_once


def test_v19_87_4_7_exact_legacy_status_file_and_success_status(tmp_path):
    ensure_continuous_runtime_files(tmp_path)
    assert (tmp_path / "data" / "continuous_runtime" / "status.json").exists()

    result = run_once(tmp_path, "Regional banks show credit risk and portfolio exposure pressure.")
    assert result["status"] == "success"
    assert result["loop_running"] is False
    assert result["review_candidate_created"] is True
