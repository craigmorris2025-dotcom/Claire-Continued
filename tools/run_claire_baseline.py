#!/usr/bin/env python
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if SRC.exists() and str(SRC) not in sys.path:
    sys.path.append(str(SRC))


class BaselineRunner:
    def __init__(self) -> None:
        self.manifest_path = (
            PROJECT_ROOT
            / "data"
            / "baselines"
            / "claire_baseline_manifest.json"
        )

        self.manifest = json.loads(
            self.manifest_path.read_text(encoding="utf-8")
        )

        self.results: List[Dict[str, Any]] = []

    def run(self) -> int:
        checks: List[tuple[str, Callable[[], Dict[str, Any]]]] = [
            ("imports", self.check_imports),
        ]

        for name, fn in checks:
            self.results.append(self._run_check(name, fn))

        summary = {
            "status": (
                "success"
                if all(
                    item["status"] == "success"
                    for item in self.results
                )
                else "failed"
            ),
            "baseline_version": self.manifest.get(
                "baseline_version",
                "unknown",
            ),
            "check_count": len(self.results),
            "passed_count": len(
                [
                    item
                    for item in self.results
                    if item["status"] == "success"
                ]
            ),
            "failed": [
                item
                for item in self.results
                if item["status"] != "success"
            ],
            "results": self.results,
        }

        print(json.dumps(summary, indent=2))

        return 0 if summary["status"] == "success" else 1

    def _run_check(
        self,
        name: str,
        fn: Callable[[], Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            payload = fn()

            return {
                "name": name,
                "status": "success",
                **payload,
            }

        except Exception as exc:
            return {
                "name": name,
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

    def check_imports(self) -> Dict[str, Any]:
        import claire.app  # noqa: F401
        import claire.orchestrator.pipeline_v4  # noqa: F401

        return {
            "message": "top-level claire imports succeeded",
        }


def main() -> int:
    return BaselineRunner().run()


if __name__ == "__main__":
    raise SystemExit(main())