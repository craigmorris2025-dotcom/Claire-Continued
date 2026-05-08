from claire.runtime.master_control_action_log import append_master_control_action, read_action_log

def test_action_log_appends_without_mutation_flag():
    log = append_master_control_action({"command": "read_runtime_state", "status": "completed", "accepted": True})
    assert log["latest"]["command"] == "read_runtime_state"
    assert log["latest"]["mutation_performed"] is False
    assert log["latest"]["protected_runtime_spine"] == "preserved"
    assert isinstance(read_action_log()["actions"], list)
