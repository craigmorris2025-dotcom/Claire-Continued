"""
Mode Controller — Deterministic / Connected / Hybrid.
Gates capabilities based on the active operating mode.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("claire.mode")

MODE_CAPS = {
    "deterministic": sorted([
        "nlp", "scoring", "engines", "persistence", "acquirer_matching",
        "score_calibration", "compliance", "export",
    ]),
    "connected": sorted([
        "nlp", "scoring", "engines", "persistence", "acquirer_matching",
        "score_calibration", "compliance", "export",
        "market_connector", "patent_connector", "financial_connector",
    ]),
    "hybrid": sorted([
        "nlp", "scoring", "engines", "persistence", "acquirer_matching",
        "score_calibration", "compliance", "export",
        "market_connector", "patent_connector", "financial_connector",
        "pattern_recognition", "fettio", "desking", "predictive_analytics",
    ]),
}

MODE_DESCRIPTIONS = {
    "deterministic": "Air-gapped, patent-safe, reproducible. Zero external data.",
    "connected": "Live data ingestion via connectors. Real-time scanning.",
    "hybrid": "Dual-core. Both engines active. Maximum capability.",
}


class ModeController:
    """Controls feature gating based on operating mode."""

    def __init__(self, mode: str = "deterministic"):
        if mode not in MODE_CAPS:
            mode = "deterministic"
        self._mode = mode

    @property
    def current_mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str):
        if mode in MODE_CAPS:
            self._mode = mode
            logger.info(f"Mode set to: {self._mode}")

    def is_allowed(self, capability: str) -> bool:
        return capability in MODE_CAPS.get(self._mode, [])

    def get_capabilities(self, mode: str = None) -> List[str]:
        m = mode or self._mode
        return MODE_CAPS.get(m, [])

    def get_status(self) -> Dict[str, Any]:
        caps = MODE_CAPS.get(self._mode, [])
        return {"mode": self._mode, "capabilities": caps, "count": len(caps)}

    def get_all_modes(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": mode,
                "capabilities": caps,
                "description": MODE_DESCRIPTIONS.get(mode, ""),
            }
            for mode, caps in MODE_CAPS.items()
        ]
