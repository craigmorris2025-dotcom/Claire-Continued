from __future__ import annotations
from typing import Dict, List

class SampleInputLibrary:
    def default_inputs(self) -> List[Dict[str, str]]:
        return [
            {"name": "opportunity_intelligence", "input": "Evaluate a weak-signal opportunity using governed evidence."},
            {"name": "portfolio_review", "input": "Review a portfolio thesis using benchmark and operator evidence."},
            {"name": "pilot_readiness", "input": "Determine whether pilot readiness gates are satisfied."},
        ]
