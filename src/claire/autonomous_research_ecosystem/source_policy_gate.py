from __future__ import annotations
from typing import Dict, Any, List

class SourcePolicyGate:
    def evaluate(self, source: str, allowlist: List[str]) -> Dict[str, Any]:
        return {"status": "allowed" if source in allowlist else "blocked", "source": source}
