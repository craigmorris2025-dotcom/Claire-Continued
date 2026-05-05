"""Map design components to compatible technologies."""

from __future__ import annotations

from typing import Any, Dict, List

from .technology_catalog import TechnologyCatalog
from .technology_search import TechnologySearch


class ComponentMatcher:
    """Match AutoDesign/SystemDesign components to catalog technologies."""

    COMPONENT_HINTS = {
        "ingestion": ["fastapi", "sqlite"],
        "semantic_processing": ["vector_index", "fastapi"],
        "analysis_engines": ["fastapi", "postgresql"],
        "decision_layer": ["fastapi", "openapi"],
        "api_gateway": ["fastapi", "openapi"],
        "dashboard": ["react"],
        "monitoring": ["prometheus"],
        "run_history": ["sqlite", "postgresql"],
        "job_state": ["redis"],
    }

    def __init__(self, catalog: TechnologyCatalog | None = None) -> None:
        self.catalog = catalog or TechnologyCatalog()
        self.search = TechnologySearch(self.catalog)

    def match(self, components: List[Any]) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        for component in components or []:
            name = self._component_name(component)
            normalized = name.strip().lower().replace(" ", "_")
            technology_ids = self.COMPONENT_HINTS.get(normalized, [])
            technologies = [self.catalog.by_id(item) for item in technology_ids]
            if not technologies:
                technologies = self.search.keyword(name, limit=3)
            matches.append({
                "component": name,
                "matched_technologies": [item for item in technologies if item],
                "integration_complexity": self._complexity(technologies),
                "buildability_note": f"{name} can be implemented with the matched stack components." if technologies else f"No strong catalog match for {name}.",
            })
        return matches

    def _component_name(self, component: Any) -> str:
        if isinstance(component, dict):
            return str(component.get("component") or component.get("name") or component.get("id") or "unnamed_component")
        return str(component or "unnamed_component")

    def _complexity(self, technologies: List[Dict[str, Any]]) -> str:
        levels = {item.get("integration_complexity") for item in technologies if isinstance(item, dict)}
        if "high" in levels:
            return "high"
        if "medium" in levels:
            return "medium"
        return "low" if technologies else "unknown"
