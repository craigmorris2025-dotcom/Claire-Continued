
from claire.runtime.runtime_command_contracts import RuntimeCommand, validate_runtime_command
from claire.runtime.runtime_command_dispatcher import dispatch_runtime_command

def test_allowed_command_passes_contract():
    decision = validate_runtime_command(RuntimeCommand(command="refresh_master_control_ui"))
    assert decision.allowed is True

def test_unknown_command_is_blocked():
    decision = validate_runtime_command(RuntimeCommand(command="random_uncontrolled_command"))
    assert decision.allowed is False

def test_explicitly_blocked_command_is_blocked():
    decision = validate_runtime_command(RuntimeCommand(command="disable_governance"))
    assert decision.allowed is False

def test_dispatcher_blocks_unsafe_command():
    result = dispatch_runtime_command(RuntimeCommand(command="uncontrolled_recursive_install"))
    assert result["status"] == "blocked"
