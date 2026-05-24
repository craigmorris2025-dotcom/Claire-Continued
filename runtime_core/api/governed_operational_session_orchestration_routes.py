from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from runtime_core.api.governed_operational_session_orchestration import (
    build_governed_operational_session_orchestration,
)

router = APIRouter(prefix="/api/governed/session-orchestration", tags=["governed-session-orchestration"])


@router.get("/status")
def governed_operational_session_orchestration_status() -> Dict[str, Any]:
    return build_governed_operational_session_orchestration({})
