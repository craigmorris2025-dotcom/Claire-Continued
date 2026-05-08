from claire.ui.master_control_ui_shell import build_master_control_ui_shell

def test_master_control_ui_shell_is_read_only():
    payload = build_master_control_ui_shell()
    assert payload["version"] == "v16.46"
    assert payload["mode"] == "read_only"
    assert payload["mutation_allowed"] is False
    assert payload["protected_runtime_spine"] == "preserved"
    assert isinstance(payload["sources"], list)
