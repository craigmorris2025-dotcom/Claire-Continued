"""Research result contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ResearchResult:
    title: str
    source_type: str
    summary: str
    relevance: float = 0.0
    source_credibility: float = 0.0
    freshness: float = 0.0
    url: str | None = None
    internal_path: str | None = None
    extracted_entities: List[str] = field(default_factory=list)
    extracted_signals: List[str] = field(default_factory=list)
    related_lifecycle_route: str = "trend_thesis"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source_type": self.source_type,
            "url": self.url,
            "internal_path": self.internal_path,
            "summary": self.summary,
            "relevance": round(float(self.relevance or 0.0), 4),
            "source_credibility": round(float(self.source_credibility or 0.0), 4),
            "freshness": round(float(self.freshness or 0.0), 4),
            "extracted_entities": self.extracted_entities,
            "extracted_signals": self.extracted_signals,
            "related_lifecycle_route": self.related_lifecycle_route,
            "metadata": self.metadata,
        }
