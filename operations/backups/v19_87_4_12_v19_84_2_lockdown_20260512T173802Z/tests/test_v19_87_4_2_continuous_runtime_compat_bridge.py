from claire.continuous_runtime.cycle import (
    ContinuousRuntimeCycle,
    ensure_continuous_runtime_cycle,
    run_continuous_runtime_cycle,
)


def test_v19_87_4_2_legacy_continuous_runtime_import_path_exists():
    cycle = ensure_continuous_runtime_cycle()
    assert isinstance(cycle, ContinuousRuntimeCycle)


def test_v19_87_4_2_legacy_continuous_runtime_bridge_is_fail_closed():
    payload = run_continuous_runtime_cycle({"input_summary": "compatibility bridge proof"})
    assert payload["runtime_truth_mutated"] is False
    assert payload["promotion_required"] is True
    assert payload["terminal_state"] in {"insufficient_data", "blocked", "max_iterations_reached"}
