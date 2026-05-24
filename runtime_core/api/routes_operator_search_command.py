
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from runtime_core.operator.search_command_layer import (
    build_search_command_layer,
    capabilities,
    parse_operator_command,
    search_query,
    web_search_request,
    web_search_status,
)

router = APIRouter(tags=["Operator Search Command"])


@router.get("/operator/search/capabilities")
def get_operator_search_capabilities():
    return capabilities()


@router.post("/operator/search/query")
def post_operator_search_query(payload: Dict[str, Any]):
    return search_query(
        query=str(payload.get("query", "")),
        mode=payload.get("mode"),
        limit=int(payload.get("limit", 12)),
    )


@router.post("/operator/command/parse")
def post_operator_command_parse(payload: Dict[str, Any]):
    return parse_operator_command(query=str(payload.get("query", "")))


@router.get("/operator/search/web/status")
def get_operator_web_search_status():
    return web_search_status()


@router.post("/operator/search/web")
def post_operator_web_search(payload: Dict[str, Any]):
    return web_search_request(
        query=str(payload.get("query", "")),
        mode=str(payload.get("mode", "web")),
    )


@router.get("/operator/search/layer")
def get_operator_search_layer():
    return build_search_command_layer()
