from __future__ import annotations
from typing import Dict, Any

class BenchmarkExhibitBuilder:
    def build_exhibit(self, benchmark_id: str, result: str) -> Dict[str, Any]:
        return {"record_type": "benchmark_exhibit", "benchmark_id": benchmark_id, "result": result}
