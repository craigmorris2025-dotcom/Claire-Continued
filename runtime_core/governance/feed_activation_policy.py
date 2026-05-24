"""
Feed Activation Policy — permission layer for connected/hybrid feed use.

v5.43:
- Does not ingest data.
- Decides whether a feed request is allowed, review-required, blocked, or deterministic-only.
- Preserves deterministic fallback while preparing safe connected/hybrid activation.
"""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timezone
import uuid

from runtime_core.governance.redline_classifier import RedlineClassifier
from runtime_core.governance.source_allowlist import SourceAllowlist


class FeedActivationPolicy:
    """Evaluate feed activation requests against mode, source, universe, and redline rules."""

    def __init__(self) -> None:
        self.redlines = RedlineClassifier()
        self.sources = SourceAllowlist()

    def status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "activation_layer": "ready",
            "connected_ingestion_default": False,
            "deterministic_fallback_default": True,
            "supported_modes": ["deterministic", "connected", "hybrid"],
            "policy_summary": {
                "deterministic": "No external ingestion. Offline taxonomy and protected opportunity generation only.",
                "connected": "Connected feeds may be activated from approved source categories after governance checks.",
                "hybrid": "Connected feeds may be activated and fused with deterministic logic after governance checks.",
            },
            "source_allowlist": self.sources.catalog(),
        }

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request = request or {}
        mode = self._normalize_mode(request.get("execution_mode") or request.get("mode"))
        market_universe = request.get("market_universe") or "custom_universe"
        source_category = request.get("source_category") or self._default_source_category(market_universe)
        signal = request.get("signal") or request.get("raw_input") or request.get("text") or ""

        redline_decision = self.redlines.classify(signal, {
            "execution_mode": mode,
            "market_universe": market_universe,
            "source_category": source_category,
            "workflow": request.get("workflow"),
            "industry_domain": request.get("industry_domain"),
            "buyer_segment": request.get("buyer_segment"),
            "objective": request.get("objective"),
        })

        if redline_decision.get("decision") == "block":
            return self._decision(
                request=request,
                decision="block",
                severity="critical",
                feed_status="blocked",
                reason="Feed activation blocked by governance hard stop.",
                connected_ingestion_allowed=False,
                deterministic_fallback_allowed=True,
                redline_decision=redline_decision,
                source_category=source_category,
            )

        if mode == "deterministic":
            return self._decision(
                request=request,
                decision="deterministic_only",
                severity="low",
                feed_status="offline_fallback",
                reason="Deterministic mode selected. External feed ingestion remains disabled; offline fallback is allowed.",
                connected_ingestion_allowed=False,
                deterministic_fallback_allowed=True,
                redline_decision=redline_decision,
                source_category=source_category,
            )

        source_check = self.sources.check(source_category)
        if not source_check.get("allowed"):
            return self._decision(
                request=request,
                decision="review",
                severity="high",
                feed_status="source_review_required",
                reason=f"Source category '{source_category}' is not currently allowlisted for connected feed activation.",
                connected_ingestion_allowed=False,
                deterministic_fallback_allowed=True,
                redline_decision=redline_decision,
                source_category=source_category,
                source_check=source_check,
            )

        if redline_decision.get("decision") == "review":
            return self._decision(
                request=request,
                decision="review",
                severity="high",
                feed_status="governance_review_required",
                reason="Connected/hybrid feed activation requires review due to sensitive defense/legal indicators.",
                connected_ingestion_allowed=False,
                deterministic_fallback_allowed=True,
                redline_decision=redline_decision,
                source_category=source_category,
                source_check=source_check,
            )

        return self._decision(
            request=request,
            decision="allow",
            severity="medium" if mode == "hybrid" else "low",
            feed_status="activation_allowed",
            reason=f"{mode.title()} feed activation is allowed for approved source category '{source_category}'.",
            connected_ingestion_allowed=True,
            deterministic_fallback_allowed=True,
            redline_decision=redline_decision,
            source_category=source_category,
            source_check=source_check,
        )

    def _decision(
        self,
        request: Dict[str, Any],
        decision: str,
        severity: str,
        feed_status: str,
        reason: str,
        connected_ingestion_allowed: bool,
        deterministic_fallback_allowed: bool,
        redline_decision: Dict[str, Any],
        source_category: str,
        source_check: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "activation_id": "act_" + uuid.uuid4().hex[:12],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "severity": severity,
            "feed_status": feed_status,
            "reason": reason,
            "execution_mode": self._normalize_mode(request.get("execution_mode") or request.get("mode")),
            "market_universe": request.get("market_universe") or "custom_universe",
            "source_category": source_category,
            "connected_ingestion_allowed": connected_ingestion_allowed,
            "deterministic_fallback_allowed": deterministic_fallback_allowed,
            "redline_decision": redline_decision,
            "source_check": source_check or {},
        }

    def _default_source_category(self, market_universe: str) -> str:
        if market_universe in {"sp500_public", "djia_public", "nasdaq_composite"}:
            return "public_company_market_data"
        if market_universe == "private_sector_establishments":
            return "public_statistical_establishment_data"
        if market_universe in {"federal_government", "defense_industrial_base"}:
            return "public_government_procurement_data"
        return "user_supplied_or_custom_sources"

    def _normalize_mode(self, mode: str | None) -> str:
        mode = mode or "deterministic"
        if mode == "connected_intelligence":
            mode = "connected"
        return mode if mode in {"deterministic", "connected", "hybrid"} else "deterministic"
