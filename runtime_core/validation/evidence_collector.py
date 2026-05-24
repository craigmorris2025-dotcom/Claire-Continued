"""
Evidence Collector — gathers and chains evidence across lifecycle stages

Version: 5.98.1
Module: src.claire.validation.evidence_collector
Architecture: LOCKED at v5.90.2
Layer: 4 — Output & Validation System
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional


logger = logging.getLogger("claire.validation")


class EvidenceCollector:
    """
    Evidence Collector.

    Purpose:
    - Extract evidence-bearing sections from a pipeline result
    - Build a lightweight validation evidence chain
    - Avoid blocking runtime if evidence is incomplete
    """

    EVIDENCE_KEYS = [
        "knowledge_ingestion",
        "signal_extraction",
        "market_gap",
        "trend_discovery",
        "thesis_formation",
        "opportunity_discovery",
        "breakthrough_synthesis",
        "technical_feasibility",
        "productization_path",
        "trend_trajectory",
        "market_formation",
        "acquirer_matches",
        "scores",
    ]

    def __init__(self):
        self.logger = logging.getLogger(f"claire.validation.{type(self).__name__}")

    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_input(self, stage_input: dict):
        required = ["stage_id", "source_stage", "payload", "metadata", "timestamp"]
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(f"Input contract violation — missing fields: {missing}")

    def _build_output(
        self,
        status: str = "completed",
        confidence: float = 0.0,
        evidence: list | None = None,
        failure_reasons: list | None = None,
        payload: dict | None = None,
        metadata: dict | None = None,
    ) -> dict:
        return {
            "stage_id": "evidence_collector",
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": self._utc_now_iso(),
        }

    def collect(self, result: dict, run_id: Optional[str] = None) -> dict:
        """
        Collect evidence from a full pipeline result.
        """
        if not isinstance(result, dict):
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=["result is not a dictionary"],
                metadata={"run_id": run_id},
            )

        evidence_items = []
        missing_sections = []

        for key in self.EVIDENCE_KEYS:
            value = result.get(key)

            if value is None:
                missing_sections.append(key)
                continue

            evidence_items.append(
                {
                    "section": key,
                    "present": True,
                    "evidence_type": self._classify_evidence_type(key, value),
                    "summary": self._summarize_section(key, value),
                    "confidence": self._extract_confidence(value),
                }
            )

        scores = result.get("scores", {}) if isinstance(result.get("scores"), dict) else {}

        evidence_strength = self._calculate_evidence_strength(
            evidence_items=evidence_items,
            scores=scores,
            missing_sections=missing_sections,
        )

        status = "completed"
        if evidence_strength < 0.35:
            status = "weak_evidence"
        elif evidence_strength < 0.55:
            status = "partial_evidence"

        return self._build_output(
            status=status,
            confidence=evidence_strength,
            evidence=evidence_items,
            failure_reasons=[],
            payload={
                "run_id": run_id or result.get("run_id"),
                "evidence_count": len(evidence_items),
                "missing_sections": missing_sections,
                "evidence_strength": evidence_strength,
                "validation_ready": evidence_strength >= 0.55,
                "audit_ready": evidence_strength >= 0.70,
            },
            metadata={
                "run_id": run_id or result.get("run_id"),
                "collector_version": "5.98.1",
                "created_at": self._utc_now_iso(),
            },
        )

    def _classify_evidence_type(self, key: str, value: Any) -> str:
        if key == "scores":
            return "quantitative_scores"
        if key == "acquirer_matches":
            return "strategic_matching"
        if isinstance(value, dict) and "evidence_signals" in value:
            return "structured_evidence_signals"
        if isinstance(value, dict) and "confidence" in value:
            return "confidence_bearing_section"
        if isinstance(value, dict):
            return "structured_section"
        if isinstance(value, list):
            return "list_section"
        return "raw_section"

    def _summarize_section(self, key: str, value: Any) -> dict:
        if isinstance(value, dict):
            return {
                "status": value.get("status"),
                "domain": value.get("domain"),
                "sector": value.get("sector") or value.get("dominant_sector"),
                "confidence": value.get("confidence"),
                "has_evidence_signals": "evidence_signals" in value,
                "top_level_keys": list(value.keys())[:12],
            }

        if isinstance(value, list):
            return {
                "item_count": len(value),
                "sample_type": type(value[0]).__name__ if value else None,
            }

        return {
            "value_type": type(value).__name__,
            "preview": str(value)[:240],
        }

    def _extract_confidence(self, value: Any) -> Optional[float]:
        if isinstance(value, dict):
            confidence = value.get("confidence")
            if isinstance(confidence, (int, float)):
                return max(0.0, min(1.0, float(confidence)))

            score = value.get("score")
            if isinstance(score, (int, float)):
                return max(0.0, min(1.0, float(score)))

        return None

    def _calculate_evidence_strength(
        self,
        evidence_items: list[dict],
        scores: dict,
        missing_sections: list[str],
    ) -> float:
        section_coverage = len(evidence_items) / max(1, len(self.EVIDENCE_KEYS))

        confidence_values = [
            item["confidence"]
            for item in evidence_items
            if isinstance(item.get("confidence"), (int, float))
        ]

        avg_confidence = (
            sum(confidence_values) / len(confidence_values)
            if confidence_values
            else 0.45
        )

        score_quality = 0.0
        if scores:
            score_candidates = [
                scores.get("knowledge_quality_score"),
                scores.get("source_quality_score"),
                scores.get("coverage_score"),
                scores.get("_confidence"),
                scores.get("portfolio_score"),
                scores.get("breakthrough_synthesis_score"),
            ]
            usable_scores = [
                float(s)
                for s in score_candidates
                if isinstance(s, (int, float))
            ]
            score_quality = (
                sum(usable_scores) / len(usable_scores)
                if usable_scores
                else 0.45
            )

        missing_penalty = min(0.25, len(missing_sections) * 0.015)

        strength = (
            section_coverage * 0.35
            + avg_confidence * 0.35
            + score_quality * 0.30
            - missing_penalty
        )

        return round(max(0.0, min(1.0, strength)), 4)