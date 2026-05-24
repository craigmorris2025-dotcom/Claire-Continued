from __future__ import annotations

import hashlib
from typing import List
from urllib.parse import urlparse

from .models import EvidenceRecord, FetchResult, SearchResult
from .normalizer import ContentNormalizer
from .reliability import SourceReliabilityScorer


class EvidenceExtractor:
    def __init__(self) -> None:
        self.normalizer = ContentNormalizer()
        self.reliability = SourceReliabilityScorer()

    def extract(
        self,
        run_id: str,
        query: str,
        fetch: FetchResult,
        search_result: SearchResult | None = None,
    ) -> List[EvidenceRecord]:
        if fetch.status != "success":
            return []

        title, text, terms = self.normalizer.normalize(fetch.text, fetch.content_type)
        if not text:
            return []

        domain = urlparse(fetch.url).netloc.lower().replace("www.", "")
        rank = search_result.rank if search_result else 0
        reliability = self.reliability.score(domain, content_length=len(text), search_rank=rank)

        claim = self._best_claim(text, query)
        summary = text[:700] + ("..." if len(text) > 700 else "")

        confidence = round(
            max(0.0, min(1.0, reliability * 0.75 + self._term_overlap(query, terms) * 0.25)),
            4,
        )

        evidence_id = "ev_" + hashlib.sha256(
            f"{run_id}|{fetch.url}|{claim}".encode("utf-8")
        ).hexdigest()[:16]

        return [
            EvidenceRecord(
                evidence_id=evidence_id,
                run_id=run_id,
                query=query,
                source_url=fetch.url,
                title=title or (search_result.title if search_result else "Untitled source"),
                claim=claim,
                summary=summary,
                source_domain=domain,
                source_reliability=reliability,
                confidence=confidence,
                supporting_terms=terms[:12],
                conflicting_terms=[],
                lineage={
                    "http_status": fetch.http_status,
                    "content_type": fetch.content_type,
                    "search_source": search_result.source if search_result else "direct_url",
                    "search_rank": rank,
                    "fetch_policy": fetch.policy,
                    "binary_size": fetch.binary_size,
                },
            )
        ]

    def _best_claim(self, text: str, query: str) -> str:
        cleaned_text = text.replace("\n", " ")
        sentences = [item.strip() for item in cleaned_text.split(".") if len(item.strip()) > 40]
        query_terms = {term.lower() for term in query.split() if len(term) > 3}

        if not sentences:
            return text[:300] + ("..." if len(text) > 300 else "")

        def score(sentence: str) -> int:
            low = sentence.lower()
            return sum(1 for term in query_terms if term in low)

        best = sorted(sentences, key=score, reverse=True)[0]
        return best[:500] + ("..." if len(best) > 500 else "")

    def _term_overlap(self, query: str, terms: List[str]) -> float:
        query_terms = {
            term.lower().strip(".,:;!?")
            for term in query.split()
            if len(term) > 3
        }
        source_terms = set(terms)

        if not query_terms:
            return 0.0

        return len(query_terms & source_terms) / len(query_terms)
