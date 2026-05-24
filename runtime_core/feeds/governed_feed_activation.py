"""Governed feed activation packets for connected and hybrid mode."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json
import uuid

from runtime_core.mode.switch_controller import ModeSwitchController
from runtime_core.governance.feed_activation_policy import FeedActivationPolicy


class GovernedFeedActivation:
    """Prepare auditable feed activation packets before live or offline scans."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.log_path = self.project_root / "data" / "governance" / "feed_activation_sessions.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.mode_switch = ModeSwitchController()
        self.feed_policy = FeedActivationPolicy()

    def prepare(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request = request or {}
        mode_decision = self.mode_switch.evaluate(request)
        feed_decision = mode_decision.get("feed_activation") or self.feed_policy.evaluate(request)
        packet = {
            "status": "blocked" if mode_decision.get("status") == "blocked" or feed_decision.get("decision") == "block" else "success",
            "activation_session_id": "feed_" + uuid.uuid4().hex[:12],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "requested_mode": mode_decision.get("requested_mode"),
            "effective_mode": mode_decision.get("effective_mode"),
            "market_universe": request.get("market_universe") or "custom_universe",
            "industry_domain": request.get("industry_domain") or "cross_sector",
            "source_category": feed_decision.get("source_category"),
            "connected_ingestion_allowed": bool(mode_decision.get("connected_ingestion_allowed")),
            "deterministic_fallback_allowed": bool(mode_decision.get("deterministic_fallback_allowed", True)),
            "source_urls": self._safe_urls(request.get("source_urls") or []),
            "mode_decision": mode_decision,
            "feed_activation": feed_decision,
            "next_action": self._next_action(mode_decision, feed_decision, request.get("source_urls") or []),
        }
        self.record(packet)
        return packet

    def status(self) -> Dict[str, Any]:
        recent = self.recent(limit=10)
        return {
            "status": "success",
            "activation_layer": "governed_feed_activation_v1",
            "session_count": recent.get("session_count", 0),
            "recent": recent.get("sessions", []),
            "purpose": "Prepare connected/hybrid feed scans with mode governance, source category, and deterministic fallback visible.",
        }

    def record(self, packet: Dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(packet, sort_keys=True, default=str) + "\n")

    def recent(self, limit: int = 20) -> Dict[str, Any]:
        if not self.log_path.exists():
            return {"status": "success", "session_count": 0, "sessions": []}
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        sessions = []
        for line in lines[-limit:]:
            try:
                sessions.append(json.loads(line))
            except Exception:
                continue
        sessions.reverse()
        return {"status": "success", "session_count": len(lines), "sessions": sessions}

    def _safe_urls(self, urls: List[Any]) -> List[str]:
        safe = []
        for url in urls[:10]:
            text = str(url).strip()
            if text.startswith(("https://", "http://")):
                safe.append(text)
        return safe

    def _next_action(self, mode_decision: Dict[str, Any], feed_decision: Dict[str, Any], urls: List[Any]) -> str:
        if mode_decision.get("status") == "blocked" or feed_decision.get("decision") == "block":
            return "blocked_by_governance"
        if not mode_decision.get("connected_ingestion_allowed"):
            return "use_deterministic_fallback"
        if not urls:
            return "provide_public_source_urls_or_use_offline_resolver"
        return "scan_safe_public_metadata"


__all__ = ["GovernedFeedActivation"]
