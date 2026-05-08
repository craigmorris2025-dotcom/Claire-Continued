from __future__ import annotations

import hashlib
from typing import List

from .models import EvidencePacket, FetchResult
from .source_reliability import SourceReliabilityEngine


class EvidenceExtractor:
    def __init__(self, reliability_engine: SourceReliabilityEngine | None = None) -> None:
        self.reliability_engine = reliability_engine or SourceReliabilityEngine()

    def extract(self, result: FetchResult, query_terms: List[str] | None = None) -> List[EvidencePacket]:
        terms = query_terms or []
        reliability = self.reliability_engine.score(result.domain, result.content)

        if result.status not in {"stubbed_success", "success"}:
            return []

        claim = self._claim_from_content(result.content)
        evidence_id = "evidence_" + hashlib.sha256(
            f"{result.request_id}|{claim}|{result.source_url}".encode("utf-8")
        ).hexdigest()[:12]

        confidence = min(1.0, max(0.0, reliability * 0.75 + (0.05 * len(terms))))

        return [
            EvidencePacket(
                evidence_id=evidence_id,
                claim=claim,
                source_url=result.source_url,
                domain=result.domain,
                reliability_score=reliability,
                confidence=round(confidence, 4),
                supporting_terms=terms,
                lineage={
                    "request_id": result.request_id,
                    "policy_decision": result.policy_decision,
                    "fetch_status": result.status,
                },
            )
        ]

    def _claim_from_content(self, content: str) -> str:
        text = " ".join(content.split())
        if len(text) > 240:
            return text[:237] + "..."
        return text or "No extractable claim."
