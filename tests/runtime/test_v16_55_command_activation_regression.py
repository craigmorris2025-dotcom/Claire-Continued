
import json
from pathlib import Path

from claire.runtime.command_execution_guard import guard_runtime_command
from claire.runtime.governed_command_dispatcher import dispatch_governed_runtime_command
from claire.runtime.runtime_command_contracts import RuntimeCommand
from claire.runtime.runtime_command_dashboard import build_runtime_command_dashboard


def test_execution_guard_allows_safe_command():
    result = guard_runtime_command(RuntimeCommand(command="read_runtime_state"))
    assert result.allowed is True


def test_execution_guard_blocks_high_risk_payload():
    result = guard_runtime_command(
        RuntimeCommand(command="read_runtime_state", payload={"action": "disable governance"})
    )
    assert result.allowed is False


def test_governed_dispatcher_writes_blocked_result():
    result = dispatch_governed_runtime_command(
        RuntimeCommand(command="uncontrolled_recursive_install")
    )
    assert result["status"] == "blocked"
    assert Path("data/runtime/runtime_command_results.json").exists()


def test_command_dashboard_builds():
    dashboard = build_runtime_command_dashboard()
    assert dashboard["status"] == "ready"
    assert Path("data/runtime/runtime_command_dashboard.json").exists()
