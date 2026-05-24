"""Deterministic deduplication for governed signals."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def signal_fingerprint(signal: Dict[str, Any]) -> str:
    title = str(signal.get("title") or signal.get("raw_input") or "").lower().strip()
    summary = str(signal.get("summary") or "").lower().strip()
    source_type = str(signal.get("source_type") or "unknown").lower().strip()
    compact = " ".join((title + " " + summary[:240]).split())
    return f"{source_type}|{compact}"


def dedupe_signals(signals: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    result: List[Dict[str, Any]] = []
    for signal in signals:
        fingerprint = signal_fingerprint(signal)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        result.append(signal)
    return result
