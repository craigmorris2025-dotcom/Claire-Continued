"""
Claire Syntalion v17.97
Search Bar Dashboard API Adapter

Purpose:
- Provides a read-only API adapter for the permanent search bar dashboard contract.
- Does not rewire dashboard HTML.
- Does not execute live web search.
- Does not enable automatic updates or autonomous agent execution.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from fastapi import APIRouter
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    APIRouter = None
    BaseModel = object

from runtime_core.search.search_bar_dashboard_contract import SearchBarDashboardContract


class SearchBarDashboardRequest(BaseModel):
    query: str
    requested_mode: str | None = None


def submit_search_bar_dashboard_query(
    query: str,
    requested_mode: str | None = None,
) -> Dict[str, Any]:
    contract = SearchBarDashboardContract()
    result = contract.submit_for_dashboard(query, requested_mode)

    result["api_adapter_version"] = "v17.97"
    result["api_read_only"] = True
    result["dashboard_rewire_performed"] = False
    result["live_web_execution_enabled"] = False
    result["automatic_updates_enabled"] = False
    result["autonomous_agent_execution_enabled"] = False
    result["runtime_truth_mutation_enabled"] = False

    return result


if APIRouter is not None:
    router = APIRouter(prefix="/search-bar", tags=["Search Bar"])

    @router.post("/dashboard")
    def search_bar_dashboard_submit(request: SearchBarDashboardRequest) -> Dict[str, Any]:
        return submit_search_bar_dashboard_query(
            query=request.query,
            requested_mode=request.requested_mode,
        )

    @router.get("/status")
    def search_bar_dashboard_status() -> Dict[str, Any]:
        return {
            "version": "v17.97",
            "status": "SEARCH_BAR_DASHBOARD_API_READY",
            "read_only": True,
            "dashboard_rewire_performed": False,
            "live_web_execution_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }
else:
    router = None
