
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.orchestration.intelligence_task_registry import list_intelligence_tasks
from claire.memory.strategic_memory_registry import list_strategic_memories

PRIORITY_STATE_PATH = Path("data/orchestration/strategic_priority_state.json")

def _score_task(task: Dict[str, Any]) -> float:
    base = float(task.get("priority", 5)) / 10.0
    boosts = {
        "live_ingestion": 0.12,
        "evidence_review": 0.15,
        "signal_analysis": 0.18,
        "thesis_update": 0.20,
        "portfolio_review": 0.17,
        "buyer_readiness_review": 0.10,
        "source_probe": 0.08,
    }
    state_penalty = 0.0 if task.get("state") == "queued" else -0.10
    return max(0.0, min(1.0, base + boosts.get(task.get("task_type", ""), 0.0) + state_penalty))

def _score_memory(memory: Dict[str, Any]) -> float:
    confidence = float(memory.get("confidence", 0.5))
    boosts = {
        "signal": 0.08,
        "trend": 0.12,
        "thesis": 0.18,
        "portfolio_action": 0.16,
        "breakthrough_classification": 0.15,
        "evidence": 0.12,
        "operator_decision": 0.10,
        "pilot_learning": 0.11,
        "acquisition_context": 0.09,
    }
    return max(0.0, min(1.0, confidence + boosts.get(memory.get("memory_type", ""), 0.0)))

def build_strategic_priority_state(limit: int = 25) -> Dict[str, Any]:
    tasks = list_intelligence_tasks()
    memories = list_strategic_memories()

    ranked_tasks = sorted(
        [{
            "kind": "task",
            "id": task.get("task_id"),
            "title": task.get("title"),
            "task_type": task.get("task_type"),
            "state": task.get("state"),
            "score": round(_score_task(task), 4),
        } for task in tasks],
        key=lambda item: item["score"],
        reverse=True,
    )[:limit]

    ranked_memories = sorted(
        [{
            "kind": "memory",
            "id": memory.get("memory_id"),
            "title": memory.get("title"),
            "memory_type": memory.get("memory_type"),
            "status": memory.get("status"),
            "score": round(_score_memory(memory), 4),
        } for memory in memories],
        key=lambda item: item["score"],
        reverse=True,
    )[:limit]

    combined = sorted(ranked_tasks + ranked_memories, key=lambda item: item["score"], reverse=True)

    state = {
        "version": "16.84",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "ranked_tasks": ranked_tasks,
        "ranked_memories": ranked_memories,
        "top_priority": combined[:1],
        "note": "Strategic priority scoring is conservative and explainable; it does not replace operator approval.",
    }

    PRIORITY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRIORITY_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
