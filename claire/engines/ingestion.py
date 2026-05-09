"""
Ingestion Engine — scores data input quality, completeness, and analytical potential.
"""
from typing import Any, Dict
from claire.engines.base import BaseEngine


class IngestionEngine(BaseEngine):
    """Domain engine: ingestion — evaluates raw input quality."""

    KEYWORDS = {"data", "document", "extract", "feed", "ingest", "input",
                "parse", "raw", "source", "text", "report", "analysis",
                "brief", "memo", "dossier", "intelligence"}

    def get_key(self) -> str:
        return "ingestion"

    def get_phase(self) -> str:
        return "ingestion_semantic"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "")
        words = text.split()
        word_count = len(words)

        # Length quality — diminishing returns past 500 words
        length_score = min(1.0, word_count / 200) * 0.8 + 0.1

        # Vocabulary richness — unique words / total
        unique_ratio = len(set(w.lower() for w in words)) / max(word_count, 1)
        richness = min(1.0, unique_ratio * 1.5)

        # Structural indicators — presence of numbers, punctuation variety
        has_numbers = any(c.isdigit() for c in text)
        sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))
        avg_sentence_len = word_count / sentence_count
        structure = min(1.0, (0.3 if has_numbers else 0.0) +
                        min(0.4, sentence_count * 0.05) +
                        (0.3 if 8 < avg_sentence_len < 40 else 0.1))

        # Keyword signal
        signal = self._text_signal(text, self.KEYWORDS)

        score = (length_score * 0.25 + richness * 0.25 +
                 structure * 0.25 + signal * 0.25)

        context["ingestion_quality"] = {
            "length": len(text),
            "words": word_count,
            "unique_ratio": round(unique_ratio, 3),
            "sentences": sentence_count,
            "has_numbers": has_numbers,
        }
        return self._score_with_detail(context, score, {
            "length_score": round(length_score, 3),
            "richness": round(richness, 3),
            "structure": round(structure, 3),
            "signal": round(signal, 3),
        })
