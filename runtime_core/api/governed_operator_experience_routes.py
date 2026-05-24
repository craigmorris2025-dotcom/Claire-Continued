from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import Response

from runtime_core.governance.governed_operator_experience_console import (
    build_operator_actions,
    build_operator_cards,
    build_operator_experience_payload,
    build_operator_status,
    get_operator_buttons,
    preview_operation,
)

router = APIRouter(tags=["Claire Operator Experience Console"])

@router.get("/api/cockpit/operator-experience/payload")
def operator_experience_payload():
    return build_operator_experience_payload()

@router.get("/api/cockpit/operator-experience/buttons")
def operator_experience_buttons():
    buttons = get_operator_buttons()
    return {"status": "ready", "buttons": buttons, "count": len(buttons)}

@router.get("/api/cockpit/operator-experience/cards")
def operator_experience_cards():
    cards = build_operator_cards()
    return {"status": "ready", "cards": cards, "count": len(cards)}

@router.get("/api/cockpit/operator-experience/actions")
def operator_experience_actions():
    actions = build_operator_actions()
    return {"status": "ready", "actions": actions, "count": len(actions)}

@router.get("/api/cockpit/operator-experience/status")
def operator_experience_status():
    return build_operator_status()

@router.get("/api/cockpit/operator-experience/stop-gate")
def operator_experience_stop_gate():
    payload = build_operator_experience_payload()
    return {"status": "ready", "stop_gate": payload["stop_gate"], "blocked_authorities": payload["blocked_authorities"]}

@router.get("/api/cockpit/operator-experience/preview/{operation_key}")
def operator_experience_preview(operation_key: str):
    return preview_operation(operation_key)

@router.get("/api/command-bar/operator-experience/payload")
def command_bar_operator_experience_payload():
    return build_operator_experience_payload()

@router.get("/api/command-bar/operator-experience/buttons")
def command_bar_operator_experience_buttons():
    buttons = get_operator_buttons()
    return {"status": "ready", "buttons": buttons, "count": len(buttons)}

@router.get("/api/command-bar/operator-experience/preview/{operation_key}")
def command_bar_operator_experience_preview(operation_key: str):
    return preview_operation(operation_key)

@router.get("/api/internet/operator-experience/payload")
def internet_operator_experience_payload():
    return build_operator_experience_payload()

@router.get("/api/internet/s1040-stop-gate")
def internet_s1040_stop_gate():
    payload = build_operator_experience_payload()
    return {"status": "ready", "stop_gate": payload["stop_gate"], "unlock_allowed": False}

@router.get("/api/cockpit/operator-experience/assets/js")
def operator_experience_js_asset():
    js_path = Path.cwd() / "frontend" / "cockpit" / "assets" / "claire_operator_experience_console.js"
    return Response(js_path.read_text(encoding="utf-8"), media_type="application/javascript")

@router.get("/api/cockpit/operator-experience/assets/css")
def operator_experience_css_asset():
    css_path = Path.cwd() / "frontend" / "cockpit" / "assets" / "claire_operator_experience_console.css"
    return Response(css_path.read_text(encoding="utf-8"), media_type="text/css")
