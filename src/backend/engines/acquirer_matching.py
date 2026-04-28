"""
Acquirer Matching Engine — ranks potential acquirers by multi-dimensional strategic fit.
Consumes all connector data for enriched matching against 12 strategic profiles.
"""
from typing import Any, Dict, List
from backend.engines.base import BaseEngine


class AcquirermatchingEngine(BaseEngine):
    """Domain engine: acquirer_matching — strategic acquirer ranking."""

    KEYWORDS = {"acquirer", "buyer", "candidate", "fit", "match", "prospect",
                "suitor", "target", "strategic buyer", "financial sponsor"}

    def get_key(self) -> str:
        return "acquirer_matching"

    def get_phase(self) -> str:
        return "deal_construction"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from backend.core.data_engine import DataEngine
        de = DataEngine()
        acquirers = de.load_acquirers()
        domain = context.get("primary_domain", "technology")
        text_lower = context.get("raw_input", "").lower()
        keywords = set(context.get("keywords", []))

        # Connector data for matching enrichment
        market = self._get_market_data(context)
        patent = self._get_patent_data(context)
        financial = self._get_financial_data(context)

        matches: List[Dict] = []
        for acq in acquirers:
            # 1. Domain alignment
            acq_sector = acq.get("sector", "").lower()
            domain_match = 0.25 if domain.lower() in acq_sector else 0.0

            # 2. Focus area keyword matching
            focus_match = 0.0
            matched_focus: List[str] = []
            for f in acq.get("focus", []):
                f_lower = f.lower()
                if f_lower in text_lower:
                    focus_match += 0.08
                    matched_focus.append(f)
                elif any(kw in f_lower for kw in keywords if len(kw) > 3):
                    focus_match += 0.04
                    matched_focus.append(f)
            focus_match = min(0.30, focus_match)

            # 3. Base profile scores
            base_fit = acq.get("fit", 0.5)
            capacity = acq.get("capacity", 0.5)
            strategy_align = acq.get("strategy_alignment", 0.5)
            tech_align = acq.get("tech_alignment", 0.5)

            # 4. Market-informed matching
            market_adj = 0.0
            if market:
                sector_pe = market.get("sector_pe", 0)
                if sector_pe > 20:
                    market_adj = 0.03  # hot sector = more acquirer interest

            # 5. Deal size feasibility (from financial connector)
            size_adj = 0.0
            if financial:
                avg_deal = financial.get("avg_deal_size_m", 0)
                cap = acq.get("capacity", 0.5)
                if cap > 0.7 and avg_deal < 5000:
                    size_adj = 0.04

            # Composite match score
            total = self._clamp(
                base_fit * 0.20 +
                domain_match +
                focus_match +
                strategy_align * 0.10 +
                tech_align * 0.08 +
                capacity * 0.05 +
                market_adj + size_adj
            )

            match_entry = dict(acq)
            match_entry["match_score"] = round(total, 4)
            match_entry["matched_focus"] = matched_focus[:5]
            match_entry["domain_match"] = domain.lower() in acq_sector
            matches.append(match_entry)

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        context["acquirer_matches"] = matches[:12]
        context["acquirer_match_count"] = len(matches)

        top_score = matches[0]["match_score"] if matches else 0.0
        top3_avg = (sum(m["match_score"] for m in matches[:3]) / 3
                    if len(matches) >= 3 else top_score)

        return self._score_with_detail(context, top3_avg, {
            "acquirers_evaluated": len(matches),
            "top_match": matches[0]["ticker"] if matches else "none",
            "top_score": round(top_score, 3),
            "top3_avg": round(top3_avg, 3),
        })
