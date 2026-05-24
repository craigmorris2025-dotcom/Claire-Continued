from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def add_minutes(value: str | None, minutes: int) -> str:
    base = parse_utc(value) or datetime.now(timezone.utc)
    return (base + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def is_due(value: str | None, now_value: str | None = None) -> bool:
    if not value:
        return True
    due = parse_utc(value)
    now = parse_utc(now_value) or datetime.now(timezone.utc)
    if due is None:
        return True
    return due <= now
