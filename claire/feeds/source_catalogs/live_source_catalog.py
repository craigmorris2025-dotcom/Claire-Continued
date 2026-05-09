"""
Live source catalog activation.

v5.65:
- Loads governed public URL packs from data/live_sources.
- Resolves cataloged source definitions into scan-ready URLs.
- Performs no network access by default; live fetching stays behind the live scanner gate.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse


class LiveSourceCatalog:
    """Resolve governed starter source packs into public metadata scan URLs."""

    SUPPORTED_UNIVERSES = {"sp500_public", "djia_public", "nasdaq_composite"}

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[4]
        self.catalog_path = self.project_root / "data" / "live_sources" / "public_company_source_packs.json"

    def load(self) -> Dict[str, Any]:
        if not self.catalog_path.exists():
            return {
                "status": "missing",
                "catalog_path": str(self.catalog_path),
                "source_packs": [],
                "notes": ["Live source catalog file is missing."],
            }
        return json.loads(self.catalog_path.read_text(encoding="utf-8-sig"))

    def status(self) -> Dict[str, Any]:
        payload = self.load()
        packs = payload.get("source_packs", [])
        sources = self._flatten_sources(packs)
        active = [item for item in sources if item.get("active") is True]
        valid = [item for item in active if self._validate_url(item.get("url", "")).get("allowed")]
        universe_counts = {
            universe: len(self.resolve(market_universe=universe, limit=100).get("source_urls", []))
            for universe in sorted(self.SUPPORTED_UNIVERSES)
        }
        return {
            "status": "success" if payload.get("status") != "missing" else "missing",
            "catalog_version": payload.get("catalog_version"),
            "catalog_name": payload.get("catalog_name", "public_company_live_source_catalog"),
            "catalog_path": str(self.catalog_path),
            "source_pack_count": len(packs),
            "source_count": len(sources),
            "active_source_count": len(active),
            "valid_source_count": len(valid),
            "resolver_enabled": True,
            "safe_metadata_only": payload.get("safe_metadata_only", True),
            "default_limit": int(payload.get("default_limit", 5) or 5),
            "universe_source_counts": universe_counts,
            "notes": payload.get("notes", []),
        }

    def packs(self) -> Dict[str, Any]:
        payload = self.load()
        return {
            "status": "success" if payload.get("source_packs") is not None else payload.get("status", "missing"),
            "catalog_version": payload.get("catalog_version"),
            "source_packs": payload.get("source_packs", []),
        }

    def resolve(
        self,
        market_universe: str = "sp500_public",
        source_ids: List[str] | None = None,
        source_types: List[str] | None = None,
        limit: int | None = None,
    ) -> Dict[str, Any]:
        payload = self.load()
        requested_limit = limit or int(payload.get("default_limit", 5) or 5)
        source_ids = {item for item in (source_ids or []) if item}
        source_types = {item for item in (source_types or []) if item}

        if market_universe not in self.SUPPORTED_UNIVERSES:
            return {
                "status": "unsupported_universe",
                "market_universe": market_universe,
                "source_urls": [],
                "sources": [],
                "warnings": ["Live source catalog currently supports public-company universes only."],
            }

        selected: List[Dict[str, Any]] = []
        warnings: List[str] = []
        for pack in payload.get("source_packs", []):
            if pack.get("status") != "active":
                continue
            if market_universe not in pack.get("supported_universes", []):
                continue
            for source in pack.get("sources", []):
                enriched = dict(source)
                enriched["pack_id"] = pack.get("pack_id")
                enriched["pack_name"] = pack.get("name")
                enriched["source_category"] = pack.get("source_category", "public_company_market_data")
                if source_ids and enriched.get("source_id") not in source_ids:
                    continue
                if source_types and enriched.get("source_type") not in source_types:
                    continue
                if not enriched.get("active", False):
                    continue
                validation = self._validate_url(enriched.get("url", ""))
                enriched["validation"] = validation
                if not validation.get("allowed"):
                    warnings.append(f"{enriched.get('source_entry_id')}: {validation.get('reason')}")
                    continue
                selected.append(enriched)

        selected.sort(key=lambda item: (int(item.get("priority", 999) or 999), item.get("name", "")))
        selected = selected[: max(0, int(requested_limit))]
        return {
            "status": "success",
            "resolver": "live_source_catalog_v1",
            "catalog_version": payload.get("catalog_version"),
            "market_universe": market_universe,
            "source_count": len(selected),
            "source_urls": [item["url"] for item in selected],
            "sources": selected,
            "warnings": warnings,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "safe_metadata_only": payload.get("safe_metadata_only", True),
        }

    def _flatten_sources(self, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        flattened: List[Dict[str, Any]] = []
        for pack in packs:
            for source in pack.get("sources", []):
                item = dict(source)
                item["pack_id"] = pack.get("pack_id")
                item["source_category"] = pack.get("source_category")
                flattened.append(item)
        return flattened

    def _validate_url(self, url: str) -> Dict[str, Any]:
        parsed = urlparse((url or "").strip())
        if parsed.scheme not in {"http", "https"}:
            return {"allowed": False, "reason": "Only http/https URLs are allowed."}
        if not parsed.hostname:
            return {"allowed": False, "reason": "URL hostname is missing."}
        host = parsed.hostname.lower()
        if host in {"localhost", "127.0.0.1", "0.0.0.0"}:
            return {"allowed": False, "reason": "Local/private hostnames are blocked."}
        return {"allowed": True, "reason": "catalog_url_valid"}
