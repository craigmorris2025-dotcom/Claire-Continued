from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _bootstrap(project_root: Path) -> None:
    for candidate in (project_root, project_root / "src"):
        candidate_str = str(candidate)
        if candidate.exists() and candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Claire v17.62 local dashboard intelligence/search index.")
    parser.add_argument("--project-root", default=".", help="Claire project root. Defaults to current directory.")
    parser.add_argument("--out", default=None, help="Optional output path.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    _bootstrap(project_root)

    try:
        from runtime_core.dashboard_intelligence.local_index import build_dashboard_intelligence_index
    except Exception as exc:
        print(f"[Claire v17.62] Import error: {exc}", file=sys.stderr)
        return 2

    index = build_dashboard_intelligence_index(project_root)
    out_path = Path(args.out).resolve() if args.out else project_root / "src" / "frontend" / "command_center" / "modern" / "dashboard_search_index.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    latest = project_root / "exports" / "latest" / "dashboard_search_index.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("[Claire v17.62] Dashboard search/intelligence index written:")
    print(f"  {out_path}")
    print(f"  {latest}")
    print(f"[Claire v17.62] Indexed {index.get('documents_indexed')} of {index.get('documents_total')} known local truth files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
