"""
Claire Syntalion v17.92
Search Bar Session State
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
import json
from pathlib import Path


class SearchBarSessionState:
    def __init__(
        self,
        session_log_path: str | Path = "data/search/search_bar_session_log.json",
    ) -> None:
        self.session_log_path = Path(session_log_path)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _read_json(self) -> Dict[str, Any]:
        if not self.session_log_path.exists():
            return {
                "version": "v17.92",
                "sessions": []
            }

        try:
            return json.loads(self.session_log_path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "version": "v17.92",
                "sessions": []
            }

    def _write_json(self, payload: Dict[str, Any]) -> None:
        self.session_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_log_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def append_event(
        self,
        query: str,
        resolved_mode: str,
        status: str,
    ) -> Dict[str, Any]:
        payload = self._read_json()

        event = {
            "timestamp": self._utc_now(),
            "query": query,
            "resolved_mode": resolved_mode,
            "status": status,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
        }

        payload.setdefault("sessions", []).append(event)
        payload["version"] = "v17.92"

        self._write_json(payload)

        return event

    def get_session_history(self) -> List[Dict[str, Any]]:
        payload = self._read_json()
        sessions = payload.get("sessions", [])

        if not isinstance(sessions, list):
            return []

        return sessions
