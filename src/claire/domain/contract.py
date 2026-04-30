
"""
Claire Domain Contract — shared data structures for intents, results, and semantic output.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class IntentMetadata:
    """Metadata attached to a Claire request."""

    source: str = "api"
    priority: str = "medium"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_any(cls, value: Any) -> "IntentMetadata":
        if isinstance(value, cls):
            return value

        if isinstance(value, dict):
            return cls(
                source=value.get("source", "api"),
                priority=value.get("priority", "medium"),
                user_id=value.get("user_id"),
                session_id=value.get("session_id"),
                tags=value.get("tags", []),
            )

        return cls()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "priority": self.priority,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tags": self.tags,
        }


class ClaireIntent:
    """Standard request contract."""

    def __init__(
        self,
        raw_input: str,
        intent_id: Optional[str] = None,
        mode: str = "deterministic",
        request_type: str = "evaluate",
        metadata: Optional[Any] = None,
        **extra: Any,
    ):
        self.intent_id = intent_id or extra.get("id") or "unknown"
        self.id = self.intent_id
        self.raw_input = raw_input or ""
        self.mode = mode or "deterministic"
        self.request_type = request_type or "evaluate"
        self.metadata = IntentMetadata.from_any(metadata)
        self.extra = extra or {}

    def get_text(self) -> str:
        return self.raw_input

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "id": self.id,
            "raw_input": self.raw_input,
            "mode": self.mode,
            "request_type": self.request_type,
            "metadata": self.metadata.to_dict(),
            "extra": self.extra,
        }


@dataclass
class SemanticRepresentation:
    """Semantic/NLP representation of an input."""

    dimensions: Dict[str, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    domain: str = "general"
    entities: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions": self.dimensions,
            "keywords": self.keywords,
            "domain": self.domain,
            "entities": self.entities,
            "confidence": self.confidence,
        }


class ClaireResult:
    """Standard pipeline result contract."""

    def __init__(
        self,
        status: str = "success",
        mode: str = "deterministic",
        decision_classification: str = "UNKNOWN",
        breakthrough_classification: str = "UNKNOWN",
        scores: Optional[Dict[str, float]] = None,
        data: Optional[Dict[str, Any]] = None,
        acquirer_matches: Optional[List[Dict[str, Any]]] = None,
        ready_for_syntalion: bool = False,
        run_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        **extra: Any,
    ):
        self.status = status
        self.mode = mode
        self.decision_classification = decision_classification
        self.breakthrough_classification = breakthrough_classification
        self.scores = scores or {}
        self.data = data or {}
        self.acquirer_matches = acquirer_matches or []
        self.ready_for_syntalion = ready_for_syntalion
        self.run_id = run_id or intent_id or self.data.get("intent_id") or "unknown"
        self.extra = extra or {}

    @property
    def confidence(self) -> float:
        return self.scores.get("_confidence", self.scores.get("portfolio_score", 0.0))

    def to_dict(self) -> Dict[str, Any]:
        connector_sources = (
            self.data.get("connector_sources")
            or self.data.get("external_signals")
            or {}
        )

        return {
            "run_id": self.run_id,
            "status": self.status,
            "mode": self.mode,
            "decision_classification": self.decision_classification,
            "breakthrough_classification": self.breakthrough_classification,

            "scores": self.scores,
            "acquirer_matches": self.acquirer_matches,

            "domain": self.data.get("domain", "general"),
            "keywords": self.data.get("keywords", []),
            "domain_scores": self.data.get("domain_scores", {}),

            "knowledge_ingestion": self.data.get("knowledge_ingestion", {}),
            "signal_extraction": self.data.get("signal_extraction", {}),
            "market_gap": self.data.get("market_gap", {}),
            "opportunity_discovery": self.data.get("opportunity_discovery", {}),
            "breakthrough_synthesis": self.data.get("breakthrough_synthesis", {}),
            "technical_feasibility": self.data.get("technical_feasibility", {}),
            "productization_path": self.data.get("productization_path", {}),
            "trend_trajectory": self.data.get("trend_trajectory", {}),
            "market_formation": self.data.get("market_formation", {}),
            "moat": self.data.get("moat", {}),
            "risk_regulation": self.data.get("risk_regulation", {}),
            "business_model": self.data.get("business_model", {}),
            "deal_exit_modeling": self.data.get("deal_exit_modeling", {}),
            "strategic_positioning": self.data.get("strategic_positioning", {}),

            "engine_details": self.data.get("engine_details", {}),
            "connector_sources": connector_sources,
            "signal_trace": self.data.get("signal_trace", {}),

            "system_design": self.data.get("system_design", {}),
            "design_portal": self.data.get("design_portal", {}),
            "design_output": self.data.get("design_output", {}),
            "portfolio_binder": self.data.get("portfolio_binder", {}),
            "export_package": self.data.get("export_package", {}),

            "lifecycle": self.data.get("lifecycle", {}),
            "lifecycle_stages": self.data.get("lifecycle_stages", []),
            "lifecycle_summary": self.data.get("lifecycle_summary", {}),

            "phase_log": self.data.get("phase_log", []),

            "syntalion_ready": self.ready_for_syntalion,
            "confidence": self.confidence,
        }


class ContractValidator:
    """Lightweight validator for incoming requests."""

    def validate_intent(self, payload: Dict[str, Any]) -> ClaireIntent:
        raw_input = (
            payload.get("raw_input")
            or payload.get("text")
            or payload.get("input")
            or ""
        )

        return ClaireIntent(
            intent_id=payload.get("intent_id") or payload.get("id"),
            raw_input=raw_input,
            mode=payload.get("mode", "deterministic"),
            request_type=payload.get("request_type", "evaluate"),
            metadata=payload.get("metadata"),
        )

    def validate(self, payload: Dict[str, Any]) -> ClaireIntent:
        return self.validate_intent(payload)


__all__ = [
    "IntentMetadata",
    "ClaireIntent",
    "ClaireResult",
    "SemanticRepresentation",
    "ContractValidator",
]
