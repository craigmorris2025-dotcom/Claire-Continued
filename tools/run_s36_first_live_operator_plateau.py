from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_live_probe"
PLATEAU_REPORT = RUNTIME_DIR / "s36_first_live_operator_plateau_report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_step(name: str, cmd: list[str]) -> dict:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    return {
        "name": name,
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-3000:],
        "stderr_tail": result.stderr[-3000:],
        "passed": result.returncode == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run exactly one S36 governed first-live HEAD metadata probe plateau."
    )
    parser.add_argument("--url", required=True)
    parser.add_argument("--operator-ack", required=True, choices=["YES"])
    args = parser.parse_args()

    steps = []
    steps.append(_run_step("preflight", [sys.executable, "tools/s36_first_live_preflight.py"]))

    if steps[-1]["passed"]:
        steps.append(_run_step(
            "single_head_probe",
            [
                sys.executable,
                "tools/run_s36_single_head_probe.py",
                "--url",
                args.url,
                "--operator-ack",
                "YES",
            ],
        ))

    if steps[-1]["passed"]:
        steps.append(_run_step("quarantine_verify", [sys.executable, "tools/verify_s36_probe_quarantine.py"]))

    if steps[-1]["passed"]:
        steps.append(_run_step("compile_first_probe_report", [sys.executable, "tools/compile_s36_first_probe_report.py"]))

    passed = all(step["passed"] for step in steps)

    report = {
        "version": "v19.89.8-S36R19-R22-first-live-operator-plateau",
        "completed_at": _utc_now(),
        "passed": passed,
        "url": args.url,
        "operator_ack": True,
        "one_shot_only": True,
        "steps": steps,
        "live_probe_count_requested": 1,
        "metadata_only": True,
        "body_reads_allowed": False,
        "browser_execution_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "automatic_updates_allowed": False,
        "continuous_crawling_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_applied": False,
    }

    PLATEAU_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PLATEAU_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if not passed:
        print("[S36-FIRST-LIVE-PLATEAU][FAILED]")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print("[S36-FIRST-LIVE-PLATEAU] PASS")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
