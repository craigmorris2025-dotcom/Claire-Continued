from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query
from claire.governance.governed_cockpit_operation_visuals import (
    build_visual_actions,
    build_visual_buttons,
    build_visual_cards,
    build_visual_payload,
    build_visual_preview,
    build_visual_status,
    build_visual_stop_gate,
)

router = APIRouter(tags=["cockpit-operation-visual-controls"])

@router.get("/api/cockpit/operation-visuals/payload")
def cockpit_operation_visuals_payload():
    return build_visual_payload()

@router.get("/api/cockpit/operation-visuals/buttons")
def cockpit_operation_visuals_buttons():
    buttons = build_visual_buttons()
    return {"buttons": buttons, "count": len(buttons), "execution_enabled": False}

@router.get("/api/cockpit/operation-visuals/cards")
def cockpit_operation_visuals_cards():
    cards = build_visual_cards()
    return {"cards": cards, "count": len(cards), "execution_enabled": False}

@router.get("/api/cockpit/operation-visuals/actions")
def cockpit_operation_visuals_actions():
    actions = build_visual_actions()
    return {"actions": actions, "count": len(actions), "execution_enabled": False}

@router.get("/api/cockpit/operation-visuals/status")
def cockpit_operation_visuals_status():
    return build_visual_status()

@router.get("/api/cockpit/operation-visuals/stop-gate")
def cockpit_operation_visuals_stop_gate():
    return build_visual_stop_gate()

@router.get("/api/cockpit/operation-visuals/preview/{operation_key}")
def cockpit_operation_visuals_preview(operation_key: str, command: Optional[str] = Query(default=None)):
    return build_visual_preview(operation_key=operation_key, command=command)

@router.get("/api/command-bar/visual-operations/payload")
def command_bar_visual_operations_payload():
    payload = build_visual_payload()
    return {
        "buttons": payload["buttons"],
        "button_groups": payload["button_groups"],
        "actions": payload["actions"],
        "status": payload["status"],
        "execution_enabled": False,
        "command_execution_enabled": False,
    }

@router.get("/api/internet/s984-operation-visual-mount")
def internet_s984_operation_visual_mount():
    return build_visual_stop_gate()
