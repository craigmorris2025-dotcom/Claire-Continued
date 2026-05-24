from __future__ import annotations

from typing import Dict, List

from .models import TelemetryMetric


class ProductionTelemetry:
    def __init__(self) -> None:
        self.metrics: List[TelemetryMetric] = []

    def record(self, name: str, value: float, unit: str = "count", tags: Dict[str, object] | None = None) -> TelemetryMetric:
        metric = TelemetryMetric(name=name, value=value, unit=unit, tags=tags or {})
        self.metrics.append(metric)
        return metric

    def summarize(self) -> Dict[str, object]:
        totals: Dict[str, float] = {}
        for metric in self.metrics:
            totals[metric.name] = totals.get(metric.name, 0.0) + metric.value
        return {
            "metric_count": len(self.metrics),
            "totals": totals,
            "metrics": [metric.to_dict() for metric in self.metrics],
        }
