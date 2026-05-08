from claire.runtime.command_layer_regression_lock import build_command_layer_regression_lock

def test_command_layer_regression_lock_passes():
    payload = build_command_layer_regression_lock()
    assert payload["version"] == "v16.50"
    assert payload["status"] == "passed"
    assert payload["protected_runtime_spine"] == "preserved"
    assert payload["uncontrolled_additive_installs"] is False
