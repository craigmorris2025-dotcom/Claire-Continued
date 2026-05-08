from claire.runtime.runtime_command_dispatcher import dispatch_runtime_command

def test_dispatcher_rejects_unknown_command():
    result = dispatch_runtime_command({"command": "unknown_command"})
    assert result["status"] == "rejected"
    assert result["mutation_performed"] is False

def test_dispatcher_can_refresh_read_only_ui_shell():
    result = dispatch_runtime_command({"command": "refresh_ui_shell"})
    assert result["status"] == "completed"
    assert result["mutation_performed"] is False
    assert result["result"]["mode"] == "read_only"
