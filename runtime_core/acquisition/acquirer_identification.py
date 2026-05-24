"""
Acquirer Identification — potential acquirer discovery and profiling

Version: 5.97.0
Module: src.claire.acquisition.acquirer_identification
Architecture: LOCKED at v5.90.2
Stage: 28 — Acquirer Identification
Phase: acquisition
Route: Acquisition Route (STRATEGIC)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from runtime_core.acquirers.matcher import AcquirerMatcher

# Runtime enforcement imports
# from claire.runtime import RuntimeEnforcer
# from claire.runtime.models import StageOutput

logger = logging.getLogger("claire.acquisition")

# Stage constants
STAGE_28_ID = 28
STAGE_28_NAME = "Acquirer Identification"

# I/O Contract — required output fields
OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class AcquirerIdentification:
    """
    Acquirer Identification — potential acquirer discovery and profiling

    Stage 28: Acquirer Identification
    Phase: acquisition
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.acquisition.{type(self).__name__}"
        )
        self.matcher = AcquirerMatcher()

    def execute(self, stage_input: dict) -> dict:
        """
        Execute Stage 28: Acquirer Identification.

        Input Contract:
            - stage_id
            - source_stage
            - payload
            - metadata
            - timestamp

        Output Contract:
            - stage_id
            - status
            - confidence
            - evidence
            - failure_reasons
            - payload
            - metadata
            - timestamp

        Returns:
            dict matching the output contract schema
        """
        # Validate input contract
        self._validate_input(stage_input)

        self.logger.info(
            f"Stage 28 (Acquirer Identification): executing"
        )

        try:
            payload = self._process(stage_input)
            matches = payload.get("acquirer_matches", [])
            confidence = 0.0
            if matches:
                confidence = min(0.95, max(float(item.get("fit", 0.0)) for item in matches))

            return self._build_output(
                status="completed",
                confidence=confidence,
                evidence=payload.get("evidence", []),
                payload=payload,
            )

        except Exception as e:
            self.logger.error(f"Stage 28 failed: {e}")
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=[str(e)],
            )

    def _process(self, stage_input: dict) -> dict:
        """Identify strategic acquirer candidates from portfolio/acquisition context."""
        payload = stage_input.get("payload") if isinstance(stage_input.get("payload"), dict) else {}
        context = _extract_acquirer_context(payload)
        matches = self.matcher.match(context, top_n=int(payload.get("top_n") or 5))
        enriched = []
        for match in matches:
            category = _acquirer_category(match)
            enriched.append(
                {
                    **match,
                    "acquirer_category": category,
                    "strategic_fit_rationale": _strategic_fit_rationale(match, context),
                    "capability_gap_narrative": _capability_gap_narrative(match, context),
                    "timing_signal": _timing_signal(match, context),
                    "source": "claire.acquirers.dataset",
                    "review_state": "operator_review_required",
                }
            )
        return {
            "status": "acquirer_candidates_identified" if enriched else "no_acquirer_candidates",
            "context": context,
            "acquirer_matches": enriched,
            "acquirer_count": len(enriched),
            "evidence": [
                {
                    "evidence_id": "stage_28_acquirer_dataset",
                    "source": "claire.acquirers.dataset",
                    "summary": "Static strategic acquirer profiles matched against portfolio/acquisition context.",
                }
            ],
            "runtime_truth_write": "blocked",
            "manual_review_required": True,
        }

    def _validate_input(self, stage_input: dict):
        """Validate input matches the I/O contract."""
        required = ['stage_id', 'source_stage', 'payload', 'metadata', 'timestamp']
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(
                f"Input contract violation — missing fields: {missing}"
            )

    def _build_output(
        self,
        status: str = "completed",
        confidence: float = 0.0,
        evidence: list = None,
        failure_reasons: list = None,
        payload: dict = None,
        metadata: dict = None,
    ) -> dict:
        """Build a contract-compliant output dict."""
        return {
            "stage_id": 28,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " ".join(_as_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_text(item) for item in value.values())
    return str(value)


def _keyword_list(*values: Any) -> list[str]:
    text = " ".join(_as_text(value).lower() for value in values)
    tokens = []
    aliases = {
        "artificial": "ai",
        "intelligence": "ai",
        "autonomy": "autonomous",
        "aerospace": "aerospace",
        "defense": "defense",
        "cloud": "cloud",
        "platform": "platform",
        "data": "data",
        "search": "search",
        "logistics": "logistics",
    }
    for raw in text.replace("/", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum())
        if not token:
            continue
        mapped = aliases.get(token, token)
        if mapped not in tokens:
            tokens.append(mapped)
    return tokens[:12]


def _infer_domain(payload: dict[str, Any], keywords: list[str]) -> str:
    explicit = str(
        payload.get("domain")
        or payload.get("sector")
        or payload.get("market")
        or payload.get("industry")
        or ""
    ).strip().lower()
    if explicit:
        if "defense" in explicit or "aerospace" in explicit:
            return "defense"
        if "tech" in explicit or "software" in explicit or "ai" in explicit:
            return "technology"
        return explicit
    if {"defense", "autonomous", "aerospace"}.intersection(keywords):
        return "defense"
    return "technology"


def _extract_acquirer_context(payload: dict[str, Any]) -> dict[str, Any]:
    thesis = payload.get("portfolio_thesis") or payload.get("thesis") or payload.get("summary")
    category = payload.get("category") or payload.get("candidate_type") or payload.get("opportunity_category")
    keywords = _keyword_list(
        thesis,
        category,
        payload.get("keywords", []),
        payload.get("trend"),
        payload.get("candidate"),
        payload.get("portfolio_candidate"),
    )
    domain = _infer_domain(payload, keywords)
    return {
        "domain": domain,
        "keywords": keywords,
        "thesis": _as_text(thesis)[:500],
        "category": _as_text(category)[:160],
        "portfolio_candidate_id": payload.get("candidate_id") or payload.get("portfolio_candidate_id"),
        "source_stage": payload.get("source_stage") or payload.get("route") or "portfolio_output",
    }


def _acquirer_category(match: dict[str, Any]) -> str:
    focus = {str(item).lower() for item in match.get("focus", [])}
    if {"defense", "aerospace", "autonomous"}.intersection(focus):
        return "strategic_defense_prime"
    if {"cloud", "platform", "ai", "data"}.intersection(focus):
        return "strategic_technology_platform"
    return "strategic_corporate_acquirer"


def _strategic_fit_rationale(match: dict[str, Any], context: dict[str, Any]) -> str:
    aligned = sorted(set(context.get("keywords", [])).intersection({str(item).lower() for item in match.get("focus", [])}))
    if aligned:
        return f"{match.get('name')} aligns with {', '.join(aligned)} signals in the candidate context."
    return f"{match.get('name')} is a broad strategic acquirer candidate for the {context.get('domain')} domain."


def _capability_gap_narrative(match: dict[str, Any], context: dict[str, Any]) -> str:
    category = context.get("category") or "the candidate capability"
    return (
        f"{match.get('name')} could use {category} to strengthen its {context.get('domain')} portfolio, "
        "close product or platform gaps, or accelerate an internal build-vs-buy decision."
    )


def _timing_signal(match: dict[str, Any], context: dict[str, Any]) -> str:
    fit = float(match.get("fit", 0.0) or 0.0)
    if fit >= 0.75:
        return "near_term_review_window"
    if fit >= 0.55:
        return "watchlist_timing_window"
    return "early_signal_only"
