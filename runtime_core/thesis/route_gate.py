"""
Route Selection Gate â€” evaluates thesis output to select primary route

Version: 5.93.0
Module: src.claire.thesis.route_gate
Architecture: LOCKED at v5.90.2
Stage: 10 â€” Insight/Thesis Structuring
Phase: analysis
Layer: 3 â€” Route Selection System
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

logger = logging.getLogger("claire.thesis")

# Stage constants
STAGE_10_ID = 10
STAGE_10_NAME = "Insight/Thesis Structuring"

# I/O Contract â€” required output fields
OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class RouteGate:
    """
    Route Selection Gate â€” evaluates thesis output to select primary route

    Stage 10: Insight/Thesis Structuring
    Phase: analysis
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.thesis.{type(self).__name__}"
        )

    def execute(self, stage_input: dict) -> dict:
        """
        Execute Stage 10: Insight/Thesis Structuring.

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
            f"Stage 10 (Insight/Thesis Structuring): executing"
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
            self.logger.error(f"Stage 10 failed: {e}")
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=[str(e)],
            )

    def _process(self, stage_input: dict) -> dict:
        return build_stage_payload(10, STAGE_10_NAME, stage_input)

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
            "stage_id": 10,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


