"""Governed mode switching for Claire dashboard and connected workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid

from claire.governance.feed_activation_policy import FeedActivationPolicy
from claire.governance.redline_classifier import RedlineClassifier


@dataclass(frozen=True)
class ModeProfile:
    mode: str
    name: str
    connected_ingestion: str
    deterministic_core: str
    hybrid_fusion: str
    export_posture: str
    safety_posture: str


class ModeSwitchController:
    """Central source for deterministic, connected, and hybrid mode decisions."""

    def __init__(self) -> None:
        self.feed_policy = FeedActivationPolicy()
        self.redlines = RedlineClassifier()

    def status(self) -> Dict[str, Any]:
        profiles = [asdict(profile) for profile in self._profiles()]
        return {
            "status": "success",
            "mode_layer": "ready",
            "controller": "mode_switch_controller_v1",
            "default_mode": "deterministic",
            "supported_modes": [profile["mode"] for profile in profiles],
            "profiles": profiles,
            "rules": [
                "deterministic never performs connected ingestion",
                "connected requires feed activation approval before ingestion",
                "hybrid keeps deterministic core active and fuses safe connected context",
                "blocked governance decisions prevent launch",
                "review decisions preserve deterministic fallback",
            ],
        }

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request = request or {}
        requested_mode = self.normalize(request.get("execution_mode") or request.get("mode"))
        text = request.get("raw_input") or request.get("signal") or request.get("text") or ""

        governance = self.redlines.classify(text, {
            "execution_mode": requested_mode,
            "market_universe": request.get("market_universe"),
            "industry_domain": request.get("industry_domain"),
            "buyer_segment": request.get("buyer_segment"),
            "objective": request.get("objective"),
            "workflow": request.get("workflow"),
        })
        feed_activation = self.feed_policy.evaluate({**request, "execution_mode": requested_mode})

        effective_mode = requested_mode
        connected_allowed = bool(feed_activation.get("connected_ingestion_allowed"))
        deterministic_fallback = bool(feed_activation.get("deterministic_fallback_allowed", True))
        hard_block = governance.get("decision") == "block" or feed_activation.get("decision") == "block"
        warnings: List[str] = []

        if hard_block:
            effective_mode = "blocked"
            warnings.append("Governance hard stop blocks this launch.")
        elif requested_mode in {"connected", "hybrid"} and not connected_allowed:
            effective_mode = "deterministic"
            warnings.append("Connected ingestion is not approved; deterministic fallback remains active.")
        elif requested_mode == "hybrid" and connected_allowed:
            effective_mode = "hybrid"
        elif requested_mode == "connected" and connected_allowed:
            effective_mode = "connected"

        return {
            "mode_decision_id": "mode_" + uuid.uuid4().hex[:12],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "blocked" if hard_block else "success",
            "requested_mode": requested_mode,
            "effective_mode": effective_mode,
            "connected_ingestion_allowed": connected_allowed and not hard_block,
            "deterministic_fallback_allowed": deterministic_fallback,
            "hybrid_fusion_allowed": effective_mode == "hybrid",
            "export_connected_artifacts": effective_mode in {"connected", "hybrid"},
            "governance_decision": governance,
            "feed_activation": feed_activation,
            "warnings": warnings,
            "profile": self.profile(effective_mode),
        }

    def profile(self, mode: str) -> Dict[str, Any]:
        normalized = self.normalize(mode)
        if mode == "blocked":
            return {
                "mode": "blocked",
                "name": "Blocked",
                "connected_ingestion": "disabled",
                "deterministic_core": "not launched",
                "hybrid_fusion": "disabled",
                "export_posture": "no export",
                "safety_posture": "hard stop",
            }
        for profile in self._profiles():
            if profile.mode == normalized:
                return asdict(profile)
        return asdict(self._profiles()[0])

    def normalize(self, mode: str | None) -> str:
        mode = mode or "deterministic"
        if mode == "connected_intelligence":
            mode = "connected"
        return mode if mode in {"deterministic", "connected", "hybrid"} else "deterministic"

    def _profiles(self) -> List[ModeProfile]:
        return [
            ModeProfile(
                mode="deterministic",
                name="Deterministic",
                connected_ingestion="disabled",
                deterministic_core="primary",
                hybrid_fusion="disabled",
                export_posture="standard deterministic exports",
                safety_posture="sealed local reasoning",
            ),
            ModeProfile(
                mode="connected",
                name="Connected Intelligence",
                connected_ingestion="governed allowlist",
                deterministic_core="supporting",
                hybrid_fusion="available for candidate previews",
                export_posture="standard exports plus connected sidecars",
                safety_posture="feed activation and legal audit required",
            ),
            ModeProfile(
                mode="hybrid",
                name="Hybrid",
                connected_ingestion="governed allowlist",
                deterministic_core="primary",
                hybrid_fusion="primary",
                export_posture="standard exports plus connected and hybrid sidecars",
                safety_posture="dual-core governed fusion",
            ),
        ]
