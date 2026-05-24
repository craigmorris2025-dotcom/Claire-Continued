
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.orchestration.strategic_priority_engine import build_strategic_priority_state


ESCALATION_STATE_PATH = Path("data/autonomy/autonomous_escalation_state.json")


def _load_escalations() -> List[Dict[str, Any]]:
    if not ESCALATION_STATE_PATH.exists():
        return []
    try:
        data = json.loads(ESCALATION_STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("escalations", [])
        return data if isinstance(data, list) else []
    except Exception:
        return []


def evaluate_autonomous_escalations(threshold: float = 0.75) -> Dict[str, Any]:
    threshold = max(0.0, min(1.0, float(threshold)))
    priority_state = build_strategic_priority_state()
    candidates = []

    for item in priority_state.get("ranked_tasks", []) + priority_state.get("ranked_memories", []):
        if float(item.get("score", 0.0)) >= threshold:
            candidates.append({
                "escalation_id": f"esc_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{len(candidates)}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_kind": item.get("kind"),
                "source_id": item.get("id"),
                "title": item.get("title"),
                "score": item.get("score"),
                "recommended_route": _recommended_route(item),
                "status": "pending_operator_review",
                "governance_note": "Escalation is recommended, not automatically executed without downstream guard checks.",
            })

    previous = _load_escalations()
    all_escalations = previous + candidates

    state = {
        "version": "16.87",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "threshold": threshold,
        "new_escalation_count": len(candidates),
        "escalations": all_escalations,
    }

    ESCALATION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ESCALATION_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def _recommended_route(item: Dict[str, Any]) -> str:
    item_type = item.get("task_type") or item.get("memory_type") or ""
    if item_type in {"signal_analysis", "signal", "trend"}:
        return "thesis_update"
    if item_type in {"thesis", "thesis_update"}:
        return "evidence_review"
    if item_type in {"portfolio_review", "portfolio_action"}:
        return "portfolio_review"
    if item_type in {"buyer_readiness_review", "acquisition_context"}:
        return "buyer_readiness_review"
    return "operator_review"
