from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from runtime_core.memory.store import Store
from runtime_core.ingestion.source_boundary import PROJECT_ROOT, is_allowed_input_path


class LifecycleMemorySignalBuilder:
    """
    Convert verified prior Claire runs into governed internal source packets.

    The output is intentionally shaped like the existing request-source packets
    so Stage 1 can ingest it through the normal source path. It is not live
    market truth, and it never promotes a candidate without fresh validation.
    """

    schema_version = "claire.lifecycle_memory_signal.v1"

    def __init__(self, store: Optional[Store] = None, limit: int = 3) -> None:
        self.store = store or Store()
        self.limit = max(1, int(limit or 3))

    def build_sources(self, current_raw_input: str = "", provided_sources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if provided_sources and "prior_claire_output" in provided_sources:
            return {}

        records = self._eligible_records()
        if not records:
            return {}

        signals = []
        keywords: List[str] = []
        domains: List[str] = []
        routes: List[str] = []
        source_run_ids: List[str] = []

        for record in records[: self.limit]:
            result = record.get("result") if isinstance(record.get("result"), dict) else {}
            run_id = str(record.get("run_id") or result.get("run_id") or "").strip()
            route = str(result.get("route_selected") or record.get("decision_classification") or "").strip()
            domain = str(result.get("domain") or record.get("domain") or "general").strip()
            summary = self._summary_text(result, record)
            signal = {
                "run_id": run_id,
                "type": "validated_prior_claire_output",
                "description": summary,
                "route_selected": route,
                "domain": domain,
                "terminal_state": result.get("terminal_state"),
                "memory_feedback_eligible": True,
            }
            if run_id:
                source_run_ids.append(run_id)
            if route:
                routes.append(route)
            if domain:
                domains.append(domain)
            for keyword in result.get("keywords") or []:
                text = str(keyword).strip().lower()
                if text and text not in keywords:
                    keywords.append(text)
            signals.append(signal)

        packet = {
            "schema_version": self.schema_version,
            "source_type": "internal_verified_memory",
            "type": "prior_claire_output",
            "sector": self._first(domains, "general"),
            "signals": signals,
            "data": {
                "current_raw_input": current_raw_input,
                "source_run_ids": source_run_ids,
                "domains": sorted(set(domains)),
                "routes": sorted(set(routes)),
                "keywords": keywords[:24],
                "memory_record_count": len(signals),
                "governance": {
                    "recursive_feedback_allowed": True,
                    "live_truth": False,
                    "promotion_requires_fresh_validation": True,
                    "stage_1_use": "context_seed_and_pattern_reference",
                },
            },
            "metrics": {
                "memory_signal_count": len(signals),
                "recency_coverage": min(1.0, len(signals) / float(self.limit)),
            },
            "provenance": {
                "origin": "verified_memory_store",
                "store_root": str(self.store.memory_root),
                "source_run_ids": source_run_ids,
            },
        }

        return {"prior_claire_output": packet}

    def _eligible_records(self) -> List[Dict[str, Any]]:
        curated = PROJECT_ROOT / "data" / "continuous_runtime" / "lifecycle_memory.json"
        if not is_allowed_input_path(curated, PROJECT_ROOT) or not curated.exists():
            return []
        try:
            payload = json.loads(curated.read_text(encoding="utf-8"))
        except Exception:
            return []
        records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            return []
        return [
            item for item in records
            if isinstance(item, dict) and self._is_feedback_eligible(item)
        ][: self.limit]

    def _legacy_eligible_records_disabled(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for item in self._history_newest_first():
            path = item.get("memory_path")
            run_id = item.get("run_id")
            record = self._load_record(run_id=run_id, memory_path=path)
            if record and self._is_feedback_eligible(record):
                records.append(record)
            if len(records) >= self.limit:
                break
        return records

    def _history_newest_first(self) -> Iterable[Dict[str, Any]]:
        try:
            history = self.store.list_runs()
        except Exception:
            return []
        if not isinstance(history, list):
            return []
        return sorted(
            [item for item in history if isinstance(item, dict)],
            key=lambda item: str(item.get("created_at") or ""),
            reverse=True,
        )

    def _load_record(self, run_id: Any, memory_path: Any) -> Optional[Dict[str, Any]]:
        try:
            if run_id:
                loaded = self.store.load_run(str(run_id))
                if isinstance(loaded, dict):
                    return loaded
        except Exception:
            pass

        try:
            path = Path(str(memory_path))
            if path.exists():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                return loaded if isinstance(loaded, dict) else None
        except Exception:
            return None
        return None

    def _is_feedback_eligible(self, record: Dict[str, Any]) -> bool:
        result = record.get("result") if isinstance(record.get("result"), dict) else {}
        quality = result.get("run_quality") if isinstance(result.get("run_quality"), dict) else {}
        source_authority = result.get("source_authority") if isinstance(result.get("source_authority"), dict) else {}
        return (
            record.get("status") == "success"
            and quality.get("memory_feedback_eligible") is True
            and (quality.get("live_truth_eligible") is True or source_authority.get("live_truth_eligible") is True)
        )

    def _summary_text(self, result: Dict[str, Any], record: Dict[str, Any]) -> str:
        user = result.get("user_facing_result") if isinstance(result.get("user_facing_result"), dict) else {}
        headline = str(user.get("headline") or "").strip()
        summary = str(user.get("summary") or "").strip()
        trend = result.get("trend_discovery") if isinstance(result.get("trend_discovery"), dict) else {}
        thesis = result.get("thesis_formation") if isinstance(result.get("thesis_formation"), dict) else {}
        pieces = [
            headline,
            summary,
            str(thesis.get("thesis_statement") or "").strip(),
            str(trend.get("description") or "").strip(),
            str(record.get("raw_input") or "").strip(),
        ]
        text = " ".join(piece for piece in pieces if piece)
        return text[:1200] if text else "Verified prior Claire output available for recursive lifecycle context."

    def _first(self, values: List[str], default: str) -> str:
        for value in values:
            if value:
                return value
        return default


def build_lifecycle_memory_sources(
    store: Optional[Store] = None,
    current_raw_input: str = "",
    provided_sources: Optional[Dict[str, Any]] = None,
    limit: int = 3,
) -> Dict[str, Any]:
    return LifecycleMemorySignalBuilder(store=store, limit=limit).build_sources(
        current_raw_input=current_raw_input,
        provided_sources=provided_sources,
    )
