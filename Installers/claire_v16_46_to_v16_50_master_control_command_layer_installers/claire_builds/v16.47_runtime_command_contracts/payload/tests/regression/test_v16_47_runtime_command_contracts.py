from claire.runtime.runtime_command_contracts import validate_runtime_command, write_command_contract_registry

def test_allowed_command_contract():
    result = validate_runtime_command({"command": "read_runtime_state"})
    assert result.accepted is True
    assert result.scope == "read"

def test_blocked_command_contract():
    result = validate_runtime_command({"command": "disable_governance"})
    assert result.accepted is False
    assert result.scope == "blocked"

def test_contract_registry_writes_validation_only():
    registry = write_command_contract_registry()
    assert registry["validation_only"] is True
    assert registry["execution_allowed"] is False
