"""
Core — DataEngine: Central data management and retrieval.
Handles acquirer profiles, cached pipeline state, query filtering.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("claire.core.data_engine")


class DataEngine:
    """Central data access layer for all pipeline operations."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._cache: Dict[str, Any] = {}
        self._acquirers: Optional[List[Dict[str, Any]]] = None

    def load_acquirers(self) -> List[Dict[str, Any]]:
        if self._acquirers is not None:
            return self._acquirers
        path = os.path.join(self.data_dir, "acquirers.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._acquirers = json.load(f)
            logger.info(f"Loaded {len(self._acquirers)} acquirer profiles")
        except FileNotFoundError:
            logger.warning(f"Acquirer data not found at {path}")
            self._acquirers = []
        return self._acquirers

    def query(self, sector: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query acquirer profiles with optional sector and custom filters."""
        data = list(self.load_acquirers())
        if sector:
            data = [d for d in data if sector.lower() in d.get("sector", "").lower()]
        if filters:
            for key, value in filters.items():
                if isinstance(value, (int, float)):
                    data = [d for d in data if d.get(key, 0) >= value]
                elif isinstance(value, str):
                    data = [d for d in data if value.lower() in str(d.get(key, "")).lower()]
        return data

    def store(self, collection: str, data: Any):
        self._cache[collection] = data

    def get_status(self) -> Dict[str, Any]:
        acqs = self.load_acquirers()
        return {"component": "DataEngine", "status": "active",
                "acquirer_profiles": len(acqs), "cached_collections": len(self._cache)}
