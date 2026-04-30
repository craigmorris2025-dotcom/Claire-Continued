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

        # Build simple design output (you can expand later)
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
                "inferred_domain": context.get("domain", "unknown"),
                "confidence": context.get("scores", {}).get("_confidence", 0.5),
                "intent_used": bool(intent),
            }
        }
