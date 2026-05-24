from __future__ import annotations

from typing import Any, Dict, List


class InternetDashboardPayloadBuilder:
    def build(self, internet_output: Dict[str, Any]) -> Dict[str, Any]:
        activation = internet_output.get("internet_activation_result", {})
        summary = internet_output.get("internet_summary", {})
        return {
            "panel": "internet_research",
            "title": "Internet Research",
            "status": summary.get("internet_status", "unknown"),
            "query": summary.get("query"),
            "searched": summary.get("searched", False),
            "fetched_count": summary.get("fetched_count", 0),
            "evidence_count": summary.get("evidence_count", 0),
            "warnings": summary.get("warnings", []),
            "errors": summary.get("errors", []),
            "sources": self._sources(activation.get("search_results", []), activation.get("fetch_results", [])),
            "evidence": activation.get("evidence", []),
            "evidence_links": internet_output.get("evidence_links", []),
            "governance": activation.get("governance", {}),
        }

    def _sources(self, searches: List[Dict[str, Any]], fetches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_url: Dict[str, Dict[str, Any]] = {}
        for item in searches:
            url = item.get("url")
            if url:
                by_url[url] = {"url": url, "title": item.get("title", ""), "snippet": item.get("snippet", ""), "search_source": item.get("source", ""), "rank": item.get("rank", 0), "fetch_status": None}
        for fetch in fetches:
            url = fetch.get("url")
            if not url:
                continue
            by_url.setdefault(url, {"url": url})
            by_url[url]["fetch_status"] = fetch.get("status")
            by_url[url]["http_status"] = fetch.get("http_status")
            by_url[url]["content_type"] = fetch.get("content_type")
            by_url[url]["error"] = fetch.get("error")
        return list(by_url.values())
