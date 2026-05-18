from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query
from claire.governance.governed_cockpit_operation_controls import (
    build_button_preview,
    build_command_surface,
    build_operation_actions,
    build_operation_buttons,
    build_operation_cards,
    build_operation_payload,
    build_status,
    build_stop_gate,
)

router = APIRouter(tags=["cockpit-operation-controls"])

@router.get("/api/cockpit/operations/payload")
def cockpit_operations_payload():
    return build_operation_payload()

@router.get("/api/cockpit/operations/buttons")
def cockpit_operations_buttons():
    buttons = build_operation_buttons()
    return {"buttons": buttons, "count": len(buttons), "execution_enabled": False}

@router.get("/api/cockpit/operations/cards")
def cockpit_operations_cards():
    cards = build_operation_cards()
    return {"cards": cards, "count": len(cards), "execution_enabled": False}

@router.get("/api/cockpit/operations/actions")
def cockpit_operations_actions():
    actions = build_operation_actions()
    return {"actions": actions, "count": len(actions), "execution_enabled": False}

@router.get("/api/cockpit/operations/status")
def cockpit_operations_status():
    return build_status()

@router.get("/api/cockpit/operations/stop-gate")
def cockpit_operations_stop_gate():
    return build_stop_gate()

@router.get("/api/cockpit/operations/preview/{operation_key}")
def cockpit_operation_preview(operation_key: str, command: Optional[str] = Query(default=None)):
    return build_button_preview(operation_key, supplied_command=command)

@router.get("/api/command-bar/operations/payload")
def command_bar_operations_payload():
    payload = build_operation_payload()
    return {
        "command_surface": payload["command_surface"],
        "buttons": payload["buttons"],
        "actions": payload["actions"],
        "blocked_capabilities": payload["blocked_capabilities"],
        "execution_enabled": False,
    }

@router.get("/api/command-bar/operations/buttons")
def command_bar_operations_buttons():
    buttons = build_operation_buttons()
    return {"buttons": buttons, "count": len(buttons), "execution_enabled": False}

@router.get("/api/command-bar/submit/preview")
def command_bar_submit_preview(command: str = Query(default="")):
    return {
        "status": "command_preview_only",
        "command": command,
        "command_surface": build_command_surface(),
        "message": "Command bar execution is blocked; this endpoint returns only governed operation suggestions.",
        "suggested_buttons": build_operation_buttons()[:7],
        "execution_enabled": False,
        "command_execution_enabled": False,
    }

@router.get("/api/internet/operation-controls/payload")
def internet_operation_controls_payload():
    return build_operation_payload()

@router.get("/api/internet/s956-stop-gate")
def internet_s956_stop_gate():
    return build_stop_gate()
