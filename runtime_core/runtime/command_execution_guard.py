
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from runtime_core.runtime.runtime_command_contracts import RuntimeCommand, validate_runtime_command


HIGH_RISK_KEYS = {
    "delete",
    "remove",
    "overwrite",
    "disable",
    "bypass",
    "unguarded",
    "uncontrolled",
}


@dataclass
class CommandGuardResult:
    allowed: bool
    command: str
    reason: str
    contract_reason: str | None = None


def guard_runtime_command(command: RuntimeCommand) -> CommandGuardResult:
    contract = validate_runtime_command(command)

    if not contract.allowed:
        return CommandGuardResult(
            allowed=False,
            command=command.command,
            reason="Blocked by runtime command contract.",
            contract_reason=contract.reason,
        )

    payload_text = str(command.payload).lower()
    for key in HIGH_RISK_KEYS:
        if key in payload_text:
            return CommandGuardResult(
                allowed=False,
                command=command.command,
                reason=f"Blocked by execution guard because payload contains high-risk term: {key}",
                contract_reason=contract.reason,
            )

    return CommandGuardResult(
        allowed=True,
        command=command.command,
        reason="Command passed execution guard.",
        contract_reason=contract.reason,
    )
