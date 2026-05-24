from __future__ import annotations

from typing import Optional


class SourceReliabilityEngine:
    HIGH_TRUST = {
        "sec.gov": 0.95,
        "federalregister.gov": 0.93,
        "congress.gov": 0.92,
        "nist.gov": 0.92,
        "nih.gov": 0.92,
        "who.int": 0.9,
        "oecd.org": 0.88,
        "worldbank.org": 0.88,
        "imf.org": 0.88,
        "reuters.com": 0.82,
        "apnews.com": 0.82,
    }

    def score(self, domain: Optional[str], content: str = "") -> float:
        if not domain:
            return 0.45

        base = self.HIGH_TRUST.get(domain, 0.55)

        if not content:
            return round(max(0.1, base - 0.1), 4)

        if "STUB_FETCH_RESULT" in content:
            return round(min(base, 0.5), 4)

        if len(content) < 200:
            return round(max(0.1, base - 0.08), 4)

        return round(base, 4)
