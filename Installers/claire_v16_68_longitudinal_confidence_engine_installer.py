from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/memory/longitudinal_confidence_engine.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from claire.memory.strategic_memory_registry import list_strategic_memories
from claire.memory.cross_run_evidence_linker import list_evidence_links


CONFIDENCE_STATE_PATH = Path("data/memory/longitudinal_confidence_state.json")


def calculate_longitudinal_confidence() -> Dict[str, Any]:
    memories = list_strategic_memories()
    links = list_evidence_links()

    memory_confidences = [
        float(m.get("confidence", 0.5))
        for m in memories
        if isinstance(m.get("confidence", 0.5), (int, float))
    ]

    base_confidence = mean(memory_confidences) if memory_confidences else 0.0
    linkage_boost = min(0.15, len(links) * 0.01)
    proof_depth_boost = min(0.10, len(memories) * 0.005)

    total_confidence = max(0.0, min(1.0, base_confidence + linkage_boost + proof_depth_boost))

    state = {
        "version": "16.68",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "memory_count": len(memories),
        "evidence_link_count": len(links),
        "base_memory_confidence": round(base_confidence, 4),
        "linkage_boost": round(linkage_boost, 4),
        "proof_depth_boost": round(proof_depth_boost, 4),
        "longitudinal_confidence": round(total_confidence, 4),
        "note": "Confidence is longitudinal and conservative; it should increase only through memory depth, evidence linkage, and operator feedback.",
    }

    CONFIDENCE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIDENCE_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
""")

print("v16.68 longitudinal confidence engine installed.")
