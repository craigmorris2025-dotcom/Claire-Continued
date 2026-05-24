"""
Claire v6.1.0
Live Ingestion Adapter

Purpose:
- Normalize incoming live/simulated source packets.
- Attach provenance.
- Prevent live ingestion failures from breaking the lifecycle runtime.
- Prepare Claire for real source connectors in v6.2+.

This file does NOT perform web search.
This file does NOT call external APIs.
This file only governs source packet intake.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


ALLOWED_SOURCE_TYPES = {
    "market",
    "patent",
    "financial",
    "news",
    "regulatory",
    "research",
    "technology",
    "company",
    "portfolio",
    "custom",
}


@dataclass
class SourceRecord:
    name: str
    source_type: str
    accepted: bool
    reason: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LiveIngestionResult:
    status: str
    source_mode: str
    live_ingestion: bool
    simulated: bool
    fallback_used: bool
    sources_received: List[str]
    sources_accepted: List[str]
    sources_rejected: List[str]
    records: List[SourceRecord]
    ingested_at: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["records"] = [asdict(record) for record in self.records]
        return data


class LiveIngestionAdapter:
    """
    Normalizes source packets for Claire's lifecycle runtime.

    Expected input shape can be flexible:

    {
        "market": {...},
        "patent": {...},
        "financial": {...}
    }

    or:

    {
        "sources": {
            "market": {...},
            "patent": {...}
        },
        "source_mode": "simulated_live_packet"
    }
    """

    def normalize(
        self,
        raw_payload: Optional[Dict[str, Any]],
        source_mode: Optional[str] = None,
    ) -> LiveIngestionResult:
        ingested_at = datetime.now(timezone.utc).isoformat()

        if not raw_payload:
            return LiveIngestionResult(
                status="not_configured",
                source_mode="not_configured",
                live_ingestion=False,
                simulated=False,
                fallback_used=True,
                sources_received=[],
                sources_accepted=[],
                sources_rejected=[],
                records=[],
                ingested_at=ingested_at,
                warnings=[
                    "No source packet was provided. Runtime may continue from raw input only."
                ],
            )

        extracted_sources = self._extract_sources(raw_payload)

        if not extracted_sources:
            return LiveIngestionResult(
                status="empty",
                source_mode=source_mode or "empty_packet",
                live_ingestion=False,
                simulated=self._is_simulated(source_mode),
                fallback_used=True,
                sources_received=[],
                sources_accepted=[],
                sources_rejected=[],
                records=[],
                ingested_at=ingested_at,
                warnings=[
                    "Source packet was present but contained no usable sources."
                ],
            )

        records: List[SourceRecord] = []
        accepted: List[str] = []
        rejected: List[str] = []
        received: List[str] = list(extracted_sources.keys())

        for name, payload in extracted_sources.items():
            source_type = self._infer_source_type(name, payload)

            if source_type not in ALLOWED_SOURCE_TYPES:
                records.append(
                    SourceRecord(
                        name=name,
                        source_type=source_type,
                        accepted=False,
                        reason="unsupported_source_type",
                        payload={},
                    )
                )
                rejected.append(name)
                continue

            if not isinstance(payload, dict):
                records.append(
                    SourceRecord(
                        name=name,
                        source_type=source_type,
                        accepted=False,
                        reason="payload_not_object",
                        payload={},
                    )
                )
                rejected.append(name)
                continue

            if len(payload) == 0:
                records.append(
                    SourceRecord(
                        name=name,
                        source_type=source_type,
                        accepted=False,
                        reason="empty_payload",
                        payload={},
                    )
                )
                rejected.append(name)
                continue

            records.append(
                SourceRecord(
                    name=name,
                    source_type=source_type,
                    accepted=True,
                    reason="accepted",
                    payload=payload,
                )
            )
            accepted.append(name)

        final_source_mode = source_mode or raw_payload.get("source_mode") or "simulated_live_packet"

        return LiveIngestionResult(
            status="success" if accepted else "no_accepted_sources",
            source_mode=final_source_mode,
            live_ingestion=self._is_live(final_source_mode),
            simulated=self._is_simulated(final_source_mode),
            fallback_used=False if accepted else True,
            sources_received=received,
            sources_accepted=accepted,
            sources_rejected=rejected,
            records=records,
            ingested_at=ingested_at,
            warnings=[] if accepted else ["No source packets were accepted."],
        )

    def build_source_provenance(
        self,
        result: LiveIngestionResult,
    ) -> Dict[str, Any]:
        return {
            "status": result.status,
            "source_mode": result.source_mode,
            "live_ingestion": result.live_ingestion,
            "simulated": result.simulated,
            "fallback_used": result.fallback_used,
            "sources_received": result.sources_received,
            "sources_accepted": result.sources_accepted,
            "sources_rejected": result.sources_rejected,
            "ingested_at": result.ingested_at,
            "warnings": result.warnings,
        }

    def _extract_sources(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        if "sources" in raw_payload and isinstance(raw_payload["sources"], dict):
            return raw_payload["sources"]

        ignored_keys = {
            "raw_input",
            "mode",
            "metadata",
            "source_mode",
            "user_id",
            "session_id",
            "priority",
            "tags",
        }

        return {
            key: value
            for key, value in raw_payload.items()
            if key not in ignored_keys
        }

    def _infer_source_type(self, name: str, payload: Any) -> str:
        if isinstance(payload, dict):
            explicit_type = payload.get("source_type") or payload.get("type")
            if isinstance(explicit_type, str):
                return explicit_type.lower().strip()

        normalized_name = name.lower().strip()

        if normalized_name in ALLOWED_SOURCE_TYPES:
            return normalized_name

        return "custom"

    def _is_live(self, source_mode: Optional[str]) -> bool:
        return source_mode in {
            "live",
            "live_packet",
            "live_ingestion",
            "external_live",
        }

    def _is_simulated(self, source_mode: Optional[str]) -> bool:
        return source_mode in {
            None,
            "",
            "simulated",
            "simulated_live_packet",
            "test_packet",
            "mock_live_packet",
        }


def normalize_live_sources(
    raw_payload: Optional[Dict[str, Any]],
    source_mode: Optional[str] = None,
) -> LiveIngestionResult:
    """
    Convenience function for routes/orchestrators.
    """
    adapter = LiveIngestionAdapter()
    return adapter.normalize(raw_payload=raw_payload, source_mode=source_mode)


def build_source_provenance(
    raw_payload: Optional[Dict[str, Any]],
    source_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function for directly adding provenance to /evaluate output.
    """
    adapter = LiveIngestionAdapter()
    result = adapter.normalize(raw_payload=raw_payload, source_mode=source_mode)
    return adapter.build_source_provenance(result)