"""
Optional FastAPI route adapter for v18.53 dashboard smoke testing.

This file is safe to import even if FastAPI is unavailable.
"""

from __future__ import annotations

from typing import Optional

from claire.governed_web.live_search_dashboard_smoke import (
    execute_live_search_dashboard_smoke,
)


try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - FastAPI may not be installed in minimal checks
    APIRouter = None  # type: ignore


if APIRouter is not None:
    router = APIRouter(prefix="/governed-web", tags=["governed-web"])

    @router.get("/search/dashboard-smoke")
    def governed_live_search_dashboard_smoke(
        q: str,
        manual_enable: Optional[bool] = None,
    ):
        return execute_live_search_dashboard_smoke(q, manual_enable=manual_enable)
else:
    router = None
