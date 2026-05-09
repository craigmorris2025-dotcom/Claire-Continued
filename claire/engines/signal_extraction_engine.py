"""
Signal Extraction Engine — dedicated Stage 2 engine for Claire.

v6.1.1:
- Preserves existing deterministic signal extraction behavior.
- Improves source-driven signal interpretation for live/simulated connector packets.
- Promotes real event-derived keywords over weak upstream keywords.
- Scores connector event severity/confidence so rich source packets raise signal quality.
- Keeps outputs compatible with lifecycle, binder, proof, and downstream pipeline diagnostics.
"""

from typing import Any, Dict, List, Optional
import re


class SignalExtractionEngine:
    """Deterministic signal extraction and routing-evidence analyzer."""

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = text or ""
        keywords = keywords or []
        connector_sources = connector_sources or {}

        normalized = self._normalize(text)
        tokens = self._tokens(normalized)

        sector_signals = self._sector_signals(normalized)
        dominant_sector = self._dominant_sector(sector_signals)
        semantic_profile = self._semantic_profile(normalized, tokens, keywords)
        buyer_signals = self._buyer_signals(normalized)
        product_signals = self._product_signals(normalized)
        control_signals = self._control_signals(normalized)
        evidence_signals = self._evidence_signals(normalized)
        technical_signals = self._technical_signals(normalized)
        routing_evidence = self._routing_evidence(dominant_sector, sector_signals, normalized)
        quality = self._signal_quality_score(
            semantic_profile=semantic_profile,
            sector_signals=sector_signals,
            buyer_signals=buyer_signals,
            product_signals=product_signals,
            control_signals=control_signals,
            evidence_signals=evidence_signals,
            technical_signals=technical_signals,
            connector_sources=connector_sources,
        )

        return {
            "status": "success",
            "domain": domain,
            "dominant_sector": dominant_sector,
            "signal_quality_score": quality,
            "semantic_profile": semantic_profile,
            "extracted_keywords": self._ranked_keywords(tokens, keywords),
            "entities": self._entities(text),
            "sector_signals": sector_signals,
            "buyer_signals": buyer_signals,
            "product_signals": product_signals,
            "control_signals": control_signals,
            "evidence_signals": evidence_signals,
            "technical_signals": technical_signals,
            "routing_evidence": routing_evidence,
            "signal_contract": self._signal_contract(
                dominant_sector=dominant_sector,
                semantic_profile=semantic_profile,
                buyer_signals=buyer_signals,
                product_signals=product_signals,
                control_signals=control_signals,
                evidence_signals=evidence_signals,
                technical_signals=technical_signals,
            ),
            "recommended_downstream_attention": self._recommended_attention(
                dominant_sector=dominant_sector,
                quality=quality,
                control_signals=control_signals,
                evidence_signals=evidence_signals,
                sector_signals=sector_signals,
            ),
            "signal_extraction_thesis": self._thesis(dominant_sector, quality, control_signals, evidence_signals),
            "confidence": self._confidence(quality, sector_signals, semantic_profile),
        }

    # =========================
    # Signal groups
    # =========================
    def _sector_signals(self, text: str) -> Dict[str, Any]:
        sector_terms = {
            "climate_insurance": [
                "insurance", "insurer", "reinsurer", "reinsurance", "underwriting", "underwriter",
                "premium", "catastrophe", "weather loss", "wildfire", "flood", "exposure",
                "risk-transfer", "risk transfer", "market withdrawal", "loss history",
                "portfolio exposure", "repricing", "property", "carrier", "carriers",
                "climate", "climate-exposed",
            ],
            "defense_autonomy": [
                "defense", "mission", "secure command", "command", "sensor", "operator",
                "autonomy", "autonomous", "drone", "battlefield", "contested", "allowed-use",
                "allowed use", "human authorization", "mission simulation", "audit log",
            ],
            "healthcare_operations": [
                "hospital", "healthcare", "patient", "patient-flow", "patient flow", "staffing",
                "capacity", "bed", "emergency department", "discharge", "clinical", "command center",
            ],
            "industrial_supply_chain": [
                "manufacturer", "supplier", "component", "shortage", "procurement", "production",
                "logistics", "erp", "factory", "bottleneck", "dependency graph", "disruption",
            ],
            "energy_infrastructure": [
                "energy", "utility", "grid", "transmission", "outage", "asset risk", "demand",
                "resilience", "infrastructure", "substation", "power", "operator review",
            ],
            "financial_market_intelligence": [
                "financial", "market", "credit", "liquidity", "portfolio", "institutional",
                "research", "risk desk", "macro", "repricing", "regime", "sector rotation",
            ],
        }

        scores: Dict[str, Any] = {}
        for sector, terms in sector_terms.items():
            matched = [term for term in terms if term in text]
            score = self._bounded(0.05 + len(matched) * 0.055)
            scores[sector] = {
                "score": round(score, 4),
                "matched_terms": matched[:12],
                "term_count": len(matched),
            }

        return scores

    def _buyer_signals(self, text: str) -> Dict[str, Any]:
        terms = [
            "buyer", "customer", "underwriter", "underwriters", "operator", "planner", "procurement",
            "risk team", "research desk", "hospital", "utility", "defense prime",
            "reinsurer", "reinsurers", "carrier", "carriers", "portfolio team", "mission team",
            "budget", "sponsor", "workflow owner", "broker", "brokers",
        ]
        matched = [term for term in terms if term in text]
        return {
            "score": round(self._bounded(0.10 + len(matched) * 0.065), 4),
            "matched_terms": matched,
            "buyer_present": len(matched) > 0,
        }

    def _product_signals(self, text: str) -> Dict[str, Any]:
        terms = [
            "platform", "product", "pilot", "module", "workflow", "console",
            "dashboard", "api", "service", "engine", "subscription", "enterprise",
            "benchmark", "recommendation", "detector", "intelligence", "analytics",
            "modeling", "automation",
        ]
        matched = [term for term in terms if term in text]
        return {
            "score": round(self._bounded(0.08 + len(matched) * 0.052), 4),
            "matched_terms": matched,
            "productizable": any(term in matched for term in [
                "platform", "pilot", "workflow", "console", "engine", "subscription",
                "enterprise", "analytics", "modeling", "automation",
            ]),
        }

    def _control_signals(self, text: str) -> Dict[str, Any]:
        terms = [
            "human review", "human-reviewed", "human authorization", "approval",
            "override", "audit", "audit log", "audit trail", "allowed-use",
            "allowed use", "restricted-use", "restricted use", "shadow mode",
            "advisory", "controls", "governance", "secure deployment",
            "compliance", "privacy", "explainable", "traceability",
        ]
        matched = [term for term in terms if term in text]
        control_gated = any(term in matched for term in [
            "human authorization", "allowed-use", "allowed use", "restricted-use",
            "restricted use", "secure deployment", "shadow mode", "human review",
            "human-reviewed",
        ])
        return {
            "score": round(self._bounded(0.06 + len(matched) * 0.055), 4),
            "matched_terms": matched,
            "control_gated": control_gated,
            "governance_present": any(term in matched for term in ["governance", "compliance", "audit", "audit log", "audit trail"]),
        }

    def _evidence_signals(self, text: str) -> Dict[str, Any]:
        terms = [
            "backtest", "validation", "validated", "evidence", "accuracy",
            "simulation", "scenario", "pilot", "proof", "review", "scorecard",
            "historical", "false-positive", "false positive", "false-negative",
            "false negative", "roi", "time-to-decision", "time to decision",
            "confidence", "severity", "timestamp", "credibility",
        ]
        matched = [term for term in terms if term in text]
        return {
            "score": round(self._bounded(0.08 + len(matched) * 0.050), 4),
            "matched_terms": matched,
            "validation_ready": any(term in matched for term in [
                "backtest", "validation", "validated", "simulation", "scenario",
                "pilot", "proof", "evidence", "confidence", "severity",
            ]),
        }

    def _technical_signals(self, text: str) -> Dict[str, Any]:
        terms = [
            "ingests", "ingestion", "sensor", "data", "model", "api", "adapter",
            "integration", "simulation", "engine", "workflow", "console",
            "authorization", "audit", "trace", "scoring", "recommendation",
            "monitoring", "schema", "versioning", "exposure", "analytics",
            "automation", "modeling",
        ]
        matched = [term for term in terms if term in text]
        return {
            "score": round(self._bounded(0.08 + len(matched) * 0.045), 4),
            "matched_terms": matched,
            "implementation_relevant": len(matched) >= 3,
        }

    def _semantic_profile(self, text: str, tokens: List[str], keywords: List[str]) -> Dict[str, Any]:
        unique_tokens = set(tokens)
        token_count = len(tokens)
        unique_count = len(unique_tokens)
        long_token_count = len([t for t in unique_tokens if len(t) >= 8])
        sentence_count = max(1, len([p for p in re.split(r"[.!?]+", text) if p.strip()]))

        density = self._bounded((unique_count / max(1, token_count)) * 0.45 + min(0.45, long_token_count * 0.012))
        specificity = self._bounded(min(0.65, long_token_count * 0.018) + min(0.25, len(keywords) * 0.012))
        structure = self._bounded(min(0.45, sentence_count * 0.05) + min(0.45, token_count / 180.0))

        return {
            "token_count": token_count,
            "unique_token_count": unique_count,
            "sentence_count": sentence_count,
            "semantic_density_score": round(density, 4),
            "specificity_score": round(specificity, 4),
            "structure_score": round(structure, 4),
        }

    # =========================
    # Derived outputs
    # =========================
    def _dominant_sector(self, sector_signals: Dict[str, Any]) -> str:
        if not sector_signals:
            return "general_intelligence"
        ranked = sorted(
            sector_signals.items(),
            key=lambda item: (item[1].get("score", 0.0), item[1].get("term_count", 0)),
            reverse=True,
        )
        top_sector, top_data = ranked[0]
        if top_data.get("score", 0.0) < 0.12:
            return "general_intelligence"
        return top_sector

    def _routing_evidence(self, dominant_sector: str, sector_signals: Dict[str, Any], text: str) -> Dict[str, Any]:
        ranked = sorted(
            [
                {
                    "sector": sector,
                    "score": data.get("score", 0.0),
                    "matched_terms": data.get("matched_terms", []),
                }
                for sector, data in sector_signals.items()
            ],
            key=lambda item: item["score"],
            reverse=True,
        )

        top = ranked[0] if ranked else {"score": 0.0}
        second = ranked[1] if len(ranked) > 1 else {"score": 0.0}
        margin = self._bounded(float(top.get("score", 0.0)) - float(second.get("score", 0.0)), 0.0, 1.0)

        return {
            "dominant_sector": dominant_sector,
            "ranked_sectors": ranked,
            "routing_confidence_score": round(self._bounded(0.25 + margin * 0.75), 4),
            "cross_sector_ambiguity": margin < 0.12,
            "routing_note": self._routing_note(dominant_sector, margin),
        }

    def _signal_contract(
        self,
        dominant_sector: str,
        semantic_profile: Dict[str, Any],
        buyer_signals: Dict[str, Any],
        product_signals: Dict[str, Any],
        control_signals: Dict[str, Any],
        evidence_signals: Dict[str, Any],
        technical_signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "dominant_sector": dominant_sector,
            "has_buyer_signal": buyer_signals.get("buyer_present", False),
            "has_product_signal": product_signals.get("productizable", False),
            "has_control_signal": control_signals.get("control_gated", False),
            "has_evidence_signal": evidence_signals.get("validation_ready", False),
            "has_technical_signal": technical_signals.get("implementation_relevant", False),
            "semantic_density_score": semantic_profile.get("semantic_density_score", 0.0),
            "specificity_score": semantic_profile.get("specificity_score", 0.0),
        }

    def _recommended_attention(
        self,
        dominant_sector: str,
        quality: Dict[str, Any],
        control_signals: Dict[str, Any],
        evidence_signals: Dict[str, Any],
        sector_signals: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        attention = []

        if control_signals.get("control_gated"):
            attention.append({
                "area": "controls",
                "reason": "control-gated language appears in the input",
                "downstream_use": "risk, feasibility, productization, and positioning should preserve advisory/human-review framing",
                "priority": "critical",
            })

        if evidence_signals.get("validation_ready"):
            attention.append({
                "area": "validation",
                "reason": "validation, simulation, pilot, proof, event confidence, or severity evidence appears in the input",
                "downstream_use": "technical feasibility and productization should create evidence gates",
                "priority": "high",
            })

        if quality.get("level") in {"weak", "thin"}:
            attention.append({
                "area": "input quality",
                "reason": "input has limited specificity or sparse semantic signals",
                "downstream_use": "treat discovery and breakthrough conclusions as early until richer evidence is provided",
                "priority": "medium",
            })

        if dominant_sector != "general_intelligence":
            attention.append({
                "area": "routing",
                "reason": f"dominant sector appears to be {dominant_sector}",
                "downstream_use": "sector-specific engines should preserve this routing unless later evidence strongly overrides it",
                "priority": "high",
            })

        return attention or [{
            "area": "general",
            "reason": "basic signal extraction completed",
            "downstream_use": "use signal contract for diagnostics and lifecycle proof",
            "priority": "medium",
        }]

    def _signal_quality_score(
        self,
        semantic_profile: Dict[str, Any],
        sector_signals: Dict[str, Any],
        buyer_signals: Dict[str, Any],
        product_signals: Dict[str, Any],
        control_signals: Dict[str, Any],
        evidence_signals: Dict[str, Any],
        technical_signals: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        top_sector_score = max([v.get("score", 0.0) for v in sector_signals.values()] or [0.0])
        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        patent = connector_sources.get("patent", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        event_signal = self._event_signal_score(connector_sources)
        source_breadth = self._source_breadth_score(connector_sources)
        cross_source_alignment = self._cross_source_alignment_score(connector_sources)

        score = self._bounded(
            0.12
            + semantic_profile.get("semantic_density_score", 0.0) * 0.100
            + semantic_profile.get("specificity_score", 0.0) * 0.120
            + semantic_profile.get("structure_score", 0.0) * 0.060
            + top_sector_score * 0.120
            + buyer_signals.get("score", 0.0) * 0.100
            + product_signals.get("score", 0.0) * 0.100
            + control_signals.get("score", 0.0) * 0.080
            + evidence_signals.get("score", 0.0) * 0.100
            + technical_signals.get("score", 0.0) * 0.080
            + event_signal * 0.180
            + source_breadth * 0.055
            + cross_source_alignment * 0.070
            + float(market.get("growth", 0.0) or 0.0) * 0.040
            + float(market.get("volatility", 0.0) or 0.0) * 0.020
            + float(patent.get("activity", 0.0) or 0.0) * 0.040
            + float(patent.get("novelty", patent.get("novelty_score", 0.0)) or 0.0) * 0.030
            + float(financial.get("health", 0.0) or 0.0) * 0.025
        )

        level = "strong" if score >= 0.70 else "usable" if score >= 0.55 else "thin" if score >= 0.38 else "weak"

        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._quality_drivers(
                semantic_profile=semantic_profile,
                top_sector_score=top_sector_score,
                buyer_signals=buyer_signals,
                product_signals=product_signals,
                control_signals=control_signals,
                evidence_signals=evidence_signals,
                technical_signals=technical_signals,
                connector_sources=connector_sources,
                event_signal=event_signal,
                source_breadth=source_breadth,
                cross_source_alignment=cross_source_alignment,
            ),
        }

    def _confidence(self, quality: Dict[str, Any], sector_signals: Dict[str, Any], semantic_profile: Dict[str, Any]) -> float:
        top_sector_score = max([v.get("score", 0.0) for v in sector_signals.values()] or [0.0])
        return round(self._bounded(
            0.22
            + quality.get("score", 0.0) * 0.24
            + top_sector_score * 0.12
            + semantic_profile.get("semantic_density_score", 0.0) * 0.08
            + semantic_profile.get("specificity_score", 0.0) * 0.08
        ), 4)

    def _thesis(
        self,
        dominant_sector: str,
        quality: Dict[str, Any],
        control_signals: Dict[str, Any],
        evidence_signals: Dict[str, Any],
    ) -> str:
        sector_label = dominant_sector.replace("_", " ")
        control_note = " Control-gated language is present and should be preserved downstream." if control_signals.get("control_gated") else ""
        evidence_note = " Validation/evidence language is present and should drive proof gates." if evidence_signals.get("validation_ready") else ""
        return (
            f"Signal extraction identifies {sector_label} as the dominant routing context with "
            f"{quality.get('level')} signal quality and score {quality.get('score')}."
            f"{control_note}{evidence_note}"
        )

    # =========================
    # Connector / event helpers
    # =========================
    def _event_signal_score(self, connector_sources: Dict[str, Any]) -> float:
        if not isinstance(connector_sources, dict):
            return 0.0

        total = 0.0
        count = 0

        for source in connector_sources.values():
            if not isinstance(source, dict):
                continue
            events = source.get("events", [])
            if not isinstance(events, list):
                continue

            for event in events:
                if not isinstance(event, dict):
                    continue
                severity = self._safe_float(event.get("severity", 0.0))
                confidence = self._safe_float(event.get("confidence", 0.0))
                if severity <= 0 and confidence <= 0:
                    continue
                total += severity * max(confidence, 0.35)
                count += 1

        if count == 0:
            return 0.0

        return self._bounded(total / count)

    def _source_breadth_score(self, connector_sources: Dict[str, Any]) -> float:
        if not isinstance(connector_sources, dict):
            return 0.0

        useful_sources = [
            name for name, payload in connector_sources.items()
            if isinstance(payload, dict) and payload
        ]

        return self._bounded(len(useful_sources) / 5.0)

    def _cross_source_alignment_score(self, connector_sources: Dict[str, Any]) -> float:
        if not isinstance(connector_sources, dict):
            return 0.0

        source_terms: List[set] = []

        for source in connector_sources.values():
            if not isinstance(source, dict):
                continue

            text_parts: List[str] = []

            for key, value in source.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, dict):
                    text_parts.extend(str(v) for v in value.values() if isinstance(v, (str, int, float)))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            text_parts.extend(str(v) for v in item.values() if isinstance(v, (str, int, float)))
                        elif isinstance(item, (str, int, float)):
                            text_parts.append(str(item))

            tokens = set(self._tokens(self._normalize(" ".join(text_parts))))
            tokens = {t for t in tokens if len(t) >= 5}
            if tokens:
                source_terms.append(tokens)

        if len(source_terms) < 2:
            return 0.0

        overlap_count = 0
        comparison_count = 0

        for i in range(len(source_terms)):
            for j in range(i + 1, len(source_terms)):
                comparison_count += 1
                if source_terms[i].intersection(source_terms[j]):
                    overlap_count += 1

        if comparison_count == 0:
            return 0.0

        return self._bounded(overlap_count / comparison_count)

    # =========================
    # Simple extraction helpers
    # =========================
    def _ranked_keywords(self, tokens: List[str], existing_keywords: List[str]) -> List[str]:
        stop = {
            "the", "and", "for", "with", "that", "this", "from", "into", "than", "then",
            "they", "their", "must", "will", "should", "before", "after", "under", "over",
            "system", "platform", "uses", "using", "use", "need", "needs", "while",
            "market", "source", "sources", "connected", "signal", "stream", "data",
        }

        preferred_terms = {
            "insurance", "capacity", "withdrawal", "carrier", "carriers", "property",
            "climate", "climate-exposed", "repricing", "premium", "underwriting",
            "reinsurance", "reinsurers", "catastrophe", "exposure", "portfolio",
            "concentration", "risk", "analytics", "modeling", "workflow",
            "automation", "decision", "pricing", "loss", "loss-ratio", "filing",
            "patent", "technology", "convergence",
        }

        counts: Dict[str, float] = {}

        for token in tokens:
            if len(token) < 4 or token in stop:
                continue
            weight = 1.0
            if token in preferred_terms:
                weight += 1.25
            if len(token) >= 9:
                weight += 0.25
            counts[token] = counts.get(token, 0.0) + weight

        ranked = sorted(counts.items(), key=lambda item: (item[1], len(item[0])), reverse=True)

        clean_existing = []
        for keyword in existing_keywords or []:
            keyword = str(keyword).lower().strip()
            if len(keyword) <= 5 or keyword in stop:
                continue
            clean_existing.append(keyword)

        terms = list(dict.fromkeys([word for word, _ in ranked] + clean_existing))
        return terms[:24]

    def _entities(self, text: str) -> List[str]:
        candidates = re.findall(r"\b[A-Z][A-Za-z0-9&/-]*(?:\s+[A-Z][A-Za-z0-9&/-]*){0,4}\b", text or "")
        cleaned = []
        for item in candidates:
            item = item.strip()
            if len(item) < 3 or item.lower() in {"the", "this", "that"}:
                continue
            cleaned.append(item)
        return list(dict.fromkeys(cleaned))[:20]

    def _quality_drivers(
        self,
        semantic_profile: Dict[str, Any],
        top_sector_score: float,
        buyer_signals: Dict[str, Any],
        product_signals: Dict[str, Any],
        control_signals: Dict[str, Any],
        evidence_signals: Dict[str, Any],
        technical_signals: Dict[str, Any],
        connector_sources: Optional[Dict[str, Any]] = None,
        event_signal: float = 0.0,
        source_breadth: float = 0.0,
        cross_source_alignment: float = 0.0,
    ) -> List[str]:
        drivers = []
        if semantic_profile.get("specificity_score", 0.0) >= 0.35:
            drivers.append("specific input language")
        if top_sector_score >= 0.30:
            drivers.append("clear sector-routing signal")
        if buyer_signals.get("buyer_present"):
            drivers.append("buyer/workflow signal present")
        if product_signals.get("productizable"):
            drivers.append("productization signal present")
        if control_signals.get("control_gated"):
            drivers.append("control-gated deployment signal present")
        if evidence_signals.get("validation_ready"):
            drivers.append("validation/proof signal present")
        if technical_signals.get("implementation_relevant"):
            drivers.append("technical implementation signal present")
        if event_signal >= 0.55:
            drivers.append("high-confidence connector event signals")
        if source_breadth >= 0.60:
            drivers.append("multi-source connector coverage")
        if cross_source_alignment >= 0.40:
            drivers.append("cross-source signal alignment")

        return drivers or ["basic semantic extraction completed"]

    def _routing_note(self, dominant_sector: str, margin: float) -> str:
        if dominant_sector == "general_intelligence":
            return "No sector-specific routing signal dominated."
        if margin < 0.12:
            return f"{dominant_sector} leads, but cross-sector ambiguity should be monitored."
        return f"{dominant_sector} has the strongest extracted routing evidence."

    def _normalize(self, text: str) -> str:
        return (text or "").lower().replace("—", "-").replace("–", "-")

    def _tokens(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text or "")

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))
