"""Claire v16.47 Runtime Command Contracts.

Defines a governed command schema and allow/block registry. This layer validates
command intent only; it does not execute commands.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
import json
from typing import Any, Dict, List, Literal

ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = ROOT / "data" / "runtime"
CONTRACT_PATH = RUNTIME_DIR / "runtime_command_contracts.json"

CommandScope = Literal["read", "scan", "regression", "maintenance", "install", "mutation"]

ALLOWED_COMMANDS = {
    "refresh_ui_shell": {"scope": "read", "requires_approval": False},
    "read_runtime_state": {"scope": "read", "requires_approval": False},
    "run_regression_check": {"scope": "regression", "requires_approval": False},
    "verify_install_manifest": {"scope": "install", "requires_approval": False},
    "prepare_rollback_plan": {"scope": "maintenance", "requires_approval": True},
}

BLOCKED_COMMANDS = {
    "delete_runtime_spine": "Protected runtime spine cannot be deleted.",
    "overwrite_master_control_state": "Master control state cannot be overwritten directly.",
    "disable_governance": "Governance cannot be disabled by command layer.",
    "unbounded_recursive_install": "Uncontrolled additive install is blocked.",
}

@dataclass
class RuntimeCommand:
    command: str
    requested_by: str = "system"
    payload: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True

@dataclass
class CommandValidationResult:
    accepted: bool
    command: str
    scope: str
    requires_approval: bool
    reason: str
    protected_runtime_spine: str = "preserved"


def validate_runtime_command(raw: Dict[str, Any]) -> CommandValidationResult:
    command = str(raw.get("command", "")).strip()
    if not command:
        return CommandValidationResult(False, command, "unknown", False, "missing_command")
    if command in BLOCKED_COMMANDS:
        return CommandValidationResult(False, command, "blocked", False, BLOCKED_COMMANDS[command])
    info = ALLOWED_COMMANDS.get(command)
    if not info:
        return CommandValidationResult(False, command, "unknown", False, "command_not_registered")
    return CommandValidationResult(True, command, info["scope"], bool(info["requires_approval"]), "command_allowed")


def write_command_contract_registry() -> Dict[str, Any]:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "v16.47",
        "layer": "runtime_command_contracts",
        "execution_allowed": False,
        "validation_only": True,
        "allowed_commands": ALLOWED_COMMANDS,
        "blocked_commands": BLOCKED_COMMANDS,
        "protected_runtime_spine": "preserved",
    }
    CONTRACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

if __name__ == "__main__":
    print(json.dumps(write_command_contract_registry(), indent=2))
