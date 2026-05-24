"""
Market data feed integration for portfolio decisions

Version: 6.1.0
Module: src.claire.portfolio.market_feed
Architecture: LOCKED at v5.90.2
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("claire.portfolio")

class MarketFeed:
    """Market data feed integration for portfolio decisions"""

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.portfolio.{type(self).__name__}"
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
