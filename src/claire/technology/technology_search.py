"""Technology catalog search utilities."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List

from .technology_catalog import TechnologyCatalog


class TechnologySearch:
    """Exact, fuzzy, keyword, category, tag, and compatibility search."""

    def __init__(self, catalog: TechnologyCatalog | None = None) -> None:
        self.catalog = catalog or TechnologyCatalog()

    def exact(self, query: str) -> List[Dict[str, Any]]:
        q = self._norm(query)
        return [item for item in self.catalog.all() if self._norm(item["name"]) == q or item["id"] == q]

    def fuzzy(self, query: str, threshold: float = 0.58) -> List[Dict[str, Any]]:
        q = self._norm(query)
        scored = []
        for item in self.catalog.all():
            hay = " ".join([item["id"], item["name"], item["description"], " ".join(item.get("tags", []))]).lower()
            score = max(SequenceMatcher(None, q, item["id"]).ratio(), SequenceMatcher(None, q, self._norm(item["name"])).ratio(), SequenceMatcher(None, q, hay).ratio())
            if score >= threshold:
                row = dict(item)
                row["match_score"] = round(score, 4)
                scored.append(row)
        return sorted(scored, key=lambda item: item.get("match_score", 0), reverse=True)

    def keyword(self, query: str | Iterable[str], limit: int = 8) -> List[Dict[str, Any]]:
        terms = self._terms(query)
        scored = []
        for item in self.catalog.all():
            hay = self._terms([
                item.get("id"),
                item.get("name"),
                item.get("category"),
                item.get("description"),
                item.get("tags", []),
                item.get("use_cases", []),
                item.get("platforms", []),
            ])
            score = len(terms.intersection(hay))
            if score:
                row = dict(item)
                row["match_score"] = round(min(1.0, score / max(1, len(terms))), 4)
                scored.append(row)
        return sorted(scored, key=lambda item: item.get("match_score", 0), reverse=True)[:limit]

    def category(self, category: str) -> List[Dict[str, Any]]:
        q = self._norm(category)
        return [item for item in self.catalog.all() if self._norm(item.get("category")) == q]

    def tag(self, tag: str) -> List[Dict[str, Any]]:
        q = self._norm(tag)
        return [item for item in self.catalog.all() if q in {self._norm(t) for t in item.get("tags", [])}]

    def compatibility(self, technology_id: str) -> List[Dict[str, Any]]:
        base = self.catalog.by_id(self._norm(technology_id))
        compatible = set(base.get("compatible_with", []))
        return [item for item in self.catalog.all() if item["id"] in compatible]

    def _norm(self, value: Any) -> str:
        return str(value or "").strip().lower().replace(" ", "_")

    def _terms(self, value: Any) -> set[str]:
        if isinstance(value, str):
            raw = value.replace("_", " ").replace("-", " ").split()
        elif isinstance(value, Iterable):
            raw = []
            for item in value:
                raw.extend(self._terms(item))
        else:
            raw = []
        return {str(term).strip().lower() for term in raw if str(term).strip()}
