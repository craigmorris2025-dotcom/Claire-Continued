"""
Acquirer Matching Engine — ranks likely strategic acquirers.
"""

from typing import Dict, List, Any


class AcquirerMatchingEngine:
    """Simple deterministic acquirer matcher."""

    DEFAULT_ACQUIRERS = [
        {
            "name": "Lockheed Martin",
            "ticker": "LMT",
            "sector": "defense",
            "focus": ["autonomous systems", "drones", "sensor fusion", "battlefield intelligence"],
            "base_fit": 0.86,
        },
        {
            "name": "Northrop Grumman",
            "ticker": "NOC",
            "sector": "defense",
            "focus": ["aerospace", "autonomous platforms", "surveillance", "command systems"],
            "base_fit": 0.84,
        },
        {
            "name": "RTX",
            "ticker": "RTX",
            "sector": "defense",
            "focus": ["sensors", "missiles", "defense systems", "edge computing"],
            "base_fit": 0.80,
        },
        {
            "name": "Anduril",
            "ticker": "PRIVATE",
            "sector": "defense technology",
            "focus": ["autonomous defense", "drones", "ai", "border security"],
            "base_fit": 0.90,
        },
        {
            "name": "Palantir",
            "ticker": "PLTR",
            "sector": "data / defense software",
            "focus": ["battlefield intelligence", "ai", "data fusion", "decision systems"],
            "base_fit": 0.82,
        },
    ]

    def match(self, keywords: List[str], domain: str = "technology") -> List[Dict[str, Any]]:
        keywords_lower = [k.lower() for k in keywords]
        results = []

        for acquirer in self.DEFAULT_ACQUIRERS:
            focus_terms = [f.lower() for f in acquirer.get("focus", [])]

            matched = []
            for kw in keywords_lower:
                for focus in focus_terms:
                    if kw in focus or focus in kw:
                        matched.append(kw)

            domain_boost = 0.08 if domain.lower() in acquirer.get("sector", "").lower() else 0.0
            keyword_boost = min(0.12, len(set(matched)) * 0.03)

            score = min(0.98, acquirer["base_fit"] + domain_boost + keyword_boost)

            results.append({
                "name": acquirer["name"],
                "ticker": acquirer["ticker"],
                "sector": acquirer["sector"],
                "match_score": round(score, 4),
                "matched_keywords": sorted(list(set(matched))),
                "focus": acquirer["focus"],
            })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results