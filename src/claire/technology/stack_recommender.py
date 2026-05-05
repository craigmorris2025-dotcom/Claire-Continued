"""Route-aware software/platform stack recommender."""

from __future__ import annotations

from typing import Any, Dict, List

from .technology_catalog import TechnologyCatalog
from .technology_search import TechnologySearch


class StackRecommender:
    """Recommend a minimum viable app/software/platform stack."""

    def __init__(self, catalog: TechnologyCatalog | None = None) -> None:
        self.catalog = catalog or TechnologyCatalog()
        self.search = TechnologySearch(self.catalog)

    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}
        keywords = context.get("keywords", [])
        domain = context.get("domain", "general")
        search_terms = list(dict.fromkeys([*keywords, domain, "dashboard", "api", "database", "monitoring"]))
        considered = self.search.keyword(search_terms, limit=10)
        by_id = {item["id"]: item for item in self.catalog.all()}

        stack = {
            "frontend_technologies": [by_id["react"]],
            "backend_technologies": [by_id["fastapi"]],
            "database_technologies": [by_id["sqlite"], by_id["postgresql"]],
            "cloud_services": [],
            "devops_tools": [by_id["docker"]],
            "monitoring_tools": [by_id["prometheus"]],
            "security_tools": [by_id["openapi"]],
            "estimated_cost": "low_for_local_desktop; moderate_for_cloud_scale",
            "estimated_development_time": "2-6 weeks for minimum viable route-aware module",
            "complexity_score": 0.48,
            "scalability_score": 0.72,
            "security_score": 0.68,
            "maintainability_score": 0.74,
        }

        return {
            "status": "success",
            "domain": domain,
            "search_queries": search_terms,
            "technologies_considered": considered,
            "selected_stack": stack,
            "confidence": self._confidence(considered),
        }

    def _confidence(self, considered: List[Dict[str, Any]]) -> float:
        if not considered:
            return 0.42
        return round(min(0.86, 0.52 + len(considered) * 0.035), 4)
