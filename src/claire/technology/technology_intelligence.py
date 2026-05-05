"""Route-gated technology intelligence for AutoDesign and Design Portal."""

from __future__ import annotations

from typing import Any, Dict, List

from .component_matcher import ComponentMatcher
from .stack_recommender import StackRecommender
from .technology_catalog import TechnologyCatalog


class TechnologyIntelligenceLayer:
    """Produce technology recommendations only when design routes require them."""

    DESIGN_ROUTE_TERMS = {
        "solution_design",
        "invention",
        "design",
        "system_architecture",
        "software",
        "platform",
        "operational_redesign",
        "existing_system_replacement",
        "technical_breakthrough",
        "business_system_redesign",
    }

    def __init__(self) -> None:
        self.catalog = TechnologyCatalog()
        self.recommender = StackRecommender(self.catalog)
        self.matcher = ComponentMatcher(self.catalog)

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}
        required, reason = self._required(context)
        if not required:
            return {
                "required": False,
                "technologies_considered": [],
                "selected_stack": {},
                "component_matches": [],
                "compatibility_notes": ["Technology Intelligence skipped by route."],
                "dependency_notes": [],
                "search_queries": [],
                "integration_complexity": "not_required",
                "buildability_notes": [reason],
                "confidence": 0.0,
                "status": "skipped_by_route",
            }

        recommendation = self.recommender.recommend(context)
        components = self._components(context)
        component_matches = self.matcher.match(components)
        selected_stack = recommendation.get("selected_stack", {})
        dependency_notes = self._dependency_notes(selected_stack, component_matches)

        return {
            "required": True,
            "technologies_considered": recommendation.get("technologies_considered", []),
            "selected_stack": selected_stack,
            "component_matches": component_matches,
            "compatibility_notes": self._compatibility_notes(selected_stack),
            "dependency_notes": dependency_notes,
            "search_queries": recommendation.get("search_queries", []),
            "integration_complexity": self._overall_complexity(component_matches),
            "buildability_notes": self._buildability_notes(component_matches),
            "confidence": recommendation.get("confidence", 0.55),
            "status": "success",
        }

    def _required(self, context: Dict[str, Any]) -> tuple[bool, str]:
        route = str(context.get("route_selected") or context.get("route") or "").lower()
        portal = context.get("design_portal", {}) if isinstance(context.get("design_portal"), dict) else {}
        if portal.get("route_to_design") is True:
            return True, "Design Portal route_to_design is true."
        if any(term in route for term in self.DESIGN_ROUTE_TERMS):
            return True, "Selected route requires design/system/software support."
        return False, "Selected route does not require design/system/software construction."

    def _components(self, context: Dict[str, Any]) -> List[Any]:
        system_design = context.get("system_design", {}) if isinstance(context.get("system_design"), dict) else {}
        design = system_design.get("design", {}) if isinstance(system_design.get("design"), dict) else {}
        design_output = context.get("design_output", {}) if isinstance(context.get("design_output"), dict) else {}
        components = design.get("components") or design_output.get("components") or design_output.get("component_map") or []
        if components:
            return components
        return ["ingestion", "semantic_processing", "analysis_engines", "decision_layer", "api_gateway", "monitoring"]

    def _dependency_notes(self, selected_stack: Dict[str, Any], component_matches: List[Dict[str, Any]]) -> List[str]:
        notes = []
        for group, technologies in selected_stack.items():
            if isinstance(technologies, list) and technologies:
                notes.append(f"{group}: {', '.join(item.get('name', item.get('id', 'unknown')) for item in technologies if isinstance(item, dict))}")
        for match in component_matches:
            if match.get("integration_complexity") in {"medium", "high"}:
                notes.append(f"{match.get('component')} integration complexity: {match.get('integration_complexity')}")
        return notes

    def _compatibility_notes(self, selected_stack: Dict[str, Any]) -> List[str]:
        notes = []
        frontend = selected_stack.get("frontend_technologies", [])
        backend = selected_stack.get("backend_technologies", [])
        database = selected_stack.get("database_technologies", [])
        if frontend and backend:
            notes.append("Frontend and backend stack can communicate through OpenAPI-defined routes.")
        if backend and database:
            notes.append("Backend stack supports local-first SQLite and scalable PostgreSQL persistence.")
        notes.append("Technology stack is advisory and route-gated; it should not activate portfolio-only outputs.")
        return notes

    def _buildability_notes(self, component_matches: List[Dict[str, Any]]) -> List[str]:
        notes = [match.get("buildability_note", "") for match in component_matches if match.get("buildability_note")]
        return notes or ["Buildability requires component map and selected technology stack."]

    def _overall_complexity(self, component_matches: List[Dict[str, Any]]) -> str:
        levels = {match.get("integration_complexity") for match in component_matches}
        if "high" in levels:
            return "high"
        if "medium" in levels:
            return "medium"
        return "low" if component_matches else "unknown"
