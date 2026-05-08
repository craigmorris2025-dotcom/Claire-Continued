"""FastAPI routes for Claire v17.50 dashboard/runtime alignment."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import APIRouter

from claire.dashboard.button_registry import get_button_registry, validate_button_registry
from claire.dashboard.runtime_alignment import build_capability_manifest, get_alignment_status, write_capability_manifest

router = APIRouter(prefix="/dashboard/alignment", tags=["dashboard-alignment"])


@router.get("/status")
def dashboard_alignment_status() -> Dict[str, object]:
    return get_alignment_status(Path.cwd())


@router.get("/capabilities")
def dashboard_alignment_capabilities() -> Dict[str, object]:
    return write_capability_manifest(Path.cwd())


@router.get("/buttons")
def dashboard_alignment_buttons() -> Dict[str, object]:
    return {
        "status": "ok",
        "buttons": get_button_registry(),
        "validation": validate_button_registry(),
    }


@router.get("/verify")
def dashboard_alignment_verify() -> Dict[str, object]:
    manifest = build_capability_manifest(Path.cwd())
    validation = validate_button_registry()
    return {
        "status": "ok" if validation["status"] == "ok" else "failed",
        "version": "17.50",
        "alignment_status": manifest.get("status"),
        "validation": validation,
        "route_candidates": manifest.get("route_candidates", []),
    }
