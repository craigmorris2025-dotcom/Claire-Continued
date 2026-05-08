from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/runtime/runtime_command_dispatcher.py", r"""
from __future__ import annotations

from typing import Any, Dict

from claire.runtime.runtime_command_contracts import RuntimeCommand, validate_runtime_command

def dispatch_runtime_command(command: RuntimeCommand) -> Dict[str, Any]:
    decision = validate_runtime_command(command)

    if not decision.allowed:
        return {"status": "blocked", "command": command.command, "reason": decision.reason}

    if command.command == "refresh_master_control_ui":
        from claire.ui.master_control_ui import build_master_control_ui_state
        return {"status": "ok", "command": command.command, "result": build_master_control_ui_state()}

    return {
        "status": "accepted",
        "command": command.command,
        "message": "Command accepted by dispatcher. Execution hook reserved for protected runtime spine.",
    }
""")

print("v16.48 runtime command dispatcher installed.")
