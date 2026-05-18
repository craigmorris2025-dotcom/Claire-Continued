from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from claire.dashboard.final_dashboard_payload import build_final_dashboard_payload


router = APIRouter(tags=["Dashboard V5"])


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _dashboard_dir() -> Path:
    return _root() / "frontend" / "operator_dashboard" / "v5"


@router.get("/api/dashboard/v5/payload")
def api_dashboard_v5_payload(request: Request) -> dict[str, Any]:
    return build_final_dashboard_payload(routes=request.app.routes)


@router.get("/dashboard/v5/payload")
def dashboard_v5_payload(request: Request) -> dict[str, Any]:
    return build_final_dashboard_payload(routes=request.app.routes)


@router.get("/dashboard/v5", include_in_schema=False)
@router.get("/dashboard/final-user", include_in_schema=False)
def dashboard_v5() -> HTMLResponse:
    path = _dashboard_dir() / "index.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dashboard V5 index missing")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/dashboard/v5/assets/{asset_name}", include_in_schema=False)
def dashboard_v5_asset(asset_name: str):
    allowed = {
        "dashboard_v5.css": ("text/css", _dashboard_dir() / "dashboard_v5.css"),
        "dashboard_v5.js": ("application/javascript", _dashboard_dir() / "dashboard_v5.js"),
    }
    item = allowed.get(asset_name)
    if item is None:
        raise HTTPException(status_code=404, detail="Dashboard V5 asset not allowed")
    media_type, path = item
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dashboard V5 asset missing")
    return FileResponse(str(path), media_type=media_type)


def include_dashboard_v5_routes(app: Any) -> None:
    app.include_router(router)
