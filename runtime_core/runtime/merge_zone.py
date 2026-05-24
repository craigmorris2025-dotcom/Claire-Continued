"""
Rule 3: Merge zone reconciles route outputs before validation

Version: 5.91.0
Module: src.claire.runtime.merge_zone
Architecture: LOCKED at v5.90.2
Stage: 23 â€” Market Positioning
Phase: portfolio
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

logger = logging.getLogger("claire.runtime")

# Stage constants
STAGE_23_ID = 23
STAGE_23_NAME = "Market Positioning"
STAGE_24_ID = 24
STAGE_24_NAME = "Moat & Differentiation"
STAGE_25_ID = 25
STAGE_25_NAME = "Business Model & Value Capture"
STAGE_26_ID = 26
STAGE_26_NAME = "Competitor Analysis"
STAGE_27_ID = 27
STAGE_27_NAME = "Portfolio Creation/Optimization"
STAGE_28_ID = 28
STAGE_28_NAME = "Acquirer Identification"
STAGE_29_ID = 29
STAGE_29_NAME = "Acquisition Fit & Rationale"
STAGE_30_ID = 30
STAGE_30_NAME = "Final Package Construction"

# I/O Contract â€” required output fields
OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class MergeZone:
    """
    Rule 3: Merge zone reconciles route outputs before validation

    Stage 23: Market Positioning
    Phase: portfolio
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.runtime.{type(self).__name__}"
        )

    def execute(self, stage_input: dict) -> dict:
        """
        Execute Stage 23: Market Positioning.

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
            f"Stage 23 (Market Positioning): executing"
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
            self.logger.error(f"Stage 23 failed: {e}")
            return self._build_output(
                status="failed",
                confidence=0.0,
                failure_reasons=[str(e)],
            )

    def _process(self, stage_input: dict) -> dict:
        return build_stage_payload(23, STAGE_23_NAME, stage_input)

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
            "stage_id": 23,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


