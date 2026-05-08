from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/runtime/runtime_command_contracts.py", r"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

ALLOWED_COMMANDS = {
    "refresh_master_control_ui",
    "read_runtime_state",
    "read_intelligence_state",
    "run_regression_check",
}

BLOCKED_COMMANDS = {
    "delete_runtime_spine",
    "disable_governance",
    "overwrite_manifest",
    "uncontrolled_recursive_install",
}

@dataclass
class RuntimeCommand:
    command: str
    payload: Dict[str, Any] = field(default_factory=dict)
    requested_by: str = "system"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class RuntimeCommandDecision:
    allowed: bool
    command: str
    reason: str
    requires_rollback_link: bool = False

def validate_runtime_command(command: RuntimeCommand) -> RuntimeCommandDecision:
    if command.command in BLOCKED_COMMANDS:
        return RuntimeCommandDecision(False, command.command, "Command is explicitly blocked by governance.")
    if command.command not in ALLOWED_COMMANDS:
        return RuntimeCommandDecision(False, command.command, "Command is not in the allowed command registry.")
    return RuntimeCommandDecision(True, command.command, "Command allowed by runtime command contract.", True)
""")

print("v16.47 runtime command contracts installed.")
