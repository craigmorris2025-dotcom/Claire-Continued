"""
Claire Technology Intelligence Layer

Safe v6 compatibility module.
Provides the TechnologyIntelligenceLayer expected by pipeline_v4.py.
"""

from typing import Any, Dict, List


class TechnologyIntelligenceLayer:
    """
    Lightweight technology intelligence adapter.

    This keeps the v6 pipeline stable when the full technology intelligence
    subsystem is not yet installed.
    """

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}

        domain = context.get("domain", "general")
        keywords = context.get("keywords", []) or []
        route = context.get("route", "unknown")

        selected_stack = self._select_stack(domain=domain, keywords=keywords)

        return {
            "status": "available",
            "mode": "safe_compatibility",
            "route": route,
            "domain": domain,
            "keywords": keywords,
            "selected_stack": selected_stack,
            "component_recommendations": self._component_recommendations(selected_stack),
            "dependency_notes": self._dependency_notes(selected_stack),
            "integration_complexity": self._integration_complexity(selected_stack),
            "buildability_notes": self._buildability_notes(domain, selected_stack),
            "confidence": 0.62,
        }

    def _select_stack(self, domain: str, keywords: List[str]) -> Dict[str, Any]:
        keyword_text = " ".join(str(k).lower() for k in keywords)

        if domain == "technology" or any(
            term in keyword_text
            for term in ["ai", "software", "platform", "model", "data", "autonomous"]
        ):
            return {
                "application_layer": ["FastAPI", "Python"],
                "intelligence_layer": ["rules engine", "model adapter", "signal scoring"],
                "data_layer": ["JSON outputs", "local file persistence"],
                "interface_layer": ["dashboard", "review tabs"],
                "deployment_layer": ["local runtime", "safe installer"],
            }

        if domain == "finance" or any(
            term in keyword_text
            for term in ["portfolio", "market", "asset", "investment", "financial"]
        ):
            return {
                "application_layer": ["FastAPI", "Python"],
                "intelligence_layer": ["portfolio scoring", "risk scoring", "signal governance"],
                "data_layer": ["market signal files", "portfolio outputs"],
                "interface_layer": ["portfolio dashboard", "review tabs"],
                "deployment_layer": ["local runtime", "safe installer"],
            }

        return {
            "application_layer": ["FastAPI", "Python"],
            "intelligence_layer": ["deterministic scoring", "route-aware lifecycle"],
            "data_layer": ["JSON outputs"],
            "interface_layer": ["dashboard"],
            "deployment_layer": ["local runtime"],
        }

    def _component_recommendations(self, selected_stack: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "core_components": list(selected_stack.keys()),
            "priority": [
                "keep runtime stable",
                "avoid optional dependency crashes",
                "preserve route-aware outputs",
            ],
        }

    def _dependency_notes(self, selected_stack: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "external_dependencies_required": False,
            "notes": [
                "Compatibility layer uses standard Python only.",
                "Full technology catalog can replace this module later.",
            ],
        }

    def _integration_complexity(self, selected_stack: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "level": "low",
            "reason": "Module provides the interface expected by pipeline_v4.py without changing pipeline routing.",
        }

    def _buildability_notes(self, domain: str, selected_stack: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "buildability": "safe",
            "domain": domain,
            "notes": [
                "Prevents missing-module failure.",
                "Keeps technology intelligence available as a safe optional subsystem.",
            ],
        }