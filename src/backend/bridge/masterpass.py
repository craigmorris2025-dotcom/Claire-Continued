"""
MasterPass Bridge — CLAIRE → Syntalion handoff protocol.
5-stage pipeline: Prep → Call → Normalize → Post → Assert.
"""
import logging
from typing import Any, Dict

logger = logging.getLogger("claire.bridge.masterpass")


class MasterPassBridge:
    """MasterPass Bridge: validates and transforms ClaireResult for Syntalion."""

    READINESS_THRESHOLD = 0.35
    CONFIDENCE_MINIMUM = 0.15

    def process(self, result: Any) -> Dict[str, Any]:
        """Execute the 5-stage bridge: Prep → Call → Normalize → Post → Assert."""
        stages: Dict[str, Any] = {}

        # Stage 1: PREP — validate input completeness
        prep = self._stage_prep(result)
        stages["prep"] = prep
        if not prep["valid"]:
            return {"syntalion_ready": False, "stages": stages, "reason": prep["reason"]}

        # Stage 2: CALL — extract and structure payload
        call = self._stage_call(result)
        stages["call"] = call

        # Stage 3: NORMALIZE — normalize score ranges
        normalize = self._stage_normalize(call["payload"])
        stages["normalize"] = normalize

        # Stage 4: POST — post-processing and enrichment
        post = self._stage_post(normalize["normalized"], result)
        stages["post"] = post

        # Stage 5: ASSERT — final readiness assertion
        assertion = self._stage_assert(post["enriched"])
        stages["assert"] = assertion

        logger.info(f"MasterPass: syntalion_ready={assertion['ready']}, "
                     f"confidence={assertion.get('confidence', 0):.3f}")

        return {
            "syntalion_ready": assertion["ready"],
            "stages": stages,
            "confidence": assertion.get("confidence", 0),
            "payload": post["enriched"] if assertion["ready"] else None,
        }

    def _stage_prep(self, result: Any) -> Dict[str, Any]:
        """Validate that the result has minimum required data."""
        scores = getattr(result, "scores", None) or {}
        if not scores:
            return {"valid": False, "reason": "no_scores"}
        if not getattr(result, "semantic", None):
            return {"valid": False, "reason": "no_semantic"}
        if not getattr(result, "plan", None):
            return {"valid": False, "reason": "no_plan"}
        return {"valid": True, "reason": "ok", "score_count": len(scores)}

    def _stage_call(self, result: Any) -> Dict[str, Any]:
        """Extract structured payload from ClaireResult."""
        scores = getattr(result, "scores", {}) or {}
        semantic = getattr(result, "semantic", None)
        payload = {
            "intent_id": getattr(result, "intent_id", ""),
            "mode": getattr(result, "mode", "deterministic"),
            "decision": getattr(result, "decision_classification", "UNKNOWN"),
            "breakthrough": getattr(result, "breakthrough_classification", "UNKNOWN"),
            "scores": dict(scores),
            "domain": getattr(semantic, "domain", "general") if semantic else "general",
            "keywords": getattr(semantic, "keywords", []) if semantic else [],
            "acquirer_matches": getattr(result, "acquirer_matches", []),
        }
        return {"payload": payload, "fields": len(payload)}

    def _stage_normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all scores to 0.0–1.0 range."""
        scores = payload.get("scores", {})
        normalized = {}
        for k, v in scores.items():
            if isinstance(v, (int, float)):
                normalized[k] = max(0.0, min(1.0, float(v)))
        payload["scores"] = normalized
        return {"normalized": payload, "score_count": len(normalized)}

    def _stage_post(self, payload: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Enrich with compliance summary and metadata."""
        compliance = getattr(result, "compliance_summary", None) or {}
        payload["compliance"] = compliance
        payload["data"] = getattr(result, "data", {}) or {}
        # Compute composite readiness
        scores = payload.get("scores", {})
        values = [v for v in scores.values() if isinstance(v, (int, float))]
        if values:
            payload["composite_score"] = round(sum(values) / len(values), 4)
        else:
            payload["composite_score"] = 0.0
        return {"enriched": payload}

    def _stage_assert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Final readiness gate."""
        composite = payload.get("composite_score", 0)
        confidence = payload.get("scores", {}).get("_confidence", 0.5)
        ready = (composite >= self.READINESS_THRESHOLD and
                 confidence >= self.CONFIDENCE_MINIMUM)
        return {
            "ready": ready,
            "composite": composite,
            "confidence": confidence,
            "threshold": self.READINESS_THRESHOLD,
        }
