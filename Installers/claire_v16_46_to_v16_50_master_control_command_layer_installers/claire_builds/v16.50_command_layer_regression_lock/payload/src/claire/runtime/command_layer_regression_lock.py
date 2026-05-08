"""Claire v16.50 Command Layer Regression Lock.

Aggregates command layer safety checks into a single proof artifact.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict

from claire.runtime.runtime_command_contracts import validate_runtime_command, write_command_contract_registry
from claire.runtime.runtime_command_dispatcher import dispatch_runtime_command
from claire.runtime.master_control_action_log import append_master_control_action

ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = ROOT / "data" / "runtime"
LOCK_PATH = RUNTIME_DIR / "command_layer_regression_lock.json"


def build_command_layer_regression_lock() -> Dict[str, Any]:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    registry = write_command_contract_registry()
    blocked = validate_runtime_command({"command": "disable_governance"})
    allowed = validate_runtime_command({"command": "read_runtime_state"})
    dispatch = dispatch_runtime_command({"command": "refresh_ui_shell"})
    action_log = append_master_control_action(dispatch)
    passed = (
        registry.get("validation_only") is True
        and blocked.accepted is False
        and allowed.accepted is True
        and dispatch.get("mutation_performed") is False
        and dispatch.get("protected_runtime_spine") == "preserved"
        and action_log.get("latest", {}).get("protected_runtime_spine") == "preserved"
    )
    payload = {
        "version": "v16.50",
        "layer": "command_layer_regression_lock",
        "status": "passed" if passed else "failed",
        "protected_runtime_spine": "preserved",
        "controlled_recursive_expansion": True,
        "uncontrolled_additive_installs": False,
        "checks": {
            "registry_validation_only": registry.get("validation_only") is True,
            "blocked_command_rejected": blocked.accepted is False,
            "allowed_command_accepted": allowed.accepted is True,
            "dispatcher_no_mutation": dispatch.get("mutation_performed") is False,
            "action_log_written": bool(action_log.get("actions")),
        },
    }
    LOCK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

if __name__ == "__main__":
    print(json.dumps(build_command_layer_regression_lock(), indent=2))
