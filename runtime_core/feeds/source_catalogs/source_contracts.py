"""
Public Company Source Contracts.

v5.44:
- Stable definitions for public-company source catalogs.
- No live scraping, network calls, or ingestion.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class SourceDefinition:
    source_id: str
    name: str
    source_category: str
    access_type: str
    status: str
    intended_use: str
    governance_notes: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IndexUniverseDefinition:
    universe_id: str
    name: str
    coverage_target: str
    market_category: str
    source_category: str
    source_ids: List[str]
    connected_scan_status: str = "not_enabled"
    deterministic_fallback: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceCatalogResult:
    status: str
    catalog_name: str
    generated_at: str
    source_count: int
    universe_count: int
    sources: List[Dict[str, Any]]
    universes: List[Dict[str, Any]]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
