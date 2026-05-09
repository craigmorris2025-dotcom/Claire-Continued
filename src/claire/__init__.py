"""
Temporary compatibility shim for Phase 4B.

Allows imports to resolve from top-level `claire/` while legacy `src`-based
bootstrap assumptions still exist during transition.
"""
from pathlib import Path

__path__ = [str((Path(__file__).resolve().parents[2] / "claire"))]
