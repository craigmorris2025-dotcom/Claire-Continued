"""
Live portfolio optimizer with real-time market integration

Version: 6.1.0
Module: src.claire.portfolio.live_optimizer
Architecture: LOCKED at v5.90.2
Stage: 27 â€” Portfolio Creation/Optimization
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

logger = logging.getLogger("claire.portfolio")

# Stage constants
STAGE_27_ID = 27
STAGE_27_NAME = "Portfolio Creation/Optimization"

OUTPUT_CONTRACT_FIELDS = ['stage_id', 'status', 'confidence', 'evidence', 'failure_reasons', 'payload', 'metadata', 'timestamp']

class LiveOptimizer:
    """Live portfolio optimizer with real-time market integration"""

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.portfolio.{type(self).__name__}"
        )

    def execute(self, stage_input: dict) -> dict:
        """Execute Stage 27: Portfolio Creation/Optimization."""
        self._validate_input(stage_input)
        self.logger.info(f"Stage 27 (Portfolio Creation/Optimization): executing")
        try:
            payload = self._process(stage_input)
            return self._build_output(
                status="completed",
                confidence=float(payload.get("confidence", 0.5)),
                evidence=payload.get("evidence", []),
                payload=payload,
            )
        except Exception as e:
            self.logger.error(f"Stage 27 failed: {e}")
            return self._build_output(status="failed", confidence=0.0, failure_reasons=[str(e)])

    def _process(self, stage_input: dict) -> dict:
        return build_stage_payload(27, STAGE_27_NAME, stage_input)

    def _validate_input(self, stage_input: dict):
        """Validate input matches the I/O contract."""
        required = ['stage_id', 'source_stage', 'payload', 'metadata', 'timestamp']
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(f"Input contract violation â€” missing fields: {missing}")

    def _build_output(self, status='completed', confidence=0.0, evidence=None, failure_reasons=None, payload=None, metadata=None) -> dict:
        """Build a contract-compliant output dict."""
        return {
            "stage_id": 27,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

