"""
Core — Semantic Layer: NLP processing, domain scoring, keyword extraction.
8 domain lexicons, entity extraction, TF-IDF inspired scoring.
"""
import logging
import re
from collections import Counter
from typing import Any, Dict, List
from backend.claire.contract import SemanticRepresentation

logger = logging.getLogger("claire.core.semantic")

DOMAIN_LEXICONS = {
    "defense": {
        "military", "defense", "security", "weapon", "drone", "surveillance",
        "classified", "clearance", "dod", "pentagon", "nato", "combat",
        "tactical", "strategic", "missile", "radar", "intelligence", "cyber",
        "warfare", "autonomous", "swarm", "encrypted", "sovereign",
    },
    "technology": {
        "ai", "machine learning", "deep learning", "algorithm", "software",
        "platform", "cloud", "api", "data", "neural", "quantum", "compute",
        "processor", "semiconductor", "automation", "robotics", "iot",
        "blockchain", "mesh", "network", "edge", "model", "gpu",
    },
    "healthcare": {
        "patient", "clinical", "diagnostic", "treatment", "therapeutic",
        "pharmaceutical", "biotech", "medical", "health", "genomic",
        "drug", "fda", "trial", "hospital", "telemedicine",
    },
    "finance": {
        "investment", "portfolio", "capital", "fund", "equity", "valuation",
        "revenue", "market", "acquisition", "merger", "ipo", "fintech",
        "banking", "trading", "asset", "risk", "roi", "yield",
    },
    "energy": {
        "renewable", "solar", "wind", "battery", "grid", "power",
        "energy", "nuclear", "hydrogen", "carbon", "emissions",
        "sustainability", "clean", "fossil", "turbine",
    },
    "aerospace": {
        "satellite", "orbit", "launch", "rocket", "space", "payload",
        "propulsion", "avionics", "aircraft", "flight", "navigation",
        "trajectory", "hypersonic", "reentry",
    },
    "infrastructure": {
        "infrastructure", "bridge", "road", "construction", "utility",
        "water", "pipeline", "telecom", "broadband", "fiber", "5g",
        "critical", "resilience", "smart city", "transportation",
    },
    "government": {
        "federal", "government", "agency", "regulation", "compliance",
        "procurement", "contract", "grant", "policy", "legislation",
        "congress", "executive", "judiciary", "state", "municipal",
    },
}

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "neither", "each", "every", "all", "any", "few", "more", "most",
    "other", "some", "such", "no", "only", "own", "same", "than",
    "too", "very", "just", "because", "as", "until", "while",
    "of", "at", "by", "for", "with", "about", "against", "between",
    "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "what", "which", "who", "whom", "this",
    "that", "these", "those", "it", "its",
}


class SemanticLayer:
    """Full NLP pipeline: tokenize -> entities -> domain scoring -> keywords."""

    def process(self, text: str) -> SemanticRepresentation:
        tokens = self._tokenize(text)
        entities = self._extract_entities(text)
        dimensions = self._score_domains(tokens)
        domain = max(dimensions, key=dimensions.get) if dimensions else "general"
        keywords = self._extract_keywords(tokens, top_n=15)
        max_s = max(dimensions.values()) if dimensions else 0
        avg_s = sum(dimensions.values()) / len(dimensions) if dimensions else 0
        confidence = round(min(1.0, max_s * 0.6 + avg_s * 0.4 + 0.1), 4)

        result = SemanticRepresentation(
            dimensions=dimensions, keywords=keywords,
            domain=domain, entities=entities, confidence=confidence,
        )
        logger.info(f"Semantic: domain={domain}, confidence={confidence:.3f}, kw={len(keywords)}")
        return result

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text.lower())
        return [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]

    def _extract_entities(self, text: str) -> List[str]:
        caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
        return list(set(caps[:10] + acronyms[:10]))

    def _score_domains(self, tokens: List[str]) -> Dict[str, float]:
        token_set = set(tokens)
        bigrams = {f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)} if len(tokens) > 1 else set()
        combined = token_set | bigrams
        scores = {}
        for domain, lexicon in DOMAIN_LEXICONS.items():
            hits = combined & lexicon
            scores[domain] = round(min(1.0, (len(hits) / max(len(lexicon), 1)) * 3.0), 4) if hits else 0.0
        return scores

    def _extract_keywords(self, tokens: List[str], top_n: int = 15) -> List[str]:
        return [w for w, _ in Counter(tokens).most_common(top_n)]

    def get_status(self) -> Dict[str, Any]:
        return {"component": "SemanticLayer", "status": "active",
                "domains": len(DOMAIN_LEXICONS),
                "lexicon_size": sum(len(v) for v in DOMAIN_LEXICONS.values())}
