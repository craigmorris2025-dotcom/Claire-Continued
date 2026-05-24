"""
Claire Syntalion v17.89.1
Runtime Truth Search Adapter Repair

Fix:
- Rewrites the v17.89 search adapter with clean Python syntax.
- Preserves read-only governed runtime truth search behavior.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.api.runtime_truth_read_api import get_runtime_truth_records


class RuntimeTruthSearchAdapter:
    def __init__(self) -> None:
        self.read_only = True
        self.automatic_updates_enabled = False
        self.autonomous_agent_execution_enabled = False

    def normalize_query(self, query: str) -> str:
        return (query or "").strip().lower()

    def search(self, query: str) -> Dict[str, Any]:
        normalized = self.normalize_query(query)
        records = get_runtime_truth_records()

        matches: List[Dict[str, Any]] = []

        for record in records:
            haystack = str(record).lower()

            if normalized and normalized in haystack:
                matches.append(
                    {
                        "runtime_truth_id": record.get("runtime_truth_id"),
                        "evidence_id": record.get("evidence_id"),
                        "source_provenance": record.get("source_provenance"),
                        "truth_payload": record.get("truth_payload"),
                        "match_type": "governed_runtime_truth_search_match",
                        "read_only": True,
                    }
                )

        return {
            "version": "v17.89.1",
            "query": query,
            "normalized_query": normalized,
            "match_count": len(matches),
            "matches": matches,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "source": "runtime_truth_search_adapter",
        }
