
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


STRATEGIC_MEMORY_PATH = Path("data/memory/strategic_memory_registry.json")

VALID_MEMORY_TYPES = {
    "signal",
    "trend",
    "thesis",
    "portfolio_action",
    "breakthrough_classification",
    "evidence",
    "operator_decision",
    "pilot_learning",
    "acquisition_context",
}


def _load_memories() -> List[Dict[str, Any]]:
    if not STRATEGIC_MEMORY_PATH.exists():
        return []
    try:
        data = json.loads(STRATEGIC_MEMORY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def add_strategic_memory(
    memory_type: str,
    title: str,
    payload: Dict[str, Any],
    confidence: float = 0.5,
    tags: List[str] | None = None,
) -> Dict[str, Any]:
    if memory_type not in VALID_MEMORY_TYPES:
        raise ValueError(f"Invalid strategic memory type: {memory_type}")

    confidence = max(0.0, min(1.0, float(confidence)))

    record = {
        "version": "16.66",
        "memory_id": f"mem_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "memory_type": memory_type,
        "title": title,
        "payload": payload,
        "confidence": confidence,
        "tags": tags or [],
        "status": "active",
    }

    STRATEGIC_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    memories = _load_memories()
    memories.append(record)
    STRATEGIC_MEMORY_PATH.write_text(json.dumps(memories, indent=2), encoding="utf-8")
    return record


def list_strategic_memories(memory_type: str | None = None) -> List[Dict[str, Any]]:
    memories = _load_memories()
    if memory_type is None:
        return memories
    return [m for m in memories if m.get("memory_type") == memory_type]
