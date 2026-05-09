"""
Trend Trajectory Engine — models trend direction, historical trajectory,
inflection signals, timing pressure, adoption curve position, and inevitability.

Purpose:
- Give Claire a dedicated Stage 3 lifecycle engine
- Move beyond static keyword/gap matching
- Estimate whether a market/technology pattern is accelerating, emerging,
  plateauing, or strategically inevitable
- Feed discovery, breakthrough, market gap, binder, and lifecycle outputs

This version is deterministic/local. Later versions can plug into real datasets,
time series, filings, patents, news, funding data, and market history.
"""

from typing import Any, Dict, List, Optional


class TrendTrajectoryEngine:
    """
    Deterministic trend and trajectory analyzer.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        connector_sources = connector_sources or {}

        signals = self._extract_signals(
            text=text,
            keywords=keywords,
            market_gap=market_gap,
            connector_sources=connector_sources,
        )

        trend_direction = self._trend_direction(signals)
        adoption_position = self._adoption_curve_position(signals)
        trajectory = self._trajectory_profile(signals, trend_direction, adoption_position)

        return {
            "status": "success",
            "domain": domain,
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
            "trend_direction": trend_direction,
            "historical_trajectory": trajectory,
            "adoption_curve_position": adoption_position,
            "inflection_signals": self._inflection_signals(signals),
            "timing_pressure": self._timing_pressure(signals),
            "market_momentum": self._market_momentum(signals),
            "inevitability_score": self._inevitability_score(signals),
            "trajectory_risk": self._trajectory_risk(signals),
            "strategic_window": self._strategic_window(signals),
            "evidence_signals": signals,
            "confidence": self._confidence(signals),
        }

    # =========================
    # SIGNAL EXTRACTION
    # =========================
    def _extract_signals(
        self,
        text: str,
        keywords: List[str],
        market_gap: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        keyword_text = " ".join(keywords).lower()
        combined = f"{text} {keyword_text}"

        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        pressure = market_gap.get("strategic_pressure", {}) if isinstance(market_gap, dict) else {}
        pressure_score = pressure.get("score", 0.0) if isinstance(pressure, dict) else 0.0
        gap_confidence = market_gap.get("confidence", 0.0) if isinstance(market_gap, dict) else 0.0

        acceleration_terms = [
            "accelerating",
            "rapid",
            "surge",
            "spike",
            "velocity",
            "funding velocity",
            "adoption",
            "growth",
            "demand",
            "pressure",
            "shortage",
            "bottleneck",
            "resilience",
            "regulatory",
            "urgent",
        ]

        inevitability_terms = [
            "inevitable",
            "must",
            "needed",
            "critical",
            "mission-critical",
            "before outcomes degrade",
            "before capital reprices",
            "before shortages",
            "unmet",
            "gap",
            "gaps",
            "infrastructure",
            "capacity",
        ]

        weak_signal_terms = [
            "hidden",
            "early",
            "emerging",
            "overlooked",
            "weak signal",
            "unseen",
            "undetected",
            "latent",
            "underpriced",
            "underserved",
        ]

        maturity_terms = [
            "legacy",
            "manual",
            "fragmented",
            "reactive",
            "inefficient",
            "siloed",
            "outdated",
        ]

        data_terms = [
            "historical",
            "trajectory",
            "trend",
            "time series",
            "forecast",
            "predict",
            "predicts",
            "model",
            "maps",
            "detects",
            "analyzes",
        ]

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term in combined)

        return {
            "acceleration_term_count": count_terms(acceleration_terms),
            "inevitability_term_count": count_terms(inevitability_terms),
            "weak_signal_term_count": count_terms(weak_signal_terms),
            "maturity_term_count": count_terms(maturity_terms),
            "data_term_count": count_terms(data_terms),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(gap_confidence or 0.0),
            "strategic_pressure_score": float(pressure_score or 0.0),
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
        }

    # =========================
    # OUTPUT BUILDERS
    # =========================
    def _trend_direction(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        acceleration = self._acceleration_score(signals)

        if acceleration >= 0.78:
            direction = "accelerating"
        elif acceleration >= 0.58:
            direction = "rising"
        elif acceleration >= 0.38:
            direction = "emerging"
        else:
            direction = "weak_or_unclear"

        return {
            "direction": direction,
            "score": round(acceleration, 4),
            "drivers": self._direction_drivers(signals),
        }

    def _adoption_curve_position(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        maturity = self._maturity_score(signals)
        acceleration = self._acceleration_score(signals)

        if maturity >= 0.72 and acceleration >= 0.60:
            position = "early_majority_transition"
        elif maturity >= 0.45 and acceleration >= 0.55:
            position = "early_adoption"
        elif acceleration >= 0.70:
            position = "rapid_emergence"
        elif maturity < 0.30:
            position = "pre_market_signal"
        else:
            position = "emerging_market"

        return {
            "position": position,
            "maturity_score": round(maturity, 4),
            "adoption_pressure": round(acceleration, 4),
        }

    def _trajectory_profile(
        self,
        signals: Dict[str, Any],
        trend_direction: Dict[str, Any],
        adoption_position: Dict[str, Any],
    ) -> Dict[str, Any]:
        momentum = self._market_momentum(signals)
        inevitability = self._inevitability_score(signals)

        if momentum["score"] >= 0.75 and inevitability["score"] >= 0.75:
            shape = "compound_acceleration"
        elif momentum["score"] >= 0.60:
            shape = "steady_acceleration"
        elif inevitability["score"] >= 0.70:
            shape = "pressure_driven_adoption"
        else:
            shape = "early_signal_accumulation"

        return {
            "shape": shape,
            "direction": trend_direction["direction"],
            "adoption_position": adoption_position["position"],
            "interpretation": self._trajectory_interpretation(shape, signals),
        }

    def _inflection_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        inflections = []

        if signals["strategic_pressure_score"] >= 0.75:
            inflections.append("high strategic pressure")

        if signals["patent_activity"] >= 0.65:
            inflections.append("elevated patent activity")

        if signals["patent_novelty"] >= 0.55:
            inflections.append("novel technical activity")

        if signals["weak_signal_term_count"] > 0:
            inflections.append("weak signal / overlooked opportunity language")

        if signals["acceleration_term_count"] >= 2:
            inflections.append("acceleration vocabulary present")

        if signals["maturity_term_count"] > 0:
            inflections.append("legacy or reactive market structure")

        if not inflections:
            inflections.append("no strong inflection signal detected")

        score = min(
            0.95,
            0.30
            + signals["strategic_pressure_score"] * 0.25
            + signals["patent_activity"] * 0.15
            + signals["patent_novelty"] * 0.10
            + min(0.15, signals["acceleration_term_count"] * 0.03)
            + min(0.10, signals["weak_signal_term_count"] * 0.03)
        )

        return {
            "score": round(score, 4),
            "signals": inflections,
        }

    def _timing_pressure(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.95,
            0.25
            + signals["strategic_pressure_score"] * 0.35
            + signals["market_gap_confidence"] * 0.18
            + signals["market_volatility"] * 0.08
            + min(0.14, signals["inevitability_term_count"] * 0.035)
        )

        if score >= 0.78:
            level = "urgent"
        elif score >= 0.60:
            level = "high"
        elif score >= 0.42:
            level = "moderate"
        else:
            level = "early"

        return {
            "level": level,
            "score": round(score, 4),
            "rationale": self._timing_rationale(level, signals),
        }

    def _market_momentum(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.95,
            0.30
            + signals["market_growth"] * 0.18
            + signals["patent_activity"] * 0.20
            + signals["patent_novelty"] * 0.14
            + signals["market_gap_confidence"] * 0.12
            + min(0.11, signals["acceleration_term_count"] * 0.025)
        )

        if score >= 0.75:
            level = "strong"
        elif score >= 0.55:
            level = "moderate"
        else:
            level = "emerging"

        return {
            "level": level,
            "score": round(score, 4),
        }

    def _inevitability_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.96,
            0.25
            + signals["strategic_pressure_score"] * 0.30
            + signals["market_gap_confidence"] * 0.22
            + signals["patent_activity"] * 0.08
            + min(0.16, signals["inevitability_term_count"] * 0.04)
        )

        if score >= 0.82:
            level = "highly_inevitable"
        elif score >= 0.65:
            level = "likely"
        elif score >= 0.48:
            level = "possible"
        else:
            level = "speculative"

        return {
            "level": level,
            "score": round(score, 4),
        }

    def _trajectory_risk(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        risk = min(
            0.92,
            0.20
            + signals["financial_risk"] * 0.30
            + signals["market_volatility"] * 0.24
            + max(0.0, 0.65 - signals["financial_health"]) * 0.18
        )

        if risk >= 0.65:
            level = "high"
        elif risk >= 0.42:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(risk, 4),
            "risk_factors": self._risk_factors(signals),
        }

    def _strategic_window(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        timing = self._timing_pressure(signals)
        inevitability = self._inevitability_score(signals)
        momentum = self._market_momentum(signals)

        window_score = min(
            0.96,
            timing["score"] * 0.40
            + inevitability["score"] * 0.35
            + momentum["score"] * 0.25
        )

        if window_score >= 0.80:
            window = "now"
        elif window_score >= 0.64:
            window = "near_term"
        elif window_score >= 0.48:
            window = "watch_and_prepare"
        else:
            window = "early_watchlist"

        return {
            "window": window,
            "score": round(window_score, 4),
        }

    # =========================
    # SCORING HELPERS
    # =========================
    def _acceleration_score(self, signals: Dict[str, Any]) -> float:
        return min(
            0.95,
            0.28
            + signals["strategic_pressure_score"] * 0.24
            + signals["market_gap_confidence"] * 0.16
            + signals["patent_activity"] * 0.14
            + signals["market_growth"] * 0.08
            + min(0.15, signals["acceleration_term_count"] * 0.03)
        )

    def _maturity_score(self, signals: Dict[str, Any]) -> float:
        return min(
            0.95,
            0.22
            + signals["patent_activity"] * 0.18
            + signals["financial_health"] * 0.14
            + signals["market_gap_confidence"] * 0.12
            + min(0.18, signals["data_term_count"] * 0.03)
            + min(0.11, signals["maturity_term_count"] * 0.035)
        )

    def _confidence(self, signals: Dict[str, Any]) -> float:
        return round(
            min(
                0.96,
                0.25
                + signals["market_gap_confidence"] * 0.28
                + signals["strategic_pressure_score"] * 0.22
                + signals["patent_activity"] * 0.12
                + signals["data_term_count"] * 0.025
            ),
            4,
        )

    # =========================
    # TEXT HELPERS
    # =========================
    def _direction_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []

        if signals["strategic_pressure_score"] >= 0.70:
            drivers.append("strategic pressure")

        if signals["market_gap_confidence"] >= 0.70:
            drivers.append("high-confidence market gap")

        if signals["patent_activity"] >= 0.65:
            drivers.append("patent activity")

        if signals["acceleration_term_count"] > 0:
            drivers.append("acceleration language")

        if signals["data_term_count"] > 0:
            drivers.append("data/modeling language")

        if not drivers:
            drivers.append("limited deterministic signals")

        return drivers

    def _trajectory_interpretation(self, shape: str, signals: Dict[str, Any]) -> str:
        sector = signals.get("sector", "target sector")

        if shape == "compound_acceleration":
            return (
                f"{sector} shows a compound acceleration pattern: market pressure, gap confidence, "
                f"and technical activity are reinforcing each other."
            )

        if shape == "steady_acceleration":
            return (
                f"{sector} shows steady acceleration, with enough momentum to justify active discovery "
                f"and validation."
            )

        if shape == "pressure_driven_adoption":
            return (
                f"{sector} appears pressure-driven: adoption may be forced by operational pain, risk, "
                f"or market constraints even if maturity remains uneven."
            )

        return (
            f"{sector} is in early signal accumulation; additional evidence should be gathered before "
            f"high-conviction execution."
        )

    def _timing_rationale(self, level: str, signals: Dict[str, Any]) -> str:
        if level == "urgent":
            return "High pressure and high market-gap confidence suggest the strategic window is open now."

        if level == "high":
            return "Signals suggest near-term pressure and meaningful timing advantage."

        if level == "moderate":
            return "The opportunity is forming, but more evidence would improve timing confidence."

        return "Timing remains early; monitor for stronger inflection signals."

    def _risk_factors(self, signals: Dict[str, Any]) -> List[str]:
        factors = []

        if signals["financial_risk"] >= 0.45:
            factors.append("financial risk")

        if signals["market_volatility"] >= 0.25:
            factors.append("market volatility")

        if signals["financial_health"] < 0.55:
            factors.append("weaker financial health signal")

        if not factors:
            factors.append("no major trajectory risk surfaced")

        return factors
