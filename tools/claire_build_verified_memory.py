from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_project_imports(project_root: Path) -> None:
    for candidate in (project_root, project_root / "src"):
        candidate_str = str(candidate)
        if candidate.exists() and candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Claire v17.61 verified memory and recursive feedback gate reports."
    )
    parser.add_argument("--project-root", default=".", help="Claire project root. Defaults to current directory.")
    parser.add_argument("--runtime-truth", default=None, help="Optional runtime truth JSON path.")
    parser.add_argument("--validation-report", default=None, help="Optional validation authority report path.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to exports/latest.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    _bootstrap_project_imports(project_root)

    try:
        from runtime_core.verified_memory.io import (
            find_runtime_truth,
            find_validation_report,
            load_json,
            write_json,
        )
        from runtime_core.verified_memory.memory_gate import build_memory_gate_report
        from runtime_core.verified_memory.recursive_feedback_gate import build_recursive_feedback_report
    except Exception as exc:
        print(f"[Claire v17.61] Import error: {exc}", file=sys.stderr)
        print("[Claire v17.61] Make sure you run this from the project root after installing v17.61.", file=sys.stderr)
        return 2

    runtime_path = Path(args.runtime_truth).resolve() if args.runtime_truth else find_runtime_truth(project_root)
    validation_path = Path(args.validation_report).resolve() if args.validation_report else find_validation_report(project_root)

    if runtime_path is None or not runtime_path.exists():
        print("[Claire v17.61] No runtime truth found.", file=sys.stderr)
        print("[Claire v17.61] Run Claire, then run tools/claire_build_runtime_truth.py.", file=sys.stderr)
        return 1

    if validation_path is None or not validation_path.exists():
        print("[Claire v17.61] No validation authority report found.", file=sys.stderr)
        print("[Claire v17.61] Run tools/claire_validate_runtime_truth.py before this command.", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).resolve() if args.out_dir else project_root / "exports" / "latest"
    frontend_dir = project_root / "src" / "frontend" / "command_center" / "modern"

    runtime_truth = load_json(runtime_path)
    validation_report = load_json(validation_path)

    memory_report = build_memory_gate_report(
        runtime_truth=runtime_truth,
        validation_report=validation_report,
        source_output_path=str(runtime_path),
    )
    recursive_report = build_recursive_feedback_report(memory_report)

    memory_report["runtime_truth_input_path"] = str(runtime_path)
    memory_report["validation_report_input_path"] = str(validation_path)
    recursive_report["memory_gate_input_path"] = str(out_dir / "verified_memory_gate_report.json")

    write_json(out_dir / "verified_memory_gate_report.json", memory_report)
    write_json(out_dir / "recursive_feedback_gate_report.json", recursive_report)

    if frontend_dir.exists():
        write_json(frontend_dir / "verified_memory_status.json", memory_report)
        write_json(frontend_dir / "recursive_feedback_status.json", recursive_report)

    print("[Claire v17.61] Verified memory gate report written:")
    print(f"  {out_dir / 'verified_memory_gate_report.json'}")
    print("[Claire v17.61] Recursive feedback gate report written:")
    print(f"  {out_dir / 'recursive_feedback_gate_report.json'}")
    print(f"[Claire v17.61] Memory: {memory_report.get('memory_status')} | Recursion: {recursive_report.get('feedback_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
