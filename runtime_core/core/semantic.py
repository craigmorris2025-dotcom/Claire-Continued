"""
Semantic Layer — domain detection + keyword extraction.
"""
import re
from collections import Counter
from typing import List, Dict


DOMAIN_LEXICONS = {
    "defense": {"defense", "drone", "autonomous", "military", "sensor", "c4isr"},
    "technology": {"ai", "software", "platform", "cloud", "data", "network"},
}


class SemanticLayer:

    def process(self, text: str):
        tokens = self._tokenize(text)

        dimensions = self._score_domains(tokens)

        # 🔥 Hard bias for defense if detected
        if any(k in text.lower() for k in ["defense", "drone", "autonomous"]):
            domain = "defense"
        else:
            domain = max(dimensions, key=dimensions.get) if dimensions else "technology"

        keywords = self._extract_keywords(tokens)

        return {
            "domain": domain,
            "keywords": keywords,
            "dimensions": dimensions,
            "confidence": 0.7
        }

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
        return text.split()

    def _score_domains(self, tokens: List[str]) -> Dict[str, float]:
        scores = {}
        token_set = set(tokens)
        for domain, lexicon in DOMAIN_LEXICONS.items():
            hits = token_set & lexicon
            scores[domain] = len(hits) / max(len(lexicon), 1)
        return scores

    def _extract_keywords(self, tokens: List[str]) -> List[str]:
        return [w for w, _ in Counter(tokens).most_common(10)]
