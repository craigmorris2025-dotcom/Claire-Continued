"""Claire Runtime Truth Backbone (v17.59).

This package normalizes Claire run output into one canonical truth payload for the
operating environment dashboard. It does not execute lifecycle stages and it does
not fabricate completed work. Missing required truth is represented as pending,
blocked, skipped_by_route, failed, or not_applicable.
"""

from .runtime_truth_builder import build_runtime_truth, find_latest_core_output, write_runtime_truth

__all__ = ["build_runtime_truth", "find_latest_core_output", "write_runtime_truth"]
