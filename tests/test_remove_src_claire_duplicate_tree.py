from __future__ import annotations

from pathlib import Path


def test_src_claire_duplicate_tree_removed():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "src" / "claire").exists(), "src/claire duplicate package tree must remain removed"


def test_top_level_claire_package_still_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "claire").exists(), "top-level claire package must remain the active package"
