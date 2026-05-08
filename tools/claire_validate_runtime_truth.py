from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_project_imports(project_root: Path) -> None:
    candidates = [
        project_root,
        project_root / "src",
    ]
    for candidate in candidates:
        candidate_str = str(candidate)
        if candidate.exists() and candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Claire v17.60 validation authority and evidence traceability reports."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Claire project root. Defaults to current directory.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional runtime truth JSON path. Defaults to exports/latest/dashboard_runtime_truth.json or latest available output.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to exports/latest.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    _bootstrap_project_imports(project_root)

    try:
        from claire.validation_authority.evidence_traceability import build_evidence_traceability_index
        from claire.validation_authority.io import find_latest_runtime_truth, load_json, write_json
        from claire.validation_authority.validation_authority import build_validation_report
    except Exception as exc:
        print(f"[Claire v17.60] Import error: {exc}", file=sys.stderr)
        print("[Claire v17.60] Make sure you run this from the project root after installing v17.60.", file=sys.stderr)
        return 2

    input_path = Path(args.input).resolve() if args.input else find_latest_runtime_truth(project_root)
    if input_path is None or not input_path.exists():
        print("[Claire v17.60] No runtime truth or core run output found.", file=sys.stderr)
        print("[Claire v17.60] Run Claire, then run tools/claire_build_runtime_truth.py, then rerun this command.", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).resolve() if args.out_dir else project_root / "exports" / "latest"
    frontend_dir = project_root / "src" / "frontend" / "command_center" / "modern"

    runtime_truth = load_json(input_path)
    report = build_validation_report(runtime_truth)
    evidence_index = build_evidence_traceability_index(runtime_truth)

    report["input_path"] = str(input_path)
    evidence_index["input_path"] = str(input_path)

    write_json(out_dir / "validation_authority_report.json", report)
    write_json(out_dir / "evidence_traceability_index.json", evidence_index)

    # Mirror small status files to the dashboard folder for local/static dashboard reads.
    if frontend_dir.exists():
        write_json(frontend_dir / "validation_authority_status.json", report)
        write_json(frontend_dir / "evidence_traceability_status.json", evidence_index)

    print("[Claire v17.60] Validation authority report written:")
    print(f"  {out_dir / 'validation_authority_report.json'}")
    print("[Claire v17.60] Evidence traceability index written:")
    print(f"  {out_dir / 'evidence_traceability_index.json'}")
    print(f"[Claire v17.60] Status: {report.get('validation_authority_status')} | Score: {report.get('validation_score')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
