"""Legacy engine base class used by older tests."""

from __future__ import annotations

from typing import Any, Dict


class BaseEngine:
    def __init__(self, key: str, phase: str):
        self.key = key
        self.phase = phase

    def get_phase(self) -> str:
        return self.phase

    def process(self, payload: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "engine": self.key,
            "phase": self.phase,
            "input_present": bool(payload),
        }
