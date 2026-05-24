"""
Gap Qualification â€” validate gap significance and exploitability

Version: 5.94.0
Module: src.claire.breakthrough.gap_qualification
Architecture: LOCKED at v5.90.2
Stage: 12 â€” Gap Qualification
Phase: breakthrough
Route: Breakthrough Route (CONDITIONAL)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Optional

from runtime_core.runtime.stage_logic import build_stage_payload

# Runtime enforcement imports
# from claire.runtime import RuntimeEnforcer
# from claire.runtime.models import StageOutput

logger = logging.getLogger("claire.breakthrough")

# Stage constants
STAGE_12_ID = 12
STAGE_12_NAME = "Gap Qualification"

# I/O Contract â€” required output fields
OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class GapQualification:
    """
    Gap Qualification â€” validate gap significance and exploitability

    Stage 12: Gap Qualification
    Phase: breakthrough
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.breakthrough.{type(self).__name__}"
        )

    def execute(self, stage_input: dict) -> dict:
        """
        Execute Stage 12: Gap Qualification.

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
            f"Stage 12 (Gap Qualification): executing"
        )

        try:
            payload = self._process(stage_input)

            return self._build_output(
                status="completed",
                confidence=float(payload.get("confidence", 0.5)),
                evidence=payload.get("evidence", []),
                payload=payload,
            )

        except Exception as e:
            self.logger.error(f"Stage 12 failed: {e}")
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=[str(e)],
            )

    def _process(self, stage_input: dict) -> dict:
        return build_stage_payload(12, STAGE_12_NAME, stage_input)

    def _validate_input(self, stage_input: dict):
        """Validate input matches the I/O contract."""
        required = ['stage_id', 'source_stage', 'payload', 'metadata', 'timestamp']
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(
                f"Input contract violation â€” missing fields: {missing}"
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
            "stage_id": 12,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


