"""
Knowledge Ingestion Engine — dedicated Stage 1 engine for Claire.

v5.28:
- Converts Stage 1 from partial connector/source availability into a real engine.
- Normalizes raw input, connector payloads, source availability, source quality,
  and ingestion metadata into a structured ingestion contract.
- Provides downstream engines with explicit source-health, coverage, lineage,
  and evidence-readiness diagnostics.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import hashlib
import re


class KnowledgeIngestionEngine:
    """Deterministic raw-input and connector-source ingestion analyzer."""

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = text or ""
        keywords = keywords or []
        connector_sources = connector_sources or {}
        metadata = metadata or {}

        normalized = self._normalize_text(text)
        source_inventory = self._source_inventory(connector_sources)
        input_profile = self._input_profile(text, normalized, keywords)
        source_quality = self._source_quality(source_inventory, connector_sources)
        coverage = self._coverage(domain, keywords, connector_sources, input_profile)
        ingestion_score = self._ingestion_score(input_profile, source_quality, coverage)
        lineage = self._lineage(text, domain, keywords, connector_sources, metadata)

        return {
            "status": "success",
            "domain": domain,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "input_profile": input_profile,
            "source_inventory": source_inventory,
            "source_quality": source_quality,
            "coverage_assessment": coverage,
            "knowledge_quality_score": ingestion_score,
            "ingestion_contract": self._ingestion_contract(
                domain=domain,
                input_profile=input_profile,
                source_inventory=source_inventory,
                source_quality=source_quality,
                coverage=coverage,
            ),
            "lineage": lineage,
            "normalized_input": {
                "text_hash": lineage["input_hash"],
                "preview": normalized[:240],
                "keyword_count": len(keywords),
                "keywords": keywords[:24],
            },
            "data_readiness": self._data_readiness(source_inventory, source_quality, coverage),
            "downstream_hints": self._downstream_hints(domain, source_inventory, source_quality, coverage),
            "recommended_next_actions": self._recommended_next_actions(input_profile, source_inventory, coverage),
            "knowledge_ingestion_thesis": self._thesis(domain, ingestion_score, source_inventory, coverage),
            "confidence": self._confidence(ingestion_score, source_quality, coverage),
        }

    # =========================
    # Core builders
    # =========================
    def _input_profile(self, raw_text: str, normalized: str, keywords: List[str]) -> Dict[str, Any]:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", normalized)
        sentences = [p.strip() for p in re.split(r"[.!?]+", raw_text or "") if p.strip()]
        unique_tokens = set(tokens)

        return {
            "raw_character_count": len(raw_text or ""),
            "normalized_character_count": len(normalized or ""),
            "token_count": len(tokens),
            "unique_token_count": len(unique_tokens),
            "sentence_count": len(sentences),
            "keyword_count": len(keywords),
            "has_substantive_input": len(tokens) >= 12,
            "specificity_score": round(self._bounded(
                min(0.45, len([t for t in unique_tokens if len(t) >= 8]) * 0.012)
                + min(0.25, len(keywords) * 0.012)
                + min(0.20, len(sentences) * 0.035)
                + min(0.10, len(raw_text) / 1200.0)
            ), 4),
            "structure_score": round(self._bounded(
                min(0.45, len(sentences) * 0.06)
                + min(0.35, len(tokens) / 180.0)
                + (0.12 if ":" in raw_text or ";" in raw_text else 0.0)
            ), 4),
        }

    def _source_inventory(self, connector_sources: Dict[str, Any]) -> Dict[str, Any]:
        available = []
        empty = []
        source_details: Dict[str, Any] = {}

        for source_name, payload in (connector_sources or {}).items():
            has_payload = bool(payload)
            if has_payload:
                available.append(source_name)
            else:
                empty.append(source_name)

            numeric_fields = {}
            text_fields = {}
            if isinstance(payload, dict):
                for key, value in payload.items():
                    if isinstance(value, (int, float)):
                        numeric_fields[key] = value
                    elif isinstance(value, str):
                        text_fields[key] = value

            source_details[source_name] = {
                "available": has_payload,
                "field_count": len(payload) if isinstance(payload, dict) else 0,
                "numeric_fields": numeric_fields,
                "text_fields": text_fields,
            }

        expected = ["market", "patent", "financial"]
        missing_expected = [name for name in expected if name not in (connector_sources or {})]

        return {
            "available_sources": available,
            "empty_sources": empty,
            "missing_expected_sources": missing_expected,
            "source_count": len(available),
            "expected_source_count": len(expected),
            "source_details": source_details,
        }

    def _source_quality(
        self,
        source_inventory: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        patent = connector_sources.get("patent", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        market_quality = self._bounded(
            0.18
            + float(market.get("growth", 0.0) or 0.0) * 0.35
            + max(0.0, 1.0 - float(market.get("volatility", 0.5) or 0.5)) * 0.20
            + (0.15 if "alignment" in market else 0.0)
        )
        patent_quality = self._bounded(
            0.18
            + float(patent.get("activity", 0.0) or 0.0) * 0.30
            + float(patent.get("novelty", 0.0) or 0.0) * 0.30
        )
        financial_quality = self._bounded(
            0.18
            + float(financial.get("health", 0.0) or 0.0) * 0.35
            + max(0.0, 1.0 - float(financial.get("risk", 0.5) or 0.5)) * 0.25
        )

        source_count = source_inventory.get("source_count", 0)
        coverage_quality = self._bounded(source_count / max(1, source_inventory.get("expected_source_count", 3)))

        combined = self._bounded(
            0.10
            + coverage_quality * 0.25
            + market_quality * 0.18
            + patent_quality * 0.22
            + financial_quality * 0.18
        )

        level = "strong" if combined >= 0.72 else "usable" if combined >= 0.55 else "limited" if combined >= 0.38 else "weak"

        return {
            "level": level,
            "score": round(combined, 4),
            "coverage_quality": round(coverage_quality, 4),
            "market_quality": round(market_quality, 4),
            "patent_quality": round(patent_quality, 4),
            "financial_quality": round(financial_quality, 4),
            "source_count": source_count,
            "quality_drivers": self._quality_drivers(market, patent, financial, source_count),
        }

    def _coverage(
        self,
        domain: str,
        keywords: List[str],
        connector_sources: Dict[str, Any],
        input_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        patent = connector_sources.get("patent", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        market_present = bool(market)
        patent_present = bool(patent)
        financial_present = bool(financial)

        coverage_score = self._bounded(
            0.12
            + (0.16 if input_profile.get("has_substantive_input") else 0.0)
            + input_profile.get("specificity_score", 0.0) * 0.16
            + input_profile.get("structure_score", 0.0) * 0.10
            + (0.16 if market_present else 0.0)
            + (0.16 if patent_present else 0.0)
            + (0.16 if financial_present else 0.0)
            + min(0.10, len(keywords) * 0.006)
        )

        level = "broad" if coverage_score >= 0.74 else "sufficient" if coverage_score >= 0.58 else "thin" if coverage_score >= 0.40 else "insufficient"

        return {
            "level": level,
            "score": round(coverage_score, 4),
            "domain": domain,
            "market_present": market_present,
            "patent_present": patent_present,
            "financial_present": financial_present,
            "keyword_coverage": min(24, len(keywords)),
            "coverage_gaps": self._coverage_gaps(market_present, patent_present, financial_present, input_profile),
        }

    def _ingestion_score(
        self,
        input_profile: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = self._bounded(
            0.12
            + input_profile.get("specificity_score", 0.0) * 0.16
            + input_profile.get("structure_score", 0.0) * 0.12
            + source_quality.get("score", 0.0) * 0.34
            + coverage.get("score", 0.0) * 0.26
        )
        level = "strong" if score >= 0.72 else "usable" if score >= 0.56 else "limited" if score >= 0.40 else "weak"

        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._ingestion_drivers(input_profile, source_quality, coverage),
        }

    def _ingestion_contract(
        self,
        domain: str,
        input_profile: Dict[str, Any],
        source_inventory: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "domain": domain,
            "has_raw_input": input_profile.get("has_substantive_input", False),
            "has_connector_sources": source_inventory.get("source_count", 0) > 0,
            "source_count": source_inventory.get("source_count", 0),
            "coverage_level": coverage.get("level"),
            "source_quality_level": source_quality.get("level"),
            "safe_for_downstream_scoring": coverage.get("score", 0.0) >= 0.40 and input_profile.get("has_substantive_input", False),
            "requires_source_enrichment": coverage.get("level") in {"thin", "insufficient"} or source_quality.get("level") in {"limited", "weak"},
        }

    def _lineage(
        self,
        text: str,
        domain: str,
        keywords: List[str],
        connector_sources: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        source_names = sorted(list((connector_sources or {}).keys()))
        input_hash = hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]

        return {
            "input_hash": input_hash,
            "domain": domain,
            "keyword_sample": keywords[:12],
            "source_names": source_names,
            "metadata_keys": sorted(list((metadata or {}).keys())),
            "lineage_note": "Raw input, extracted keywords, connector-source names, and metadata keys were recorded for deterministic traceability.",
        }

    # =========================
    # Interpretation helpers
    # =========================
    def _data_readiness(
        self,
        source_inventory: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> Dict[str, Any]:
        if source_quality.get("score", 0.0) >= 0.70 and coverage.get("score", 0.0) >= 0.65:
            state = "ready_for_scoring"
        elif source_quality.get("score", 0.0) >= 0.50 and coverage.get("score", 0.0) >= 0.50:
            state = "usable_for_scoring"
        elif source_inventory.get("source_count", 0) > 0:
            state = "limited_sources_available"
        else:
            state = "raw_input_only"

        return {
            "state": state,
            "source_quality_level": source_quality.get("level"),
            "coverage_level": coverage.get("level"),
            "minimum_viable_ingestion": source_inventory.get("source_count", 0) > 0 or coverage.get("score", 0.0) >= 0.40,
        }

    def _downstream_hints(
        self,
        domain: str,
        source_inventory: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        hints = []

        if source_inventory.get("source_count", 0) > 0:
            hints.append({
                "area": "connector_sources",
                "hint": "Connector source payloads are available for market, patent, financial, or similar downstream enrichment.",
                "priority": "high",
            })

        if source_quality.get("level") in {"limited", "weak"}:
            hints.append({
                "area": "source_quality",
                "hint": "Treat quantitative source-derived conclusions as early until connector quality is enriched.",
                "priority": "medium",
            })

        if coverage.get("level") in {"thin", "insufficient"}:
            hints.append({
                "area": "coverage",
                "hint": "Downstream engines should rely more heavily on raw-input semantics and request stronger evidence before final packaging.",
                "priority": "medium",
            })

        hints.append({
            "area": "domain",
            "hint": f"Use {domain} as the starting domain context unless signal extraction provides stronger sector routing.",
            "priority": "medium",
        })

        return hints

    def _recommended_next_actions(
        self,
        input_profile: Dict[str, Any],
        source_inventory: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        actions = []

        if not input_profile.get("has_substantive_input"):
            actions.append({
                "action": "collect richer raw input",
                "purpose": "improve downstream discovery, routing, and validation quality",
                "priority": "critical",
            })

        if source_inventory.get("source_count", 0) < source_inventory.get("expected_source_count", 3):
            actions.append({
                "action": "enrich connector source coverage",
                "purpose": "increase market, patent, and financial evidence coverage",
                "priority": "medium",
            })

        if coverage.get("level") in {"thin", "insufficient"}:
            actions.append({
                "action": "add evidence-bearing source material",
                "purpose": "support more reliable opportunity, feasibility, and deal-readiness conclusions",
                "priority": "high",
            })

        actions.append({
            "action": "preserve ingestion lineage",
            "purpose": "keep source names, input hash, and metadata traceable through binder/export workflows",
            "priority": "medium",
        })

        return actions

    def _thesis(
        self,
        domain: str,
        ingestion_score: Dict[str, Any],
        source_inventory: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> str:
        return (
            f"Knowledge ingestion for {domain} is {ingestion_score.get('level')} with score "
            f"{ingestion_score.get('score')}. {source_inventory.get('source_count', 0)} connector source(s) "
            f"were available and coverage is {coverage.get('level')}. This input is suitable for downstream "
            f"deterministic scoring when paired with signal extraction and lifecycle traceability."
        )

    def _quality_drivers(
        self,
        market: Dict[str, Any],
        patent: Dict[str, Any],
        financial: Dict[str, Any],
        source_count: int,
    ) -> List[str]:
        drivers = []
        if source_count:
            drivers.append(f"{source_count} connector source(s) available")
        if float(patent.get("activity", 0.0) or 0.0) >= 0.60:
            drivers.append("patent activity signal available")
        if float(patent.get("novelty", 0.0) or 0.0) >= 0.50:
            drivers.append("patent novelty signal available")
        if float(financial.get("health", 0.0) or 0.0) >= 0.50:
            drivers.append("financial health signal available")
        if "growth" in market:
            drivers.append("market growth signal available")
        return drivers or ["raw input available"]

    def _coverage_gaps(
        self,
        market_present: bool,
        patent_present: bool,
        financial_present: bool,
        input_profile: Dict[str, Any],
    ) -> List[str]:
        gaps = []
        if not market_present:
            gaps.append("market source missing")
        if not patent_present:
            gaps.append("patent source missing")
        if not financial_present:
            gaps.append("financial source missing")
        if not input_profile.get("has_substantive_input"):
            gaps.append("raw input is too thin")
        return gaps or ["no major ingestion coverage gap surfaced"]

    def _ingestion_drivers(
        self,
        input_profile: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> List[str]:
        drivers = []
        if input_profile.get("has_substantive_input"):
            drivers.append("substantive raw input")
        if input_profile.get("specificity_score", 0.0) >= 0.45:
            drivers.append("specific language in input")
        if source_quality.get("score", 0.0) >= 0.55:
            drivers.append("usable connector source quality")
        if coverage.get("score", 0.0) >= 0.58:
            drivers.append("sufficient source/input coverage")
        if coverage.get("coverage_gaps"):
            gaps = [g for g in coverage.get("coverage_gaps", []) if "no major" not in g]
            if gaps:
                drivers.append("remaining coverage gaps: " + ", ".join(gaps[:3]))
        return drivers or ["baseline ingestion completed"]

    def _confidence(
        self,
        ingestion_score: Dict[str, Any],
        source_quality: Dict[str, Any],
        coverage: Dict[str, Any],
    ) -> float:
        return round(self._bounded(
            0.22
            + ingestion_score.get("score", 0.0) * 0.24
            + source_quality.get("score", 0.0) * 0.14
            + coverage.get("score", 0.0) * 0.14
        ), 4)

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").replace("—", "-").replace("–", "-")).strip().lower()

    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))
