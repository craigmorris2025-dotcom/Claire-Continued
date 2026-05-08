
from __future__ import annotations

from typing import Any, Dict

from claire.runtime.command_execution_guard import guard_runtime_command
from claire.runtime.governed_command_result_writer import write_governed_command_result
from claire.runtime.master_control_action_log import append_master_control_action
from claire.runtime.runtime_command_contracts import RuntimeCommand
from claire.runtime.runtime_command_dispatcher import dispatch_runtime_command


def dispatch_governed_runtime_command(command: RuntimeCommand) -> Dict[str, Any]:
    guard = guard_runtime_command(command)

    if not guard.allowed:
        result = {
            "status": "blocked",
            "command": command.command,
            "reason": guard.reason,
            "contract_reason": guard.contract_reason,
            "stage": "execution_guard",
        }
        write_governed_command_result(result)
        append_master_control_action(result)
        return result

    result = dispatch_runtime_command(command)
    result["stage"] = "governed_dispatcher"
    result["guard_reason"] = guard.reason

    write_governed_command_result(result)
    append_master_control_action(result)
    return result
