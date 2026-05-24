"""Mode payload isolation helpers.

The mode controller decides what may happen. This helper shapes payloads so
downstream engines receive only the parts appropriate for the effective mode.
"""

from __future__ import annotations

from typing import Any, Dict


class ModeIsolationLayer:
    """Create downstream-safe payloads from a governed mode decision."""

    def isolate(self, payload: Dict[str, Any], mode_decision: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(payload or {})
        effective_mode = mode_decision.get("effective_mode") or "deterministic"
        payload["execution_mode"] = effective_mode if effective_mode != "blocked" else "deterministic"
        payload["mode_decision"] = mode_decision

        if effective_mode == "deterministic":
            payload.pop("connected_feed_payload", None)
            payload["_connected_ingestion_allowed"] = False
            payload["_hybrid_fusion_allowed"] = False
        elif effective_mode == "connected":
            payload["_connected_ingestion_allowed"] = bool(mode_decision.get("connected_ingestion_allowed"))
            payload["_hybrid_fusion_allowed"] = False
        elif effective_mode == "hybrid":
            payload["_connected_ingestion_allowed"] = bool(mode_decision.get("connected_ingestion_allowed"))
            payload["_hybrid_fusion_allowed"] = True

        return payload
