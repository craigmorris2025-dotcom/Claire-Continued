"""
Proof Binder — generates validation proof packages for audit and investor presentation

Version: 5.98.1
Module: src.claire.validation.proof_binder
Architecture: LOCKED at v5.90.2
Layer: 4 — Output & Validation System
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional


logger = logging.getLogger("claire.validation")


class ProofBinder:
    """
    Proof Binder.

    Purpose:
    - Convert validation evidence into a proof package
    - Summarize decision support, risks, evidence gaps, and audit status
    - Keep runtime safe if proof generation is incomplete
    """

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
            "stage_id": "proof_binder",
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": self._utc_now_iso(),
        }

    def bind(
        self,
        result: dict,
        validation: Optional[dict] = None,
        evidence_chain: Optional[list] = None,
        run_id: Optional[str] = None,
    ) -> dict:
        """
        Build a proof binder from a pipeline result and validation output.
        """
        if not isinstance(result, dict):
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=["result is not a dictionary"],
                metadata={"run_id": run_id},
            )

        validation = validation or result.get("validation", {})
        evidence_chain = evidence_chain or result.get("evidence_chain", [])

        scores = result.get("scores", {}) if isinstance(result.get("scores"), dict) else {}

        proof_confidence = self._calculate_proof_confidence(
            validation=validation,
            evidence_chain=evidence_chain,
            scores=scores,
        )

        status = "completed"
        if proof_confidence < 0.40:
            status = "weak_proof"
        elif proof_confidence < 0.60:
            status = "partial_proof"

        decision = result.get("decision_classification")
        breakthrough = result.get("breakthrough_classification")
        domain = result.get("domain")
        final_run_id = run_id or result.get("run_id")

        proof_package = {
            "run_id": final_run_id,
            "domain": domain,
            "decision_classification": decision,
            "breakthrough_classification": breakthrough,
            "proof_confidence": proof_confidence,
            "proof_status": status,
            "audit_ready": bool(validation.get("audit_ready")) if isinstance(validation, dict) else False,
            "validation_ready": bool(validation.get("validation_ready")) if isinstance(validation, dict) else False,
            "evidence_count": len(evidence_chain) if isinstance(evidence_chain, list) else 0,
            "memory_path": result.get("memory", {}).get("memory_path") if isinstance(result.get("memory"), dict) else None,
            "summary": self._build_summary(result, validation, evidence_chain, proof_confidence),
            "decision_support": self._build_decision_support(result, scores),
            "risk_register": self._build_risk_register(result),
            "evidence_gaps": self._build_evidence_gaps(result, validation),
            "audit_trail": self._build_audit_trail(result, validation, evidence_chain),
            "recommended_binder_artifacts": self._recommended_artifacts(result),
        }

        return self._build_output(
            status=status,
            confidence=proof_confidence,
            evidence=evidence_chain if isinstance(evidence_chain, list) else [],
            failure_reasons=[],
            payload=proof_package,
            metadata={
                "run_id": final_run_id,
                "binder_version": "5.98.1",
                "created_at": self._utc_now_iso(),
            },
        )

    def _calculate_proof_confidence(
        self,
        validation: dict,
        evidence_chain: list,
        scores: dict,
    ) -> float:
        validation_confidence = 0.0
        if isinstance(validation, dict):
            validation_confidence = float(validation.get("confidence") or 0.0)

        evidence_count_score = min(1.0, len(evidence_chain or []) / 10)

        score_candidates = [
            scores.get("_confidence"),
            scores.get("knowledge_quality_score"),
            scores.get("source_quality_score"),
            scores.get("coverage_score"),
            scores.get("portfolio_score"),
            scores.get("breakthrough_synthesis_score"),
        ]

        usable_scores = [float(s) for s in score_candidates if isinstance(s, (int, float))]
        score_confidence = sum(usable_scores) / len(usable_scores) if usable_scores else 0.45

        proof_confidence = (
            validation_confidence * 0.45
            + evidence_count_score * 0.25
            + score_confidence * 0.30
        )

        return round(max(0.0, min(1.0, proof_confidence)), 4)

    def _build_summary(
        self,
        result: dict,
        validation: dict,
        evidence_chain: list,
        proof_confidence: float,
    ) -> dict:
        return {
            "plain_english": (
                f"Run {result.get('run_id')} produced a "
                f"{result.get('decision_classification')} decision with "
                f"{result.get('breakthrough_classification')} breakthrough classification. "
                f"Proof confidence is {proof_confidence}."
            ),
            "validation_status": validation.get("status") if isinstance(validation, dict) else None,
            "validation_ready": validation.get("validation_ready") if isinstance(validation, dict) else None,
            "audit_ready": validation.get("audit_ready") if isinstance(validation, dict) else None,
            "evidence_sections": len(evidence_chain) if isinstance(evidence_chain, list) else 0,
        }

    def _build_decision_support(self, result: dict, scores: dict) -> dict:
        return {
            "decision": result.get("decision_classification"),
            "breakthrough": result.get("breakthrough_classification"),
            "domain": result.get("domain"),
            "primary_scores": {
                "confidence": scores.get("_confidence"),
                "portfolio_score": scores.get("portfolio_score"),
                "breakthrough_score": scores.get("breakthrough_score"),
                "opportunity_score": scores.get("opportunity_score"),
                "acquisition_score": scores.get("acquisition_score"),
                "knowledge_quality_score": scores.get("knowledge_quality_score"),
                "routing_confidence_score": scores.get("routing_confidence_score"),
                "evidence_signal_score": scores.get("evidence_signal_score"),
            },
            "acquirer_count": len(result.get("acquirer_matches", [])) if isinstance(result.get("acquirer_matches"), list) else 0,
        }

    def _build_risk_register(self, result: dict) -> list[dict]:
        risks = []

        for section_key in ["technical_feasibility", "productization_path", "breakthrough_synthesis"]:
            section = result.get(section_key)
            if not isinstance(section, dict):
                continue

            for risk_key in ["technical_risks", "launch_risks", "falsifiers"]:
                values = section.get(risk_key)
                if isinstance(values, list):
                    for item in values[:5]:
                        if isinstance(item, dict):
                            risks.append({
                                "source_section": section_key,
                                "type": risk_key,
                                "item": item,
                            })

        return risks[:15]

    def _build_evidence_gaps(self, result: dict, validation: dict) -> list[dict]:
        gaps = []

        opportunity = result.get("opportunity_discovery")
        if isinstance(opportunity, dict):
            for gap in opportunity.get("evidence_gaps", []) or []:
                if isinstance(gap, dict):
                    gaps.append({
                        "source_section": "opportunity_discovery",
                        **gap,
                    })

        if isinstance(validation, dict):
            for missing in validation.get("missing_sections", []) or []:
                gaps.append({
                    "source_section": "validation",
                    "gap": f"missing section: {missing}",
                    "priority": "medium",
                })

        return gaps[:20]

    def _build_audit_trail(
        self,
        result: dict,
        validation: dict,
        evidence_chain: list,
    ) -> dict:
        return {
            "run_id": result.get("run_id"),
            "intent_id": result.get("intent_id"),
            "executed_at": result.get("executed_at"),
            "runtime_trace": result.get("runtime_trace", {}),
            "validation_timestamp": validation.get("timestamp") if isinstance(validation, dict) else None,
            "evidence_chain_count": len(evidence_chain) if isinstance(evidence_chain, list) else 0,
            "memory_status": result.get("memory", {}).get("status") if isinstance(result.get("memory"), dict) else None,
            "memory_path": result.get("memory", {}).get("memory_path") if isinstance(result.get("memory"), dict) else None,
        }

    def _recommended_artifacts(self, result: dict) -> list[str]:
        artifacts = [
            "full_run_output_json",
            "evidence_chain_json",
            "proof_binder_summary",
            "risk_register",
            "validation_gap_report",
        ]

        if result.get("acquirer_matches"):
            artifacts.append("acquirer_match_report")

        if result.get("breakthrough_synthesis"):
            artifacts.append("breakthrough_validation_memo")

        if result.get("productization_path"):
            artifacts.append("pilot_readiness_packet")

        return artifacts