from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from runtime_core.technology.technology_base import assess_technology_base, get_acs2_graph, search_technology_base
from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine, build_reemergence_taxonomy
from runtime_core.technology.technology_intelligence import TechnologyIntelligenceLayer


router = APIRouter(tags=["Technology Base"])


@router.get("/api/technology/base")
def technology_base(query: str = "") -> dict[str, Any]:
    return assess_technology_base(query)


@router.get("/api/technology/search")
def technology_search(query: str = "", limit: int = 8) -> dict[str, Any]:
    return search_technology_base(query, limit=limit)


@router.get("/api/technology/intelligence")
def technology_intelligence(query: str = "", domain: str = "technology", route: str = "technology_base") -> dict[str, Any]:
    keywords = [part for part in query.replace(",", " ").split() if part]
    return TechnologyIntelligenceLayer().analyze({"domain": domain, "route": route, "keywords": keywords})


@router.get("/api/technology/reemergence-taxonomy")
def technology_reemergence_taxonomy() -> dict[str, Any]:
    return build_reemergence_taxonomy()


@router.get("/api/technology/reemergence-classify")
def technology_reemergence_classify(query: str = "", entity_id: str = "") -> dict[str, Any]:
    return build_reemergence_pattern_engine(query=query, entity_id=entity_id or None)


@router.get("/api/acs2/{path:path}")
def acs2_visual_command_endpoint(path: str, query: str = "") -> dict[str, Any]:
    normalized = path.strip("/")
    if normalized == "graph":
        return get_acs2_graph(query)
    if normalized == "reemergence-taxonomy":
        return build_reemergence_taxonomy()
    if normalized == "reemergence-classify":
        return build_reemergence_pattern_engine(query=query)
    if normalized.startswith("timeline/"):
        entity_id = normalized.split("/", 1)[1]
        assessment = assess_technology_base(entity_id)
        return assessment.get("root_to_current_timeline", {})
    return {
        "schema_version": "claire.acs2_visual_command_endpoint.v1",
        "status": "unknown_acs2_view",
        "available_views": ["graph", "timeline/{entity_id}"],
    }
