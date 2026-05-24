"""
Acquisition Fit & Rationale — strategic fit scoring and rationale generation

Version: 5.97.0
Module: src.claire.acquisition.fit_rationale
Architecture: LOCKED at v5.90.2
Stage: 29 — Acquisition Fit & Rationale
Phase: acquisition
Route: Acquisition Route (STRATEGIC)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

# Runtime enforcement imports
# from claire.runtime import RuntimeEnforcer
# from claire.runtime.models import StageOutput

logger = logging.getLogger("claire.acquisition")

# Stage constants
STAGE_29_ID = 29
STAGE_29_NAME = "Acquisition Fit & Rationale"

# I/O Contract — required output fields
OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class FitRationale:
    """
    Acquisition Fit & Rationale — strategic fit scoring and rationale generation

    Stage 29: Acquisition Fit & Rationale
    Phase: acquisition
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.acquisition.{type(self).__name__}"
        )

    def execute(self, stage_input: dict) -> dict:
        """
        Execute Stage 29: Acquisition Fit & Rationale.

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
            f"Stage 29 (Acquisition Fit & Rationale): executing"
        )

        try:
            payload = self._process(stage_input)
            fit_items = payload.get("fit_rationales", [])
            confidence = 0.0
            if fit_items:
                confidence = min(0.95, max(float(item.get("fit_score", 0.0)) for item in fit_items))

            return self._build_output(
                status="completed",
                confidence=confidence,
                evidence=payload.get("evidence", []),
                payload=payload,
            )

        except Exception as e:
            self.logger.error(f"Stage 29 failed: {e}")
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=[str(e)],
            )

    def _process(self, stage_input: dict) -> dict:
        """Generate acquisition fit rationale from Stage 28 acquirer matches."""
        payload = stage_input.get("payload") if isinstance(stage_input.get("payload"), dict) else {}
        matches = payload.get("acquirer_matches") if isinstance(payload.get("acquirer_matches"), list) else []
        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        fit_rationales = []
        for match in matches:
            if not isinstance(match, dict):
                continue
            fit_score = float(match.get("fit", 0.0) or 0.0)
            fit_rationales.append(
                {
                    "name": match.get("name"),
                    "ticker": match.get("ticker"),
                    "fit_score": round(max(0.0, min(1.0, fit_score)), 4),
                    "acquirer_category": match.get("acquirer_category") or _acquirer_category(match),
                    "strategic_fit_rationale": match.get("strategic_fit_rationale") or _strategic_fit_rationale(match, context),
                    "capability_gap_narrative": match.get("capability_gap_narrative") or _capability_gap_narrative(match, context),
                    "timing_signal": match.get("timing_signal") or _timing_signal(fit_score),
                    "deal_readiness": _deal_readiness(fit_score),
                    "recommended_operator_action": "review_acquisition_fit" if fit_score >= 0.55 else "keep_on_watchlist",
                    "runtime_truth_write": "blocked",
                }
            )
        fit_rationales.sort(key=lambda item: item["fit_score"], reverse=True)
        return {
            "status": "acquisition_fit_ready" if fit_rationales else "no_acquisition_fit_available",
            "context": context,
            "fit_rationales": fit_rationales,
            "top_fit": fit_rationales[0] if fit_rationales else None,
            "fit_count": len(fit_rationales),
            "evidence": [
                {
                    "evidence_id": "stage_29_acquisition_fit",
                    "source": "stage_28_acquirer_identification",
                    "summary": "Fit rationale generated from identified acquirer candidates and candidate context.",
                }
            ],
            "manual_review_required": True,
            "runtime_truth_write": "blocked",
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
            "stage_id": 29,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def _acquirer_category(match: dict[str, Any]) -> str:
    focus = {str(item).lower() for item in match.get("focus", [])}
    if {"defense", "aerospace", "autonomous"}.intersection(focus):
        return "strategic_defense_prime"
    if {"cloud", "platform", "ai", "data"}.intersection(focus):
        return "strategic_technology_platform"
    return "strategic_corporate_acquirer"


def _strategic_fit_rationale(match: dict[str, Any], context: dict[str, Any]) -> str:
    return (
        f"{match.get('name')} has a strategic fit score of {match.get('fit', 0.0)} "
        f"against the {context.get('domain', 'target')} opportunity context."
    )


def _capability_gap_narrative(match: dict[str, Any], context: dict[str, Any]) -> str:
    category = context.get("category") or "candidate capability"
    return (
        f"The {category} could fill a capability, product, or platform gap for {match.get('name')} "
        "if operator review confirms evidence strength and timing."
    )


def _timing_signal(fit_score: float) -> str:
    if fit_score >= 0.75:
        return "near_term_review_window"
    if fit_score >= 0.55:
        return "watchlist_timing_window"
    return "early_signal_only"


def _deal_readiness(fit_score: float) -> str:
    if fit_score >= 0.75:
        return "package_review_candidate"
    if fit_score >= 0.55:
        return "strategic_watchlist"
    return "needs_more_evidence"
