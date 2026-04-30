from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ClaireIntent(BaseModel):
    """
    Canonical input object for the pipeline
    """

    intent_id: str
    raw_input: str
    mode: str = "deterministic"

    # 🔥 FORCE NORMALIZATION (this is the fix)
    def get_text(self) -> str:
        if not self.raw_input:
            return ""
        return str(self.raw_input).strip().lower()


class ClaireResult(BaseModel):
    """
    Final pipeline output
    """

    status: str
    mode: str
    decision_classification: str
    breakthrough_classification: str
    scores: Dict[str, float]
    data: Dict[str, Any]
    acquirer_matches: List[Dict[str, Any]]
    ready_for_syntalion: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.data.get("intent_id", "unknown"),
            "status": self.status,
            "mode": self.mode,
            "decision_classification": self.decision_classification,
            "breakthrough_classification": self.breakthrough_classification,
            "scores": self.scores,
            "acquirer_matches": self.acquirer_matches,
            "domain": self.data.get("domain"),
            "keywords": self.data.get("keywords"),
            "domain_scores": self.data.get("domain_scores", {}),
            "engine_details": self.data.get("engine_details", {}),
            "connector_sources": self.data.get("external_signals", {}),
            "system_design": self.data.get("system_design", {}),
            "syntalion_ready": self.ready_for_syntalion,
            "confidence": self.scores.get("_confidence", 0),
        }
