from claire.continuous_runtime.cycle import ensure_continuous_runtime_files, run_once


def test_v19_87_4_11_exact_remaining_legacy_contract(tmp_path):
    ensure_continuous_runtime_files(tmp_path)
    assert (tmp_path / "data" / "continuous_runtime" / "status.json").exists()
    assert (tmp_path / "data" / "continuous_runtime" / "review_queue.json").exists()

    result = run_once(tmp_path, "Regional banks show credit risk and portfolio exposure pressure.")
    assert result["status"] == "success"
    assert result["continuous_runtime_status"] == "configured_not_running"
    assert result["operator_approval_required"] is True
    assert result["loop_running"] is False
