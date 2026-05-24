from __future__ import annotations

from dataclasses import replace

from runtime_core.signals.signal_timeseries_store import SignalSeries, SignalTimeSeriesStore
from runtime_core.technology.reemergence_pattern_engine import ReemergencePattern, _compute_delta


class ReemergenceThresholdLearner:
    """Learns required signal thresholds from labeled historical cases."""

    def __init__(self, store: SignalTimeSeriesStore):
        self._store = store

    def fit_pattern(self, pattern: ReemergencePattern, positive_entities: list[str]) -> ReemergencePattern:
        learned_changes = []
        for req in pattern.required_changes:
            deltas: list[float] = []
            for entity_id in positive_entities:
                series = self._store.get_series(req.signal_id, entity_id)
                if not series or len(series.points) < 2:
                    continue
                delta = self._compute_delta(series, req.window_years or 5)
                if delta is not None:
                    deltas.append(delta)
            if deltas:
                deltas.sort()
                idx = int(0.6 * (len(deltas) - 1))
                learned_changes.append(replace(req, learned_threshold=deltas[idx]))
            else:
                learned_changes.append(req)
        return replace(pattern, required_changes=learned_changes)

    def _compute_delta(self, series: SignalSeries, window_years: int) -> float | None:
        return _compute_delta(series, window_years)


__all__ = ["ReemergenceThresholdLearner"]
