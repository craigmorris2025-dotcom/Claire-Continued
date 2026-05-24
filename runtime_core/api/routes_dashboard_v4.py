from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from runtime_core.dashboard.payload_compatibility import normalize_dashboard_payload


router = APIRouter(tags=["Dashboard V4"])


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _dashboard_dir() -> Path:
    return _root() / "frontend" / "operator_dashboard" / "v4"


def build_dashboard_v4_payload(raw_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if raw_payload is None:
        from runtime_core.app import _dashboard_payload

        raw_payload = _dashboard_payload()
    return normalize_dashboard_payload(raw_payload)


@router.get("/api/dashboard/v4/payload")
def api_dashboard_v4_payload() -> dict[str, Any]:
    return build_dashboard_v4_payload()


@router.get("/dashboard/v4/payload")
def dashboard_v4_payload() -> dict[str, Any]:
    return build_dashboard_v4_payload()


@router.get("/dashboard/v4", include_in_schema=False)
@router.get("/dashboard/operator-v4", include_in_schema=False)
def dashboard_v4() -> HTMLResponse:
    path = _dashboard_dir() / "index.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dashboard V4 index missing")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/dashboard/v4/assets/{asset_name}", include_in_schema=False)
def dashboard_v4_asset(asset_name: str):
    allowed = {
        "dashboard_v4.css": ("text/css", _dashboard_dir() / "dashboard_v4.css"),
        "dashboard_v4.js": ("application/javascript", _dashboard_dir() / "dashboard_v4.js"),
    }
    item = allowed.get(asset_name)
    if item is None:
        raise HTTPException(status_code=404, detail="Dashboard V4 asset not allowed")
    media_type, path = item
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dashboard V4 asset missing")
    return FileResponse(str(path), media_type=media_type)


def include_dashboard_v4_routes(app: Any) -> None:
    app.include_router(router)
