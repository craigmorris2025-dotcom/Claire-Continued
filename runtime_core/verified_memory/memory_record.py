from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class MemoryRecord:
    memory_id: str
    run_id: str
    route_selected: str
    terminal_state: str
    validation_score: int
    source_output_path: str
    evidence_count: int
    created_at: str
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_memory_id(run_id: str, route_selected: str, terminal_state: str) -> str:
    cleaned = f"{run_id}-{route_selected}-{terminal_state}".lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in cleaned).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return f"mem-{cleaned[:96] or 'unknown'}"
