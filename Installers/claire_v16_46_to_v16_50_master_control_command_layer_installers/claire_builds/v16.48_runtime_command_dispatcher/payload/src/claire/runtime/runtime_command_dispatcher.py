"""Claire v16.48 Runtime Command Dispatcher.

Controlled dispatcher for safe read/regression/install-verification commands.
Mutation commands remain blocked unless future governance explicitly authorizes them.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict

from claire.runtime.runtime_command_contracts import validate_runtime_command
from claire.ui.master_control_ui_shell import build_master_control_ui_shell

ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = ROOT / "data" / "runtime"
DISPATCH_PATH = RUNTIME_DIR / "runtime_command_dispatcher.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "unreadable", "path": str(path), "error": str(exc)}


def dispatch_runtime_command(raw: Dict[str, Any]) -> Dict[str, Any]:
    validation = validate_runtime_command(raw)
    base = {
        "version": "v16.48",
        "layer": "runtime_command_dispatcher",
        "command": validation.command,
        "accepted": validation.accepted,
        "scope": validation.scope,
        "requires_approval": validation.requires_approval,
        "reason": validation.reason,
        "protected_runtime_spine": "preserved",
        "mutation_performed": False,
    }
    if not validation.accepted:
        result = {**base, "status": "rejected", "result": None}
    elif validation.requires_approval and not raw.get("approved", False):
        result = {**base, "status": "approval_required", "result": None}
    elif validation.command == "refresh_ui_shell":
        result = {**base, "status": "completed", "result": build_master_control_ui_shell()}
    elif validation.command == "read_runtime_state":
        result = {**base, "status": "completed", "result": _read_json(RUNTIME_DIR / "runtime_state.json")}
    elif validation.command == "run_regression_check":
        result = {**base, "status": "prepared", "result": {"instruction": "Run pytest tests/regression from project root."}}
    elif validation.command == "verify_install_manifest":
        result = {**base, "status": "completed", "result": _read_json(RUNTIME_DIR / "runtime_manifest.json")}
    elif validation.command == "prepare_rollback_plan":
        result = {**base, "status": "completed", "result": {"rollback_plan": "Use latest install backup created by installer script."}}
    else:
        result = {**base, "status": "unhandled", "result": None}
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    DISPATCH_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    print(json.dumps(dispatch_runtime_command({"command": "refresh_ui_shell"}), indent=2))
