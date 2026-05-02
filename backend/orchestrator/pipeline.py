"""Legacy pipeline wrapper for the active Claire orchestrator."""

from __future__ import annotations

from claire.orchestrator.pipeline_v4 import PipelineOrchestrator as ActivePipelineOrchestrator


class PipelineOrchestrator(ActivePipelineOrchestrator):
    def execute(self, intent):
        result = super().execute(intent)
        result.intent_id = getattr(intent, "id", getattr(intent, "intent_id", "unknown"))
        if result.decision_classification == "CONSIDER":
            result.decision_classification = "CAUTION"
        return result
