"""
Mode Guard — feed/mode boundary utilities for Claire.

v5.43:
- Keeps deterministic, connected, and hybrid boundaries explicit.
"""

from __future__ import annotations

from typing import Any, Dict


class ModeGuard:
    """Utility layer for execution/intelligence mode boundaries."""

    def normalize(self, mode: str | None) -> str:
        mode = mode or "deterministic"
        if mode == "connected_intelligence":
            mode = "connected"
        return mode if mode in {"deterministic", "connected", "hybrid"} else "deterministic"

    def boundary(self, mode: str | None) -> Dict[str, Any]:
        mode = self.normalize(mode)
        if mode == "deterministic":
            return {
                "mode": mode,
                "external_ingestion_allowed": False,
                "deterministic_fallback_allowed": True,
                "description": "Offline, reproducible, patent-safe mode. No external feeds.",
            }
        if mode == "connected":
            return {
                "mode": mode,
                "external_ingestion_allowed": True,
                "deterministic_fallback_allowed": True,
                "description": "Connected intelligence mode. External feeds require activation policy and audit logging.",
            }
        return {
            "mode": "hybrid",
            "external_ingestion_allowed": True,
            "deterministic_fallback_allowed": True,
            "description": "Hybrid mode. Connected feeds require activation policy, audit logging, and deterministic fusion boundary.",
        }
