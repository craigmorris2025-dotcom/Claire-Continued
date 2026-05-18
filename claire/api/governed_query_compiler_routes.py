from __future__ import annotations

from fastapi import APIRouter, Query

from claire.governance.governed_query_compiler import (
    build_governed_query_plan,
    build_query_actions,
    build_query_cards,
    build_query_compiler_payload,
    blocked_authority,
)


router = APIRouter(tags=["Claire Governed Query Compiler"])


@router.get("/api/search/governed/query/compile")
def get_governed_query_compile(
    query: str = Query(default="", description="Query to compile. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return build_governed_query_plan(query=query, route_context=route_context)


@router.get("/api/search/governed/query/sample")
def get_governed_query_sample():
    return build_governed_query_plan(
        query="Claire governed source registry official documentation update readiness",
        route_context="web_source_search",
    )


@router.get("/api/search/governed/query/cards")
def get_governed_query_cards(
    query: str = Query(default="", description="Query to compile into cards. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return {"cards": build_query_cards(query=query, route_context=route_context)}


@router.get("/api/search/governed/query/actions")
def get_governed_query_actions(
    query: str = Query(default="", description="Query to compile into action descriptors. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return {"actions": build_query_actions(query=query, route_context=route_context)}


@router.get("/api/search/governed/query/policy")
def get_governed_query_policy():
    return {
        "execution": "blocked",
        "provider_execution": "blocked",
        "body_reads": "blocked",
        "network_requests": "not_performed",
        "runtime_truth_mutation": "blocked",
        "authority": blocked_authority(),
    }


@router.get("/api/search/governed/query/status")
def get_governed_query_status():
    return {
        "phase": "S618-S624",
        "status": "ready",
        "query_compiler": "available_non_executing",
        "execution": "blocked",
        "next": "S625-S631 provider capability map and probe readiness hardening",
        "authority": blocked_authority(),
    }


@router.get("/api/search/governed/query/payload")
def get_governed_query_payload(
    query: str = Query(default="", description="Query to compile. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return build_query_compiler_payload(query=query, route_context=route_context)

