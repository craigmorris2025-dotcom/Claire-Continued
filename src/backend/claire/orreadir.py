"""
Orreadir Layer — Request routing and prioritization.
Analyzes intent, determines pipeline path, applies mode constraints.
"""
import logging
from typing import Any, Dict, List
from backend.claire.contract import ClaireIntent
logger = logging.getLogger("claire.orreadir")

ROUTE_TABLE = {
    "evaluate": ("full_evaluation", 2, [
        "contract", "orreadir", "nlp", "engines", "scoring",
        "acquirer_matching", "orchestrator", "bridge",
    ]),
    "analyze": ("analysis_only", 3, [
        "contract", "orreadir", "nlp", "engines", "scoring", "orchestrator",
    ]),
    "plan": ("planning", 1, [
        "contract", "orreadir", "planner", "orchestrator", "bridge",
    ]),
    "construct": ("construction", 1, [
        "contract", "orreadir", "planner", "nlp", "engines",
        "scoring", "orchestrator", "bridge",
    ]),
}

HIGH_PRIORITY_SIGNALS = {
    "urgent", "critical", "defense", "national security",
    "classified", "immediate", "time-sensitive", "emergency",
}
LOW_PRIORITY_SIGNALS = {"test", "demo", "example", "sandbox", "trial"}


class RouteDecision:
    """Encapsulates a routing decision."""
    __slots__ = ("pipeline", "priority_rank", "phases", "skip_phases", "metadata")

    def __init__(self, pipeline: str, priority_rank: int, phases: List[str],
                 skip_phases: List[str] = None, metadata: Dict[str, Any] = None):
        self.pipeline = pipeline
        self.priority_rank = priority_rank
        self.phases = phases
        self.skip_phases = skip_phases or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline": self.pipeline, "priority_rank": self.priority_rank,
            "phases": self.phases, "skip_phases": self.skip_phases,
            "metadata": self.metadata,
        }


class OrreadirRouter:
    """Routes validated intents to the appropriate processing pipeline."""

    def route(self, intent: ClaireIntent) -> RouteDecision:
        route_key = intent.request_type if intent.request_type in ROUTE_TABLE else "evaluate"
        pipeline, base_priority, phases = ROUTE_TABLE[route_key]

        priority = self._compute_priority(intent, base_priority)
        skip = self._mode_constraints(intent.mode, phases)
        active = [p for p in phases if p not in skip]

        decision = RouteDecision(
            pipeline=pipeline, priority_rank=priority, phases=active,
            skip_phases=skip, metadata={
                "request_type": intent.request_type, "mode": intent.mode,
                "source": intent.metadata.source,
                "input_length": len(intent.raw_input),
            },
        )
        logger.info(f"Routed {intent.id} -> {pipeline} (priority={priority}, phases={len(active)})")
        return decision

    def _compute_priority(self, intent: ClaireIntent, base: int) -> int:
        priority_map = {"high": 1, "medium": 3, "low": 5}
        priority = priority_map.get(intent.metadata.priority, base)
        text_lower = intent.raw_input.lower()
        for sig in HIGH_PRIORITY_SIGNALS:
            if sig in text_lower:
                priority = min(priority, 1)
                break
        for sig in LOW_PRIORITY_SIGNALS:
            if sig in text_lower:
                priority = max(priority, 4)
                break
        return priority

    def _mode_constraints(self, mode: str, phases: List[str]) -> List[str]:
        skip = []
        if mode == "deterministic" and "connectors" in phases:
            skip.append("connectors")
        return skip

    def get_status(self) -> Dict[str, Any]:
        return {"component": "OrreadirRouter", "status": "active", "routes": list(ROUTE_TABLE.keys())}
