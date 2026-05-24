"""
Optional FastAPI route adapter for v18.54 visible query-result verification.

Safe to import when FastAPI is unavailable.
"""

from __future__ import annotations

from typing import Optional

from runtime_core.governed_web.visible_query_result_verification import verify_visible_query_result


try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - FastAPI may not be installed in minimal checks
    APIRouter = None  # type: ignore


if APIRouter is not None:
    router = APIRouter(prefix="/governed-web", tags=["governed-web"])

    @router.get("/search/visible-result-verification")
    def governed_visible_query_result_verification(
        q: str,
        manual_enable: Optional[bool] = None,
    ):
        return verify_visible_query_result(q, manual_enable=manual_enable)
else:
    router = None
