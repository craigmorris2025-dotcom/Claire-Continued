from claire.continuous_runtime.cycle import (
    ensure_continuous_runtime_files,
    run_once,
)


def test_v19_87_4_3_legacy_api_names_exist_and_are_fail_closed():
    files = ensure_continuous_runtime_files()
    assert "runtime_dir" in files
    payload = run_once({"input_summary": "legacy api lockdown proof"})
    assert payload["runtime_truth_mutated"] is False
    assert payload["promotion_required"] is True
    assert payload["terminal_state"] in {"insufficient_data", "blocked", "max_iterations_reached"}
