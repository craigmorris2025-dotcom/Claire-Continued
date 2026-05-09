"""
AutoDesignEngine — generates system design artifacts from pipeline context.
Safe, flexible signature to prevent runtime crashes.
"""

from typing import Any, Dict


class AutoDesignEngine:
    """Generates system design output from pipeline context."""

    def generate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Flexible signature to handle any caller pattern:
        - generate(context)
        - generate(intent=..., context=...)
        - generate(context=...)
        """

        context = None
        intent = None

        # Handle positional args
        if args:
            if len(args) == 1:
                context = args[0]
            elif len(args) >= 2:
                intent = args[0]
                context = args[1]

        # Handle keyword args
        if "context" in kwargs:
            context = kwargs["context"]

        if "intent" in kwargs:
            intent = kwargs["intent"]

        # Fail-safe
        if context is None:
            return {
                "status": "failed",
                "error": "No context provided to AutoDesignEngine"
            }

        technology_intelligence = context.get("technology_intelligence", {}) if isinstance(context, dict) else {}
        selected_stack = technology_intelligence.get("selected_stack", {}) if isinstance(technology_intelligence, dict) else {}
        selected_technologies = technology_intelligence.get("technologies_considered", []) if isinstance(technology_intelligence, dict) else []

        # Build minimum viable design output. Route activation is handled by
        # the core output contract and Design Portal, not by forcing every run
        # into design.
        return {
            "status": "success",
            "design": {
                "system_type": "ai_platform",
                "architecture": "modular",
                "components": [
                    "ingestion",
                    "semantic_processing",
                    "analysis_engines",
                    "decision_layer",
                    "api_gateway"
                ],
                "dependencies": [
                    "structured_pipeline_contracts",
                    "run_history_store",
                    "export_writer",
                    "dashboard_api",
                ],
                "constraints": [
                    "route_gated_design_only",
                    "local_desktop_stability",
                    "traceable_outputs_required",
                ],
                "risks": [
                    "over-routing portfolio outputs into design",
                    "technology recommendations without sufficient context",
                ],
                "selected_technologies": selected_technologies,
                "selected_stack": selected_stack,
                "implementation_phases": [
                    "contract alignment",
                    "component mapping",
                    "technology selection",
                    "validation and package export",
                ],
                "inferred_domain": context.get("domain", "unknown"),
                "confidence": context.get("scores", {}).get("_confidence", 0.5),
                "intent_used": bool(intent),
            }
        }
