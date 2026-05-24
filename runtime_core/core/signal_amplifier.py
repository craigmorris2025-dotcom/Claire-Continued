import re
from collections import Counter
from typing import Dict, List


class SignalAmplifier:

    def __init__(self):
        self.domain_map = {
            "artificial_intelligence": ["ai", "machine learning", "llm", "neural", "automation"],
            "finance": ["fintech", "trading", "banking", "payments", "crypto"],
            "healthcare": ["health", "medical", "biotech", "pharma"],
            "energy": ["energy", "battery", "solar", "grid"],
            "aerospace": ["satellite", "space", "orbital", "launch"],
            "defense": ["defense", "military", "weapon", "security"],
            "infrastructure": ["construction", "transport", "logistics"],
        }

    def amplify(self, text: str) -> Dict:

        clean = text.lower()

        # ---- KEYWORD EXTRACTION ----
        words = re.findall(r"\b[a-z]{3,}\b", clean)
        freq = Counter(words)
        keywords = [w for w, _ in freq.most_common(10)]

        # ---- DOMAIN SCORING ----
        domain_scores = {}
        for domain, triggers in self.domain_map.items():
            score = sum(clean.count(t) for t in triggers)
            if score > 0:
                domain_scores[domain] = score

        # Normalize
        total = sum(domain_scores.values()) or 1
        domain_scores = {k: v / total for k, v in domain_scores.items()}

        # ---- INTENT CLASSIFICATION ----
        intent_type = "idea"
        if "build" in clean or "create" in clean:
            intent_type = "creation"
        elif "buy" in clean or "acquire" in clean:
            intent_type = "acquisition"
        elif "optimize" in clean or "improve" in clean:
            intent_type = "optimization"

        # ---- ENTITY DETECTION (simple heuristic) ----
        entities = {
            "technologies": [w for w in keywords if w in ["ai", "ml", "blockchain", "robotics"]],
            "markets": [w for w in keywords if w in ["finance", "health", "energy"]],
            "users": [w for w in keywords if w in ["enterprise", "consumer", "government"]],
        }

        # ---- SIGNAL STRENGTH ----
        signal_strength = min(1.0, len(keywords) / 10 + sum(domain_scores.values()))

        # ---- ENRICHED TEXT ----
        enriched = text + " | " + " ".join(keywords)

        return {
            "keywords": keywords,
            "domain_scores": domain_scores,
            "intent_type": intent_type,
            "entities": entities,
            "signal_strength": signal_strength,
            "enriched_input": enriched,
        }
