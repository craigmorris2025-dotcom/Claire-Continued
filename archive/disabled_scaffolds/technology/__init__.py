"""
Claire Technology Compatibility Exports.

Keeps research/dashboard imports working while the newer technology
intelligence layer is still being wired.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


try:
    from claire.technology.technology_intelligence import TechnologyIntelligenceLayer
except Exception:
    TechnologyIntelligenceLayer = None


class TechnologyCatalog:
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None, *args: Any, **kwargs: Any) -> None:
        self.items: List[Dict[str, Any]] = items or []

    def list(self) -> List[Dict[str, Any]]:
        return self.items

    def all(self) -> List[Dict[str, Any]]:
        return self.items

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        for item in self.items:
            if item.get("name") == name:
                return item
        return default


class TechnologySearch:
    def __init__(self, catalog: Optional[TechnologyCatalog] = None, *args: Any, **kwargs: Any) -> None:
        self.catalog = catalog or TechnologyCatalog()

    def search(self, query: str = "", **kwargs: Any) -> List[Dict[str, Any]]:
        query = (query or "").lower()
        if not query:
            return self.catalog.list()

        return [
            item for item in self.catalog.list()
            if query in str(item).lower()
        ]

    def run(self, query: str = "", **kwargs: Any) -> List[Dict[str, Any]]:
        return self.search(query=query, **kwargs)


class StackRecommender:
    def __init__(self, catalog: Optional[TechnologyCatalog] = None, *args: Any, **kwargs: Any) -> None:
        self.catalog = catalog or TechnologyCatalog()

    def recommend(
        self,
        domain: str = "general",
        use_case: str = "",
        constraints: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "domain": domain,
            "use_case": use_case,
            "recommended_stack": [],
            "constraints": constraints or {},
            "note": "Compatibility recommender active; full technology intelligence layer can enrich this later.",
        }

    def run(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = payload or {}
        return self.recommend(
            domain=payload.get("domain") or kwargs.get("domain", "general"),
            use_case=payload.get("use_case") or payload.get("text") or kwargs.get("use_case", ""),
            constraints=payload.get("constraints") or kwargs.get("constraints", {}),
        )


class ComponentMatcher:
    def __init__(self, catalog: Optional[TechnologyCatalog] = None, *args: Any, **kwargs: Any) -> None:
        self.catalog = catalog or TechnologyCatalog()

    def match(
        self,
        components: Optional[List[str]] = None,
        requirements: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "components": components or [],
            "requirements": requirements or [],
            "matches": [],
            "note": "Compatibility matcher active; full technology intelligence layer can enrich this later.",
        }

    def run(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = payload or {}
        return self.match(
            components=payload.get("components") or kwargs.get("components", []),
            requirements=payload.get("requirements") or kwargs.get("requirements", []),
        )


__all__ = [
    "TechnologyCatalog",
    "TechnologySearch",
    "StackRecommender",
    "ComponentMatcher",
    "TechnologyIntelligenceLayer",
]