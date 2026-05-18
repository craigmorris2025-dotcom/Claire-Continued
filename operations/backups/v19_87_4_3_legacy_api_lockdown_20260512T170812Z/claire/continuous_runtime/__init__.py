"""Compatibility namespace for continuous runtime cycle contracts."""

from .cycle import (
    ContinuousRuntimeCycle,
    ContinuousRuntimeCycleResult,
    ensure_continuous_runtime_cycle,
    run_continuous_runtime_cycle,
)

__all__ = [
    "ContinuousRuntimeCycle",
    "ContinuousRuntimeCycleResult",
    "ensure_continuous_runtime_cycle",
    "run_continuous_runtime_cycle",
]
