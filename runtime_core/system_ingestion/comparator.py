"""
System comparator — benchmark against Claire's own architecture

Version: 7.0.0
Module: src.claire.system_ingestion.comparator
Architecture: LOCKED at v5.90.2
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("claire.system_ingestion")

class Comparator:
    """System comparator — benchmark against Claire's own architecture"""

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.system_ingestion.{type(self).__name__}"
        )

    def _validate_input(self, stage_input: dict):
        """Validate input matches the I/O contract."""
        required = ['stage_id', 'source_stage', 'payload', 'metadata', 'timestamp']
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(f"Input contract violation — missing fields: {missing}")

    def _build_output(self, status='completed', confidence=0.0, evidence=None, failure_reasons=None, payload=None, metadata=None) -> dict:
        """Build a contract-compliant output dict."""
        return {
            "stage_id": None,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def compare(self, analysis: dict[str, Any] | None, target_capabilities: list[str] | None = None) -> dict[str, Any]:
        """Compare an ingested system analysis against deterministic redesign targets."""
        analysis = analysis or {}
        components = analysis.get("components") if isinstance(analysis.get("components"), list) else []
        gaps = analysis.get("gaps") if isinstance(analysis.get("gaps"), list) else []
        targets = target_capabilities or [
            "traceable_ingestion",
            "governed_validation",
            "route_aware_orchestration",
            "dashboard_review",
            "memory_feedback_gate",
        ]
        component_ids = {str(item.get("id")) for item in components if isinstance(item, dict)}
        gap_ids = {str(item.get("id")) for item in gaps if isinstance(item, dict)}
        matched_targets = [target for target in targets if self._target_matches(target, component_ids, gap_ids)]
        missing_targets = [target for target in targets if target not in matched_targets]
        redesign_priority = "high" if gap_ids else "medium" if missing_targets else "low"
        score = round(max(0.0, min(1.0, (len(matched_targets) / max(1, len(targets))) - len(gap_ids) * 0.04)), 4)
        return {
            "status": "success",
            "comparison_type": "system_redesign_readiness",
            "matched_targets": matched_targets,
            "missing_targets": missing_targets,
            "gap_ids": sorted(gap_ids),
            "redesign_priority": redesign_priority,
            "redesign_recommendations": self._recommendations(missing_targets, gap_ids),
            "score": score,
        }

    def _target_matches(self, target: str, component_ids: set[str], gap_ids: set[str]) -> bool:
        mapping = {
            "traceable_ingestion": "ingestion" in component_ids and "missing_lineage" not in gap_ids,
            "governed_validation": "governance" in component_ids and "weak_validation" not in gap_ids,
            "route_aware_orchestration": "routing" in component_ids,
            "dashboard_review": "interface" in component_ids,
            "memory_feedback_gate": "storage" in component_ids and "missing_lineage" not in gap_ids,
        }
        return bool(mapping.get(target, False))

    def _recommendations(self, missing_targets: list[str], gap_ids: set[str]) -> list[str]:
        recommendations = [f"add_{target}" for target in missing_targets]
        recommendations.extend(f"resolve_{gap_id}" for gap_id in sorted(gap_ids))
        return recommendations or ["maintain_current_architecture_controls"]
