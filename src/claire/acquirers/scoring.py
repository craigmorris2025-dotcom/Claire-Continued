
"""
Acquirer Scoring — calculates fit, alignment, and acquisition likelihood.
"""

from typing import Dict, List


class AcquirerScorer:
    """Scores how well an acquirer matches an opportunity."""

    def score(self, acquirer: Dict, context: Dict) -> Dict:
        keywords = context.get("keywords", [])
        domain = context.get("domain", "")

        focus = acquirer.get("focus", [])
        capacity = acquirer.get("capacity", 0.5)

        # Keyword alignment
        matches = sum(1 for k in keywords if k.lower() in focus)
        keyword_score = matches / max(len(keywords), 1)

        # Domain alignment
        domain_score = 1.0 if domain == acquirer.get("sector") else 0.5

        # Final score blend
        fit = round(
            keyword_score * 0.4 +
            domain_score * 0.3 +
            capacity * 0.3,
            4
        )

        return {
            "name": acquirer.get("name"),
            "ticker": acquirer.get("ticker"),
            "fit": fit,
            "capacity": capacity,
            "strategy_alignment": keyword_score,
            "tech_alignment": domain_score,
            "focus": focus,
        }
