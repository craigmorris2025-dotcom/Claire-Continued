from __future__ import annotations
from typing import Dict, Any, List

class ResearchTaskContract:
    def build_contract(self, task_id: str, question: str, allowed_sources: List[str]) -> Dict[str, Any]:
        return {"record_type": "research_task_contract", "task_id": task_id, "question": question, "allowed_sources": allowed_sources, "requires_review": True}
