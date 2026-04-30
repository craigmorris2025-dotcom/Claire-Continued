"""
Acquirer Matching Engine — ensures matches are always produced.
"""
from typing import Dict, Any, List
from claire.engines.base import BaseEngine


class AcquirermatchingEngine(BaseEngine):

    def get_key(self) -> str:
        return "acquirer_matching"

    def get_phase(self) -> str:
        return "deal_construction"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from claire.core.data_engine import DataEngine

        de = DataEngine()
        acquirers = de.load_acquirers()

        matches: List[Dict] = []

        for acq in acquirers:
            score = (
                acq.get("fit", 0.5) * 0.4 +
                acq.get("strategy_alignment", 0.5) * 0.3 +
                acq.get("tech_alignment", 0.5) * 0.2 +
                acq.get("capacity", 0.5) * 0.1
            )

            entry = dict(acq)
            entry["match_score"] = round(score, 4)
            matches.append(entry)

        matches.sort(key=lambda x: x["match_score"], reverse=True)

        context["acquirer_matches"] = matches[:5]

        return self._score_with_detail(context, matches[0]["match_score"], {
            "top_match": matches[0]["ticker"],
            "total": len(matches)
        })
