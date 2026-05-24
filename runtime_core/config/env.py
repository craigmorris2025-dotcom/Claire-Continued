from __future__ import annotations

import os


LEGACY_PREFIX = "CL" + "AIRE_"
CANONICAL_PREFIX = "PLATFORM_"
TRUE_VALUES = {"1", "true", "yes", "on"}


def legacy_env_name(name: str) -> str:
    if name.startswith(CANONICAL_PREFIX):
        return LEGACY_PREFIX + name.removeprefix(CANONICAL_PREFIX)
    return LEGACY_PREFIX + name


def getenv(name: str, default: str = "", *, legacy: bool = True) -> str:
    value = os.environ.get(name)
    if value is not None:
        return value
    if legacy and name.startswith(CANONICAL_PREFIX):
        value = os.environ.get(legacy_env_name(name))
        if value is not None:
            return value
    return default


def env_true(name: str, *, legacy: bool = True) -> bool:
    return getenv(name, legacy=legacy).strip().lower() in TRUE_VALUES


def env_int(name: str, default: int, *, legacy: bool = True) -> int:
    value = getenv(name, legacy=legacy)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default
