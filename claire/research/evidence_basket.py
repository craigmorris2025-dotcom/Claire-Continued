"""Local evidence basket for research-to-pipeline handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json


class EvidenceBasket:
    def __init__(self, path: str = "data/research/evidence_basket.json") -> None:
        self.path = Path(path)

    def list(self) -> Dict[str, Any]:
        payload = self._read()
        return {"status": "success", "items": payload.get("items", []), "item_count": len(payload.get("items", []))}

    def add(self, result: Dict[str, Any], notes: str = "") -> Dict[str, Any]:
        payload = self._read()
        item = {
            "evidence_id": f"ev_{len(payload.get('items', [])) + 1:04d}",
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "source_type": result.get("source_type"),
            "title": result.get("title"),
            "summary": result.get("summary"),
            "credibility": result.get("source_credibility"),
            "freshness": result.get("freshness"),
            "related_lifecycle_route": result.get("related_lifecycle_route"),
            "result": result,
        }
        payload.setdefault("items", []).insert(0, item)
        self._write(payload)
        return {"status": "success", "item": item, "item_count": len(payload["items"])}

    def clear(self) -> Dict[str, Any]:
        self._write({"items": []})
        return {"status": "success", "item_count": 0}

    def as_pipeline_input(self) -> Dict[str, Any]:
        items = self._read().get("items", [])
        signals: List[str] = []
        for item in items:
            result = item.get("result", {})
            signals.extend(result.get("extracted_signals", []) or [])
        return {
            "status": "success",
            "raw_input": "\n".join([f"{item.get('title')}: {item.get('summary')}" for item in items]),
            "governed_signal_candidates": signals,
            "evidence_count": len(items),
            "items": items,
        }

    def _read(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"items": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"items": []}

    def _write(self, payload: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
