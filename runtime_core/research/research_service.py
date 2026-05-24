"""Claire Cognitive Research service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List
import json

from runtime_core.runtime.export_browser import ExportBrowser
from runtime_core.technology import TechnologyCatalog, TechnologySearch, StackRecommender, ComponentMatcher

from .evidence_basket import EvidenceBasket
from .research_result import ResearchResult
from .source_governance import SourceGovernance
from .web_search_adapter import WebSearchAdapter


class ResearchService:
    """Internal research/search foundation for Claire lifecycle input."""

    def __init__(self) -> None:
        self.browser = ExportBrowser()
        self.governance = SourceGovernance()
        self.web = WebSearchAdapter()
        self.basket = EvidenceBasket()
        self.tech_catalog = TechnologyCatalog()
        self.tech_search = TechnologySearch(self.tech_catalog)
        self.stack_recommender = StackRecommender(self.tech_catalog)
        self.component_matcher = ComponentMatcher(self.tech_catalog)

    def search(self, query: str, scope: str = "all", limit: int = 20) -> Dict[str, Any]:
        query = (query or "").strip()
        scope = (scope or "all").lower()
        results: List[Dict[str, Any]] = []
        unavailable: List[Dict[str, Any]] = []

        if not query:
            return {"status": "validation_failed", "error": "query is required", "results": []}

        if scope in {"all", "web"}:
            web = self.web.search_web(query)
            if web.get("status") != "success":
                unavailable.append(web)

        if scope in {"all", "runs", "trends", "portfolio", "breakthroughs", "designs", "packages", "system"}:
            results.extend(self._search_runs(query, scope))

        if scope in {"all", "technologies", "designs"}:
            results.extend(self._search_technology(query))

        if scope in {"all", "signals"}:
            results.extend(self._search_signals(query))

        results = sorted(results, key=lambda item: item.get("relevance", 0), reverse=True)[: int(limit or 20)]
        return {
            "status": "success",
            "query": query,
            "scope": scope,
            "result_count": len(results),
            "results": results,
            "unavailable_sources": unavailable,
            "evidence_basket": self.basket.list(),
        }

    def add_evidence(self, result: Dict[str, Any], notes: str = "") -> Dict[str, Any]:
        return self.basket.add(result, notes=notes)

    def evidence(self) -> Dict[str, Any]:
        return self.basket.list()

    def clear_evidence(self) -> Dict[str, Any]:
        return self.basket.clear()

    def evidence_pipeline_input(self) -> Dict[str, Any]:
        return self.basket.as_pipeline_input()

    def send_to_pipeline(self, result: Dict[str, Any], route: str = "scan") -> Dict[str, Any]:
        pipeline_input = {
            "status": "ready_for_pipeline",
            "route": route,
            "raw_input": f"{result.get('title')}\n\n{result.get('summary')}",
            "research_result": result,
            "governed_signal_candidate": {
                "source_type": result.get("source_type"),
                "title": result.get("title"),
                "signals": result.get("extracted_signals", []),
                "entities": result.get("extracted_entities", []),
                "credibility": result.get("source_credibility"),
                "freshness": result.get("freshness"),
            },
        }
        return pipeline_input

    def _search_runs(self, query: str, scope: str) -> List[Dict[str, Any]]:
        payload = self.browser.list_runs(limit=200, rescan_if_empty=True)
        terms = self._terms(query)
        out = []
        for run in payload.get("runs", []):
            text = " ".join(str(run.get(key, "")) for key in ["run_id", "domain", "sector", "category_name", "decision_classification", "breakthrough_classification"])
            if not self._matches(terms, text):
                continue
            core = self._read_core(run.get("run_id") or run.get("folder_name"))
            route = core.get("route_selected") or run.get("decision_classification") or "trend_thesis"
            if scope == "portfolio" and "portfolio" not in route:
                continue
            if scope == "breakthroughs" and not (core.get("breakthrough", {}) or {}).get("is_breakthrough"):
                continue
            if scope == "designs" and not (core.get("design_portal", {}) or {}).get("required"):
                continue
            if scope == "packages" and not run.get("export_package_level"):
                continue
            out.append(self._result({
                "title": core.get("user_facing_result", {}).get("headline") or run.get("category_name") or run.get("run_id"),
                "source_type": "run" if scope != "packages" else "package",
                "internal_path": run.get("output_dir"),
                "summary": core.get("user_facing_result", {}).get("summary") or f"Claire run {run.get('run_id')}",
                "timestamp": run.get("created_at"),
                "route": route,
                "metadata": {"run": run, "core_status": core.get("status")},
            }, terms))
        return out

    def _search_technology(self, query: str) -> List[Dict[str, Any]]:
        matches = self.tech_search.keyword(query, limit=12) or self.tech_search.fuzzy(query)
        out = []
        stack = self.stack_recommender.recommend({"keywords": list(self._terms(query)), "domain": "technology"})
        for item in matches:
            out.append(self._result({
                "title": item.get("name"),
                "source_type": "technology",
                "summary": item.get("description"),
                "route": "solution_design",
                "metadata": {"technology": item, "selected_stack": stack.get("selected_stack", {})},
            }, self._terms(query)))
        if "stack" in self._terms(query) or "compatible" in self._terms(query):
            out.append(self._result({
                "title": "Recommended application stack",
                "source_type": "technology",
                "summary": "Claire generated a route-gated app/software/platform stack recommendation.",
                "route": "solution_design",
                "metadata": stack,
            }, self._terms(query)))
        return out

    def _search_signals(self, query: str) -> List[Dict[str, Any]]:
        terms = self._terms(query)
        out = []
        root = Path("data")
        for path in root.glob("**/*.json*"):
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if self._matches(terms, text):
                out.append(self._result({
                    "title": path.name,
                    "source_type": "system",
                    "internal_path": str(path),
                    "summary": f"Internal Claire data file matching {query}.",
                    "route": "trend_thesis",
                    "metadata": {"path": str(path)},
                }, terms))
        return out[:8]

    def _read_core(self, run_id: str) -> Dict[str, Any]:
        if not run_id:
            return {}
        res = self.browser.read_file(run_id, "core_run_output.json", max_chars=1_500_000)
        if res.get("status") != "success":
            return {}
        try:
            return json.loads(res.get("content") or "{}")
        except Exception:
            return {}

    def _result(self, source: Dict[str, Any], terms: set[str]) -> Dict[str, Any]:
        gov = self.governance.score(source)
        text = f"{source.get('title', '')} {source.get('summary', '')}"
        result = ResearchResult(
            title=source.get("title") or "Untitled result",
            source_type=source.get("source_type") or "unknown",
            url=source.get("url"),
            internal_path=source.get("internal_path"),
            summary=source.get("summary") or "",
            relevance=self._relevance(terms, text),
            source_credibility=gov.get("source_credibility", 0.0),
            freshness=gov.get("freshness", 0.0),
            extracted_entities=self._entities(text),
            extracted_signals=self._signals(text),
            related_lifecycle_route=source.get("route") or "trend_thesis",
            metadata={**(source.get("metadata") or {}), "source_governance": gov},
        )
        return result.to_dict()

    def _terms(self, value: Any) -> set[str]:
        if isinstance(value, str):
            raw = value.replace("_", " ").replace("-", " ").split()
        elif isinstance(value, Iterable):
            raw = []
            for item in value:
                raw.extend(self._terms(item))
        else:
            raw = []
        return {str(term).strip().lower() for term in raw if len(str(term).strip()) > 2}

    def _matches(self, terms: set[str], text: str) -> bool:
        hay = text.lower()
        return any(term in hay for term in terms)

    def _relevance(self, terms: set[str], text: str) -> float:
        if not terms:
            return 0.0
        hay = text.lower()
        hits = sum(1 for term in terms if term in hay)
        return round(min(1.0, hits / max(1, len(terms))), 4)

    def _entities(self, text: str) -> List[str]:
        words = [w.strip(".,:;()[]{}") for w in text.split()]
        return list(dict.fromkeys([w for w in words if len(w) > 2 and w[:1].isupper()]))[:12]

    def _signals(self, text: str) -> List[str]:
        chunks = [part.strip() for part in text.replace("\n", ". ").split(".")]
        return [chunk for chunk in chunks if len(chunk) > 24][:8]
