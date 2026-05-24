"""API routes for Claire v19.25 search execution contract."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from runtime_core.runtime.search_execution_contract import (
    SearchExecutionRequest,
    build_search_execution_contract,
    summarize_search_execution_contract,
)

router = APIRouter(prefix="/runtime/search", tags=["runtime-search"])


class SearchExecutionPayload(BaseModel):
    query: str = Field(default="", description="Operator search query from the permanent search bar.")
    intent: str = Field(default="web_search")
    requested_by: str = Field(default="operator")
    source: str = Field(default="dashboard_search_bar")
    execution_mode: str = Field(default="dry_run")
    session_id: str = Field(default="default")
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/execute")
def create_search_execution(payload: SearchExecutionPayload) -> Dict[str, Any]:
    contract = build_search_execution_contract(
        SearchExecutionRequest(
            query=payload.query,
            intent=payload.intent,
            requested_by=payload.requested_by,
            source=payload.source,
            execution_mode=payload.execution_mode,
            session_id=payload.session_id,
            metadata=payload.metadata,
        )
    )
    return {
        "status": "blocked" if contract.blocked else "ok",
        "contract": contract.to_dict(),
        "summary": summarize_search_execution_contract(contract),
    }


@router.get("/health")
def search_execution_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "version": "v19.25",
        "component": "end_to_end_search_execution_contract",
        "retrieval_performed": False,
        "contract_ready": True,
    }
