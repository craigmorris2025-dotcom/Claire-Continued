from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SignalPoint:
    date: date
    value: float
    source: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class SignalSeries:
    signal_id: str
    entity_id: str
    points: List[SignalPoint]


class SignalTimeSeriesStore:
    """In-memory signal time-series store with optional JSON persistence."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._series: Dict[str, SignalSeries] = {}
        self._path = Path(path) if path else None
        if self._path and self._path.exists():
            self.load()

    def upsert_series(self, series: SignalSeries) -> None:
        key = self._key(series.signal_id, series.entity_id)
        self._series[key] = series

    def get_series(self, signal_id: str, entity_id: str) -> Optional[SignalSeries]:
        return self._series.get(self._key(signal_id, entity_id))

    def list_series_for_entity(self, entity_id: str) -> List[SignalSeries]:
        return [s for s in self._series.values() if s.entity_id == entity_id]

    def list_entities(self) -> list[str]:
        return sorted({series.entity_id for series in self._series.values()})

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path) if path else self._path
        if not target:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "claire.signal_timeseries_store.v1",
            "series": [self._series_to_dict(series) for series in self._series.values()],
        }
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def load(self, path: str | Path | None = None) -> None:
        target = Path(path) if path else self._path
        if not target or not target.exists():
            return
        payload = json.loads(target.read_text(encoding="utf-8"))
        for item in payload.get("series", []):
            if not isinstance(item, dict):
                continue
            points = [
                SignalPoint(
                    date=date.fromisoformat(point["date"]),
                    value=float(point["value"]),
                    source=point.get("source"),
                    notes=point.get("notes"),
                )
                for point in item.get("points", [])
                if isinstance(point, dict) and point.get("date") is not None and point.get("value") is not None
            ]
            self.upsert_series(SignalSeries(signal_id=str(item.get("signal_id")), entity_id=str(item.get("entity_id")), points=points))

    @staticmethod
    def _key(signal_id: str, entity_id: str) -> str:
        return f"{signal_id}:{entity_id}"

    @staticmethod
    def _series_to_dict(series: SignalSeries) -> dict:
        payload = asdict(series)
        payload["points"] = [{**point, "date": point["date"].isoformat()} for point in payload["points"]]
        return payload


def default_signal_timeseries_store() -> SignalTimeSeriesStore:
    """Seed historical cases so threshold learning has immediate examples."""

    store = SignalTimeSeriesStore()
    seeds = [
        (
            "battery_energy_density",
            "ev_market",
            [(1995, 90), (2005, 130), (2015, 240), (2025, 310)],
            "seed_historical_case",
        ),
        (
            "unit_cost",
            "ev_market",
            [(1995, 100), (2005, 82), (2015, 45), (2025, 24)],
            "seed_historical_case",
        ),
        (
            "charging_network_density",
            "ev_market",
            [(2005, 2), (2015, 23), (2025, 78)],
            "seed_historical_case",
        ),
        (
            "compute_per_dollar",
            "tablet_market",
            [(1995, 1), (2005, 14), (2010, 42), (2025, 600)],
            "seed_historical_case",
        ),
        (
            "touch_interface_readiness",
            "tablet_market",
            [(1995, 0.18), (2005, 0.45), (2010, 0.82), (2025, 0.96)],
            "seed_historical_case",
        ),
        (
            "broadband_penetration",
            "telehealth_market",
            [(2000, 7), (2010, 64), (2020, 88), (2025, 93)],
            "seed_historical_case",
        ),
        (
            "regulatory_acceptance",
            "telehealth_market",
            [(2000, 0.12), (2010, 0.24), (2020, 0.72), (2025, 0.81)],
            "seed_historical_case",
        ),
        (
            "sensor_cost_accuracy",
            "wearable_health_market",
            [(2005, 0.20), (2015, 0.62), (2025, 0.88)],
            "seed_historical_case",
        ),
    ]
    for signal_id, entity_id, points, source in seeds:
        store.upsert_series(
            SignalSeries(
                signal_id=signal_id,
                entity_id=entity_id,
                points=[SignalPoint(date=date(year, 1, 1), value=value, source=source) for year, value in points],
            )
        )
    return store


__all__ = [
    "SignalPoint",
    "SignalSeries",
    "SignalTimeSeriesStore",
    "default_signal_timeseries_store",
]
