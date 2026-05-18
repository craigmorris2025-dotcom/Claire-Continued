from claire.continuous_runtime.cycle import run_once


def test_v19_87_4_8_continuous_runtime_status_legacy_key(tmp_path):
    result = run_once(tmp_path, "Regional banks show credit risk and portfolio exposure pressure.")
    assert result["status"] == "success"
    assert result["continuous_runtime_status"] == "configured_not_running"
    assert result["loop_running"] is False
